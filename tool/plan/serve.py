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
import subprocess
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

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
        # /api/fetch-county/stream：以 SSE 方式实时流式运行 tool/county/fetch_county.py，逐行回传日志
        if self.path.startswith("/api/fetch-county/stream"):
            self.handle_fetch_county_stream()
            return
        # 其余路径交给静态文件处理器
        return super().do_GET()

    def handle_fetch_county_stream(self):
        """实时运行 fetch_county.py，把输出以 SSE 逐行推给前端。

        GET /api/fetch-county/stream[?debug=1]
          event: log   data: <一行日志>
          event: done  data: <退出码>
        """
        debug = ("debug=1" in self.path) or ("debug=true" in self.path)
        script = os.path.join(ROOT, "tool", "county", "fetch_county.py")
        cmd = [sys.executable, script]
        if debug:
            cmd.append("--debug")

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.flush()

        def send(ev, payload):
            try:
                self.wfile.write(
                    ("event: %s\ndata: %s\n\n" % (ev, payload)).encode("utf-8")
                )
                self.wfile.flush()
                return True
            except (BrokenPipeError, ConnectionResetError):
                return False

        if not os.path.exists(script):
            send("log", "未找到脚本: " + script)
            send("done", "-1")
            return

        try:
            # 关键：Windows 下子进程 stderr 接到管道时会用系统 ANSI 编码（cp936）写中文，
            # 而我们用 UTF-8 读管道，导致中文乱码。注入 PYTHONUTF8=1 强制子进程 I/O 用 UTF-8。
            child_env = dict(os.environ)
            child_env["PYTHONUTF8"] = "1"
            proc = subprocess.Popen(
                cmd,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并：logging 默认写 stderr
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                env=child_env,
            )
        except Exception as e:
            send("log", "启动失败: " + str(e))
            send("done", "-1")
            return

        for raw in proc.stdout:
            line = raw.rstrip("\n").rstrip("\r").replace("\n", " ").replace("\r", "")
            if not send("log", line):
                proc.terminate()
                return
        proc.wait()
        send("done", str(proc.returncode))

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
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("蜜月行程表服务器运行中： http://0.0.0.0:%d/tool/plan/plan_tool.html" % PORT)
    print("静态展示站：             http://0.0.0.0:%d/index.html" % PORT)
    print("本机 IP 查看： ipconfig（Windows） / ifconfig（Linux/macOS）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
