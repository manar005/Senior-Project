"""Paths, environment loading, and runtime settings."""
import os

PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(PKG_ROOT)

_env_path = os.path.join(APP_ROOT, ".env")


def _load_env_file(path):
    """Set os.environ from KEY=value lines (no extra dependency). utf-8-sig strips BOM."""
    try:
        with open(path, "r", encoding="utf-8-sig") as envf:
            for raw in envf:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip()
                if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                    val = val[1:-1]
                if key:
                    os.environ[key] = val
    except OSError:
        pass


def load_environment():
    """Call once at process start (before other thaghrah imports that read env)."""
    try:
        from dotenv import load_dotenv

        load_dotenv(_env_path)
    except ImportError:
        pass
    _load_env_file(_env_path)


load_environment()

DATABASE = os.path.join(APP_ROOT, "thaghrah.db")
STATIC_DIR = os.path.join(APP_ROOT, "static")
PCAPS_DIR = os.path.join(STATIC_DIR, "pcaps")
LOGS_DIR = os.path.join(APP_ROOT, "logs")
APP_LOG_PATH = os.path.join(LOGS_DIR, "app.log")
