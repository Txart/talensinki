# talensinki/gui.py
import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit GUI application."""
    server_port = 8001
    app_path = Path(__file__).parent / "streamlit_app.py"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(server_port),
        ]
    )


if __name__ == "__main__":
    main()
