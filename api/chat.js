/**
 * Vercel Edge Function - SCNet AI 代理
 * 解决浏览器 CORS 限制
 * 
 * 部署说明:
 * 1. 安装 Vercel CLI: npm i -g vercel
 * 2. 运行: vercel --prod
 */

export const config = {
  runtime: 'edge',
};

const SCNET_API = 'https://www.scnet.cn/api/chat/completions';

export default async function handler(request) {
  // CORS 头
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  // 处理预检请求
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  // 只允许 POST
  if (request.method !== 'POST') {
    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  try {
    const body = await request.json();
    const { message, model = 'qwen-turbo' } = body;

    if (!message) {
      return new Response(
        JSON.stringify({ error: 'Missing message' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 调用 SCNet API
    const response = await fetch(SCNET_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Origin': 'https://www.scnet.cn',
        'Referer': 'https://www.scnet.cn/ui/chatbot/',
        // 注意：这里的 token 需要定期更新
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

    if (!response.ok) {
      // 如果 SCNet 返回错误，提供模拟响应
      const simulated = generateSimulatedResponse(message);
      return new Response(
        JSON.stringify({ 
          response: simulated,
          status: 'ok',
          mode: 'simulation',
          note: 'SCNet API unavailable, using simulated response'
        }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || '无响应';

    return new Response(
      JSON.stringify({ response: content, status: 'ok' }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Edge Function Error:', error);
    return new Response(
      JSON.stringify({ 
        error: error.message,
        response: '服务暂时不可用，请稍后重试',
        status: 'error'
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
}

function generateSimulatedResponse(message) {
  const msg = message.toLowerCase();
  
  if (msg.includes('你好') || msg.includes('hello')) {
    return "你好！我是 SCNet AI 助手（模拟模式），很高兴为你服务。";
  }
  if (msg.includes('代码') || msg.includes('code') || msg.includes('python')) {
    return "我可以帮你编写代码。不过当前处于模拟模式，无法执行真实请求。\n\n提示：部署到 Vercel 后可使用真实 API。";
  }
  
  return `收到消息："${message.substring(0, 50)}..."\n\n当前处于模拟模式。要获取真实 AI 回复，请：\n1. 本地运行：python scripts/scnet_proxy.py\n2. 或部署到 Vercel 使用 Edge Function`;
}
