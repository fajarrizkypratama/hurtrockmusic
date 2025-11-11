import re
from pathlib import Path

# Lokasi file
project_root = Path(__file__).resolve().parent
config_file = project_root / "config.txt"
js_dir = project_root / "static" / "js"
files = [js_dir / "floating-chat.js", js_dir / "admin-chat.js"]

# Baca config.txt
config = {}
with open(config_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

CHAT_DOMAIN = config.get("CHAT_DOMAIN", "localhost:8000")
KASIR_DOMAIN = config.get("KASIR_DOMAIN", "localhost:5000")
MAIN_DOMAIN = config.get("MAIN_DOMAIN", "localhost:5001")

def patch_file(filepath: Path):
    text = filepath.read_text(encoding="utf-8")

    header = (
        "// === Domain Config injected from config.txt ===\n"
        f"const CHAT_DOMAIN = '{CHAT_DOMAIN}';\n"
        f"const KASIR_DOMAIN = '{KASIR_DOMAIN}';\n"
        f"const MAIN_DOMAIN  = '{MAIN_DOMAIN}';\n"
        "// =================================================\n\n"
    )

    # Tambah header di atas jika belum ada
    if "const CHAT_DOMAIN" not in text:
        text = header + text

    # Patch fetch('/api/chat/token')
    text = re.sub(
        r"fetch\((['\"])/api/chat/token",
        "fetch((window.location.hostname === KASIR_DOMAIN || window.location.hostname === MAIN_DOMAIN) ? `https://${CHAT_DOMAIN}/api/chat/token` : '/api/chat/token'",
        text,
    )

    # Patch WebSocket host → gunakan CHAT_DOMAIN
    text = re.sub(
        r"(\$\{wsProtocol}//)(\$\{currentHost}|window.location.hostname)(/.*?/ws/chat/)",
        r"\1${CHAT_DOMAIN}\3",
        text,
    )

    outpath = filepath.with_name("patched_" + filepath.name)
    outpath.write_text(text, encoding="utf-8")
    print("Patched:", filepath, "->", outpath)

if __name__ == "__main__":
    for f in files:
        if f.exists():
            patch_file(f)
        else:
            print("File", f, "not found, skipped.")
