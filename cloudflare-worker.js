/**
 * Cloudflare Worker - SCNet AI 代理
 * 免费部署步骤：
 * 1. 访问 https://workers.cloudflare.com/ 注册账户
 * 2. 创建新 Worker，粘贴此代码
 * 3. 保存并获取 Worker URL (如 https://your-worker.your-subdomain.workers.dev)
 * 4. 将 URL 填入 static/js/scnet-chat.js 的 PROXY_URLS 中
 */

// 配置
const SCNET_API = 'https://www.scnet.cn/api/chat/completions';

// CORS 头
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// 模拟响应
function generateSimulatedResponse(message) {
  const responses = [
    "你好！我是 SCNet AI 助手。这是一个模拟回复，因为目前无法连接到真实的 SCNet 服务。",
    "",
    "💡 获取真实 AI 回复的方法：",
    "1. **本地运行代理**: python scripts/scnet_proxy.py",
    "2. **部署 Cloudflare Worker**: 使用 cloudflare-worker.js",
    "3. **直接访问官网**: https://www.scnet.cn/ui/chatbot/",
    "",
    `你发送的消息是: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`
  ];
  return responses.join('\n');
}

export default {
  async fetch(request, env, ctx) {
    // 处理 CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 200, headers: corsHeaders });
    }

    // 只允许 POST
    if (request.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed', status: 'error' }),
        { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    try {
      const body = await request.json();
      const { message, model = 'qwen-turbo' } = body;

      if (!message) {
        return new Response(
          JSON.stringify({ error: 'Missing message', status: 'error' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      // 尝试调用 SCNet API
      try {
        const response = await fetch(SCNET_API, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://www.scnet.cn',
            'Referer': 'https://www.scnet.cn/ui/chatbot/',
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzMDMzMDQiLCJhdWQiOiJTR05ldCIsInN1YiI6IuW8oOWbvjU3MTU1NSIsImlzcyI6IlNHTmV0IiwiaWF0IjoxNzYxOTM2Njc0LCJuYmYiOjE3NjE5MzY2NzQsImV4cCI6MTc2MTk0MDI3NH0.iyPaE8Q5uQ9d0_zUftX73-ZxzBdN8JzVUMdydF6qXf8',
          },
          body: JSON.stringify({
            model: model,
            messages: [{ role: 'user', content: message }],
            stream: false,
            temperature: 0.7,
            max_tokens: 2000,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          const content = data.choices?.[0]?.message?.content || '无响应';
          
          return new Response(
            JSON.stringify({ response: content, status: 'ok', mode: 'real' }),
            { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
          );
        }
      } catch (apiError) {
        console.error('SCNet API error:', apiError);
      }

      // 如果 API 调用失败，返回模拟响应
      const simulatedResponse = generateSimulatedResponse(message);
      return new Response(
        JSON.stringify({ 
          response: simulatedResponse, 
          status: 'ok', 
          mode: 'simulation',
          note: '使用模拟响应，SCNet API 暂时不可用'
        }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );

    } catch (error) {
      return new Response(
        JSON.stringify({ error: error.message, status: 'error' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }
  },
};
