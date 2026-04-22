#!/usr/bin/env python3
"""Starts a local HTTP server and opens the RAG viewer in the browser."""

import http.server
import socketserver
import threading
import webbrowser
import os
from pathlib import Path

PORT = 7842
ROOT = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        pass  # suppress request logs

def main():
    os.chdir(ROOT)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/viewer/index.html"
        print(f"RAG Viewer → {url}")
        print("Ctrl+C to stop\n")
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
