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


class Handler(SimpleHTTPRequestHandler):
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
            with open(fname, "w", encoding="utf-8", newline="") as f:
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
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print("蜜月行程表服务器运行中： http://0.0.0.0:%d/plan_tool.html" % PORT)
    print("本机 IP 查看： ipconfig（Windows） / ifconfig（Linux/macOS）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
