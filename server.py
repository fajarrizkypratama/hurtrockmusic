#!/usr/bin/env python3
"""
Hurtrock Music Store - Universal Server Launcher
Menjalankan Flask (main.py) dan Django chat service (Daphne) bersamaan
"""

import os
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path
import socket
import logging
from dotenv import load_dotenv

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- Load environment ---
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)

# Ambil port dari .env, bersihkan comment jika ada
def parse_port(env_var, default):
    val = os.getenv(env_var, str(default)).split()[0]
    return int(val)

FLASK_PORT = parse_port('MAIN_PORT', 5000)
DJANGO_PORT = parse_port('DJANGO_PORT', 8000)
SESSION_SECRET = os.getenv('SESSION_SECRET', 'default_secret')

# --- Helper functions ---
def check_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('127.0.0.1', port)) == 0

def wait_for_port(port, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        if check_port_in_use(port):
            return True
        time.sleep(0.5)
    return False

# --- Server class ---
class HurtrockServer:
    def __init__(self):
        self.flask_thread = None
        self.django_process = None
        self.running = False
        self.project_root = BASE_DIR
        self.setup_env()

    def setup_env(self):
        os.environ.setdefault('PYTHONPATH', str(self.project_root))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
        os.environ.setdefault('FLASK_ENV', 'production')
        os.environ.setdefault('FLASK_DEBUG', '0')
        os.environ.setdefault('SESSION_SECRET', SESSION_SECRET)

    # --- Django chat service ---
    def start_django(self):
        chat_dir = self.project_root / 'chat_service'
        if not chat_dir.exists():
            logger.warning("Chat service directory not found, skipping Django")
            return
        if check_port_in_use(DJANGO_PORT):
            logger.warning(f"Port {DJANGO_PORT} in use, skipping Django start")
            return

        env = os.environ.copy()
        self.django_process = subprocess.Popen(
            [sys.executable, '-m', 'daphne', '-b', '0.0.0.0', '-p', str(DJANGO_PORT),
             'chat_microservice.asgi:application'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        if wait_for_port(DJANGO_PORT, timeout=30):
            logger.info(f"Django chat service started on port {DJANGO_PORT}")
        else:
            logger.warning("Django failed to start within timeout")

    # --- Flask main store ---
    def start_flask(self):
        if check_port_in_use(FLASK_PORT):
            logger.warning(f"Port {FLASK_PORT} in use, Flask may fail to start")
            return

        def run_flask():
            try:
                # Import app dari main.py
                from main import app
                app.run(host='0.0.0.0', port=FLASK_PORT, debug=False,
                        use_reloader=False, threaded=True)
            except Exception as e:
                logger.error(f"Flask error: {e}")

        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()
        if wait_for_port(FLASK_PORT, timeout=30):
            logger.info(f"Flask started on port {FLASK_PORT}")
        else:
            logger.error("Flask failed to start")

    # --- Stop services ---
    def stop(self):
        self.running = False
        if self.django_process and self.django_process.poll() is None:
            logger.info("Stopping Django chat service...")
            self.django_process.terminate()
            try:
                self.django_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.django_process.kill()
        logger.info("All services stopped.")

    # --- Start everything ---
    def start(self):
        signal.signal(signal.SIGINT, lambda s, f: self.stop())
        signal.signal(signal.SIGTERM, lambda s, f: self.stop())
        self.running = True
        logger.info("Starting Hurtrock Music Store services...")
        self.start_django()
        self.start_flask()

        while self.running:
            time.sleep(1)

# --- Main ---
def main():
    server = HurtrockServer()
    server.start()

if __name__ == '__main__':
    main()
