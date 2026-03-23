/**
 * Cloudflare Worker - 访问者地理位置收集与 API
 * 
 * 部署步骤：
 * 1. 登录 https://dash.cloudflare.com
 * 2. 进入 Workers & Pages > Create application > Create Worker
 * 3. 粘贴以下代码
 * 4. 绑定 KV Namespace（变量名设为 VISITOR_DATA）
 * 5. 部署并复制 Worker URL
 */

// CORS 配置 - 修改为你的域名
const ALLOWED_ORIGINS = [
  'https://yangbc2015.github.io',
  'http://localhost:1313',  // Hugo 开发服务器
  'http://127.0.0.1:1313',
];

// 简单的 IP 地理位置缓存（内存中）
const geoCache = new Map();
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24小时

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';
    
    // 检查 CORS
    const allowedOrigin = ALLOWED_ORIGINS.find(o => origin.includes(o)) || ALLOWED_ORIGINS[0];
    
    // 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': allowedOrigin,
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    try {
      // API 路由
      if (url.pathname === '/api/track') {
        return await handleTrack(request, env, allowedOrigin);
      } else if (url.pathname === '/api/heatmap') {
        return await handleHeatmap(request, env, allowedOrigin);
      } else if (url.pathname === '/api/stats') {
        return await handleStats(request, env, allowedOrigin);
      }

      return jsonResponse({ error: 'Not found' }, 404, allowedOrigin);
    } catch (error) {
      console.error('Worker error:', error);
      return jsonResponse({ error: 'Internal server error' }, 500, allowedOrigin);
    }
  },
};

/**
 * 记录访问者位置
 */
async function handleTrack(request, env, allowedOrigin) {
  if (request.method !== 'POST') {
    return jsonResponse({ error: 'Method not allowed' }, 405, allowedOrigin);
  }

  // 获取访问者 IP
  const clientIP = request.headers.get('CF-Connecting-IP') || 
                   request.headers.get('X-Forwarded-For')?.split(',')[0] || 
                   'unknown';
  
  // 排除爬虫和本地 IP
  if (isBotOrLocal(clientIP)) {
    return jsonResponse({ success: true, cached: true }, 200, allowedOrigin);
  }

  // 生成 IP 的哈希（保护隐私）
  const ipHash = await hashIP(clientIP);
  
  // 检查是否已经记录过（同一天）
  const today = new Date().toISOString().split('T')[0];
  const cacheKey = `${ipHash}_${today}`;
  
  const existing = await env.VISITOR_DATA?.get(cacheKey);
  if (existing) {
    return jsonResponse({ success: true, cached: true }, 200, allowedOrigin);
  }

  // 获取地理位置
  const geoData = await getGeoLocation(clientIP);
  if (!geoData || geoData.status === 'fail') {
    return jsonResponse({ success: false, error: 'Geo lookup failed' }, 200, allowedOrigin);
  }

  // 存储访问记录
  const record = {
    ipHash,
    lat: geoData.lat,
    lon: geoData.lon,
    city: geoData.city,
    country: geoData.country,
    countryCode: geoData.countryCode,
    region: geoData.regionName,
    timestamp: Date.now(),
    date: today,
  };

  // 保存到 KV（设置 7 天过期）
  await env.VISITOR_DATA?.put(cacheKey, JSON.stringify(record), {
    expirationTtl: 7 * 24 * 60 * 60, // 7天
  });

  // 同时添加到热力图数据列表
  const heatmapKey = `heatmap_${today}`;
  const existingHeatmap = await env.VISITOR_DATA?.get(heatmapKey);
    const heatmapData = existingHeatmap ? JSON.parse(existingHeatmap) : [];
  heatmapData.push([geoData.lat, geoData.lon, 1]); // [lat, lng, intensity]
  
  await env.VISITOR_DATA?.put(heatmapKey, JSON.stringify(heatmapData), {
    expirationTtl: 30 * 24 * 60 * 60, // 30天
  });

  return jsonResponse({ success: true, location: geoData.city }, 200, allowedOrigin);
}

/**
 * 获取热力图数据
 */
async function handleHeatmap(request, env, allowedOrigin) {
  const url = new URL(request.url);
  const days = parseInt(url.searchParams.get('days')) || 7;
  
  const heatmapData = [];
  const uniqueLocations = new Map();
  
  // 收集最近 N 天的数据
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    const data = await env.VISITOR_DATA?.get(`heatmap_${dateStr}`);
    if (data) {
      const points = JSON.parse(data);
      points.forEach(point => {
        const key = `${point[0].toFixed(2)},${point[1].toFixed(2)}`;
        if (uniqueLocations.has(key)) {
          uniqueLocations.get(key)[2] += 1; // 增加强度
        } else {
          const newPoint = [...point];
          uniqueLocations.set(key, newPoint);
          heatmapData.push(newPoint);
        }
      });
    }
  }

  // 获取统计信息
  const stats = await getVisitorStats(env);

  return jsonResponse({
    points: heatmapData,
    total: heatmapData.reduce((sum, p) => sum + p[2], 0),
    uniqueLocations: heatmapData.length,
    stats,
  }, 200, allowedOrigin);
}

/**
 * 获取访问统计
 */
async function handleStats(request, env, allowedOrigin) {
  const stats = await getVisitorStats(env);
  return jsonResponse(stats, 200, allowedOrigin);
}

/**
 * 获取访问者统计信息
 */
async function getVisitorStats(env) {
  const today = new Date().toISOString().split('T')[0];
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
  
  // 获取今日和昨日数据
  const todayData = await env.VISITOR_DATA?.get(`heatmap_${today}`);
  const yesterdayData = await env.VISITOR_DATA?.get(`heatmap_${yesterday}`);
  
  // 获取最近 7 天和 30 天的汇总
  let weekTotal = 0;
  let monthTotal = 0;
  const countryMap = new Map();
  
  for (let i = 0; i < 30; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    const data = await env.VISITOR_DATA?.get(`heatmap_${dateStr}`);
    if (data) {
      const points = JSON.parse(data);
      const count = points.length;
      monthTotal += count;
      if (i < 7) weekTotal += count;
    }
  }

  return {
    today: todayData ? JSON.parse(todayData).length : 0,
    yesterday: yesterdayData ? JSON.parse(yesterdayData).length : 0,
    week: weekTotal,
    month: monthTotal,
  };
}

/**
 * 获取 IP 地理位置
 */
async function getGeoLocation(ip) {
  // 检查缓存
  if (geoCache.has(ip)) {
    const cached = geoCache.get(ip);
    if (Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.data;
    }
  }

  try {
    // 使用 ip-api.com（免费，非商业用途）
    // 注意：生产环境建议使用付费服务如 MaxMind 或 IP2Location
    const response = await fetch(`http://ip-api.com/json/${ip}?fields=status,message,country,countryCode,region,regionName,city,lat,lon,timezone`);
    const data = await response.json();
    
    // 缓存结果
    geoCache.set(ip, { data, timestamp: Date.now() });
    
    return data;
  } catch (error) {
    console.error('Geo lookup error:', error);
    return null;
  }
}

/**
 * 检查是否为爬虫或本地 IP
 */
function isBotOrLocal(ip) {
  const localRanges = [
    '127.',
    '10.',
    '172.16.',
    '172.17.',
    '172.18.',
    '172.19.',
    '172.20.',
    '172.21.',
    '172.22.',
    '172.23.',
    '172.24.',
    '172.25.',
    '172.26.',
    '172.27.',
    '172.28.',
    '172.29.',
    '172.30.',
    '172.31.',
    '192.168.',
    '::1',
    'fc00:',
    'fe80:',
  ];
  
  if (ip === 'unknown' || !ip) return true;
  if (localRanges.some(range => ip.startsWith(range))) return true;
  
  return false;
}

/**
 * 对 IP 进行哈希（保护隐私）
 */
async function hashIP(ip) {
  const encoder = new TextEncoder();
  const data = encoder.encode(ip + 'salt_key_change_this');
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
}

/**
 * JSON 响应辅助函数
 */
function jsonResponse(data, status = 200, allowedOrigin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': allowedOrigin,
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Cache-Control': 'no-cache',
    },
  });
}
