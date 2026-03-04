#!/usr/bin/env python3
"""
简易HTTP服务器，添加缓存头以优化页面性能
"""
import http.server
import socketserver

PORT = 8888

class CachingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 为静态资源添加缓存控制头
        if self.path.endswith(('.css', '.js', '.woff2', '.woff', '.ttf')):
            self.send_header('Cache-Control', 'public, max-age=31536000')  # 1年
        elif self.path.endswith(('.html', '.htm')):
            self.send_header('Cache-Control', 'public, max-age=3600')  # 1小时
        elif self.path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
            self.send_header('Cache-Control', 'public, max-age=86400')  # 1天
        
        # 启用GZIP预压缩检查
        self.send_header('Vary', 'Accept-Encoding')
        
        super().end_headers()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CachingHTTPRequestHandler) as httpd:
        print(f"🚀 性能优化版服务器运行在 http://localhost:{PORT}")
        print("📁 按 Ctrl+C 停止服务")
        httpd.serve_forever()
