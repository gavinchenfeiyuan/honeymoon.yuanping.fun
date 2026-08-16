#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蜜月行程表 - 局域网服务器
同时提供静态文件服务 + /api/save 写文件接口（供 iPhone/iPad 保存 JSON）

用法：
    python serve.py            # 默认端口 8080，监听 0.0.0.0
    python serve.py 9000       # 指定端口

局域网设备访问：http://<本机IP>:8080/plan_tool.html
"""
import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

ALLOWED_FILES = {"path.json", "place.json"}   # 只允许保存这两个文件（白名单）
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

# 服务根目录 = 项目根（serve.py 位于 项目根/tool/plan/，向上 3 级）
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        # /api/amap-key：返回高德 Web 服务 Key（从根目录 amap_key.txt 读取，避免 key 入库/硬编码）
        if self.path == "/api/amap-key":
            key_path = os.path.join(ROOT, "amap_key.txt")
            if not os.path.exists(key_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(json.dumps({"key": ""}).encode("utf-8"))
                return
            with open(key_path, "r", encoding="utf-8") as f:
                key = f.read().strip()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps({"key": key}).encode("utf-8"))
            return
        # 其余路径交给静态文件处理器
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/save":
            self.send_error(404, "not found")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            fname = data.get("file", "")
            content = data.get("content", "")
            if fname not in ALLOWED_FILES:
                self.send_error(400, "file not allowed: %s" % fname)
                return
            with open(os.path.join(ROOT, fname), "w", encoding="utf-8", newline="") as f:
                f.write(content)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "file": fname}).encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    # 服务根目录 = 项目根（ROOT），使：
    #   http://<IP>:PORT/tool/plan/plan_tool.html  可加载根目录 path.json（../../path.json）
    #   http://<IP>:PORT/index.html                可访问静态展示站
    #   /api/save 写回根目录 path.json / place.json
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print("蜜月行程表服务器运行中： http://0.0.0.0:%d/tool/plan/plan_tool.html" % PORT)
    print("静态展示站：             http://0.0.0.0:%d/index.html" % PORT)
    print("本机 IP 查看： ipconfig（Windows） / ifconfig（Linux/macOS）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
