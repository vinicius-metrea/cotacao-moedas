import os
import sys
import time
import subprocess


def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


PORT = 8501

# ── Server mode: called by the subprocess spawned below ──────────────────────

if "--streamlit-server" in sys.argv:
    import webbrowser
    webbrowser.open = lambda *a, **kw: None
    webbrowser.open_new = lambda *a, **kw: None
    webbrowser.open_new_tab = lambda *a, **kw: None

    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    from streamlit.web.bootstrap import run
    run(resource_path("app.py"), "", [], {
        "server.port": PORT,
        "server.headless": True,
        "browser.gatherUsageStats": False,
        "server.enableCORS": False,
        "server.enableXsrfProtection": False,
    })
    sys.exit(0)


# ── Main mode: spawn server subprocess, wait, open webview ───────────────────

def wait_for_server(timeout: int = 30) -> bool:
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/_stcore/health", timeout=1)
            return True
        except Exception:
            time.sleep(0.3)
    return False


if __name__ == "__main__":
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    server = subprocess.Popen(
        [sys.executable, "--streamlit-server"],
        creationflags=flags,
    )

    if not wait_for_server():
        server.terminate()
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

    server.terminate()
