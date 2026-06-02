"""
Servidor local para o site de Cotação de Moedas.
- Serve arquivos estáticos do diretório atual
- Faz proxy de /api/* → https://api.frankfurter.app/*
- Multi-threaded (ThreadingHTTPServer)
- Reinicia automaticamente em caso de erro
"""

import http.server
import urllib.request
import urllib.error
import threading
import os
import sys
import time
import logging

PORT = 8080
ROOT = os.path.dirname(os.path.abspath(__file__))
FRANKFURTER = "https://api.frankfurter.app"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy()
        elif self.path == "/":
            self.path = "/moedas.html"
            super().do_GET()
        else:
            super().do_GET()

    def _proxy(self):
        api_path = self.path[len("/api"):]          # /latest?from=USD
        url = FRANKFURTER + api_path
        log.info("PROXY  %s", url)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cotacao-moedas/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as e:
            log.error("HTTP %s from Frankfurter: %s", e.code, url)
            self._error(502, f"Frankfurter returned {e.code}")
        except Exception as e:
            log.error("Proxy error: %s", e)
            self._error(502, str(e))

    def _error(self, code, msg):
        body = f'{{"error":"{msg}"}}'.encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        status = args[1] if len(args) > 1 else "?"
        log.info("%-6s %s", status, args[0] if args else "")


def serve():
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        log.info("Servidor rodando em http://localhost:%d/", PORT)
        log.info("Pressione Ctrl+C para parar.")
        httpd.serve_forever()


if __name__ == "__main__":
    while True:
        try:
            serve()
        except KeyboardInterrupt:
            log.info("Servidor encerrado.")
            sys.exit(0)
        except OSError as e:
            log.error("Erro ao iniciar servidor: %s", e)
            log.info("Tentando novamente em 5 segundos...")
            time.sleep(5)
