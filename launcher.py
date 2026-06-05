import os
import webbrowser

webbrowser.open = lambda *a, **kw: None
webbrowser.open_new = lambda *a, **kw: None
webbrowser.open_new_tab = lambda *a, **kw: None

os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import signal as _signal_module
_orig_signal = _signal_module.signal
def _safe_signal(signum, handler):
    try:
        return _orig_signal(signum, handler)
    except (ValueError, OSError):
        pass
_signal_module.signal = _safe_signal

import sys
import threading
import time


def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def run_streamlit(port: int) -> None:
    from streamlit.web.bootstrap import run
    run(resource_path("app.py"), "", [], {
        "server.port": port,
        "server.headless": True,
        "browser.gatherUsageStats": False,
        "server.enableCORS": False,
        "server.enableXsrfProtection": False,
    })


def wait_for_server(port: int, timeout: int = 30) -> bool:
    import urllib.request
    import urllib.error
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1)
            return True
        except Exception:
            time.sleep(0.3)
    return False


if __name__ == "__main__":
    PORT = 8501

    threading.Thread(target=run_streamlit, args=(PORT,), daemon=True).start()

    if not wait_for_server(PORT):
        import tkinter.messagebox as mb
        mb.showerror("Erro", "O servidor não iniciou. Tente abrir novamente.")
        sys.exit(1)

    import webview
    webview.create_window(
        "Cotação de Moedas",
        f"http://127.0.0.1:{PORT}",
        width=1400,
        height=900,
        min_size=(900, 650),
    )
    webview.start()
