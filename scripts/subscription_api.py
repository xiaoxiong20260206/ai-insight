#!/usr/bin/env python3
"""
AI洞察订阅API服务
==================
简单的HTTP API服务，处理前端订阅请求

启动: python scripts/subscription_api.py
访问: http://localhost:8765/
"""

import asyncio
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from subscription_manager import SubscriptionManager

# CORS 允许的源
ALLOWED_ORIGINS = [
    "https://xiaoxiong20260206.github.io",
    "http://localhost",
    "http://127.0.0.1",
]


class SubscriptionHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {args[0]}")

    def _set_cors_headers(self):
        """设置CORS头"""
        origin = self.headers.get('Origin', '')
        if any(origin.startswith(allowed) for allowed in ALLOWED_ORIGINS):
            self.send_header('Access-Control-Allow-Origin', origin)
        else:
            self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')

    def _send_json_response(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # 健康检查
        if path == '/health':
            self._send_json_response({'status': 'ok', 'service': 'INTERNAL_PROJECT_ID'})
            return

        # 查询订阅状态
        if path == '/status':
            username = params.get('username', [''])[0].strip().lower()
            if not username:
                self._send_json_response({'error': '缺少用户名参数'}, 400)
                return

            try:
                manager = SubscriptionManager()
                result = asyncio.run(self._check_subscription(manager, username))
                self._send_json_response(result)
            except Exception as e:
                self._send_json_response({'error': str(e)}, 500)
            return

        # 未知路径
        self._send_json_response({'error': 'Not Found'}, 404)

    def do_POST(self):
        """处理POST请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self._send_json_response({'error': '无效的JSON数据'}, 400)
            return

        # 订阅
        if path == '/subscribe':
            username = data.get('username', '').strip().lower()
            if not username:
                self._send_json_response({'error': '缺少用户名参数'}, 400)
                return

            try:
                manager = SubscriptionManager()
                success = asyncio.run(self._subscribe(manager, username))
                if success:
                    self._send_json_response({
                        'success': True,
                        'message': '订阅成功',
                        'username': username
                    })
                else:
                    self._send_json_response({'error': '订阅失败'}, 500)
            except Exception as e:
                self._send_json_response({'error': str(e)}, 500)
            return

        # 取消订阅
        if path == '/unsubscribe':
            username = data.get('username', '').strip().lower()
            if not username:
                self._send_json_response({'error': '缺少用户名参数'}, 400)
                return

            try:
                manager = SubscriptionManager()
                success = asyncio.run(self._unsubscribe(manager, username))
                if success:
                    self._send_json_response({
                        'success': True,
                        'message': '取消订阅成功',
                        'username': username
                    })
                else:
                    self._send_json_response({'error': '取消订阅失败'}, 500)
            except Exception as e:
                self._send_json_response({'error': str(e)}, 500)
            return

        # 未知路径
        self._send_json_response({'error': 'Not Found'}, 404)

    async def _check_subscription(self, manager: SubscriptionManager, username: str):
        """检查订阅状态"""
        subscribers = await manager.list_subscribers(active_only=False)
        for sub in subscribers:
            if sub.get('username', '').lower() == username:
                return {
                    'exists': True,
                    'is_active': sub.get('is_active', False),
                    'subscribed_at': sub.get('subscribed_at'),
                    'username': sub.get('username')
                }
        return {'exists': False}

    async def _subscribe(self, manager: SubscriptionManager, username: str) -> bool:
        """订阅"""
        return await manager.add_subscriber(username)

    async def _unsubscribe(self, manager: SubscriptionManager, username: str) -> bool:
        """取消订阅"""
        return await manager.remove_subscriber(username)


def run_server(port=8765):
    """启动服务器"""
    server = HTTPServer(('localhost', port), SubscriptionHandler)
    print(f"🚀 订阅API服务已启动: http://localhost:{port}")
    print(f"   健康检查: http://localhost:{port}/health")
    print(f"   订阅状态: http://localhost:{port}/status?username=xxx")
    print(f"\n按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port)
