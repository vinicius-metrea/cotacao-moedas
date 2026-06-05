import os
import sys
import time
import subprocess


def exe_dir() -> str:
    return os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))


def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


PORT = 8501

# ── Server mode ───────────────────────────────────────────────────────────────

if "--streamlit-server" in sys.argv:
    # Change to exe directory so Streamlit picks up .streamlit/config.toml
    os.chdir(exe_dir())

    import webbrowser
    webbrowser.open = lambda *a, **kw: None
    webbrowser.open_new = lambda *a, **kw: None
    webbrowser.open_new_tab = lambda *a, **kw: None

    from streamlit.web.bootstrap import run
    run(resource_path("app.py"), "", [], {
        "server.port": PORT,
        "server.headless": True,
    })
    sys.exit(0)


# ── Main mode ─────────────────────────────────────────────────────────────────

def ensure_streamlit_config() -> None:
    """Write .streamlit/config.toml next to the exe if it doesn't exist."""
    config_dir = os.path.join(exe_dir(), ".streamlit")
    config_path = os.path.join(config_dir, "config.toml")
    os.makedirs(config_dir, exist_ok=True)
    with open(config_path, "w") as f:
        f.write(
            "[global]\n"
            "developmentMode = false\n\n"
            "[server]\n"
            "headless = true\n"
            "enableCORS = true\n"
            "enableXsrfProtection = false\n\n"
            "[browser]\n"
            "gatherUsageStats = false\n"
        )


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
    ensure_streamlit_config()

    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    server = subprocess.Popen(
        [sys.executable, "--streamlit-server"],
        cwd=exe_dir(),
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
