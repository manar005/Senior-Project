"""Thaghrah Flask application factory."""
import logging
import os
import secrets
import time

from flask import Flask, g, request, session
from logging.handlers import RotatingFileHandler

from thaghrah.config import APP_LOG_PATH, APP_ROOT, LOGS_DIR


def _setup_app_logging(app):
    os.makedirs(LOGS_DIR, exist_ok=True)
    abs_log_path = os.path.abspath(APP_LOG_PATH)
    for h in logging.getLogger().handlers:
        if isinstance(h, RotatingFileHandler) and os.path.abspath(getattr(h, "baseFilename", "")) == abs_log_path:
            return
    file_handler = RotatingFileHandler(APP_LOG_PATH, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Logging initialized at %s", APP_LOG_PATH)


def _register_request_timing(app):
    @app.before_request
    def _request_timer_start():
        g._request_start = time.perf_counter()

    @app.after_request
    def _request_timer_log(response):
        started = getattr(g, "_request_start", None)
        if started is None:
            return response
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        should_log = (
            request.path in ("/submit_flag", "/challenges/ai/submit-flag")
            or request.path.startswith("/challenges/ai")
            or elapsed_ms >= 1200
        )
        if should_log:
            app.logger.info(
                "REQ method=%s path=%s status=%s elapsed_ms=%.2f user_id=%s",
                request.method,
                request.path,
                response.status_code,
                elapsed_ms,
                session.get("user_id"),
            )
        return response


def create_app():
    """Application factory: call once per process (e.g. from run.py or WSGI)."""
    app = Flask(
        __name__,
        template_folder=os.path.join(APP_ROOT, "templates"),
        static_folder=os.path.join(APP_ROOT, "static"),
    )
    app.secret_key = secrets.token_hex(16)

    _setup_app_logging(app)
    _register_request_timing(app)

    from thaghrah.routes import ai_lab, auth, network, pages

    auth.register_routes(app)
    pages.register_routes(app)
    network.register_routes(app)
    ai_lab.register_routes(app)

    return app
