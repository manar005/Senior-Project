"""
Compatibility shim for tools that expect `app` in this module (e.g. FLASK_APP=app).

Preferred: `python run.py` from the project root.
"""
from thaghrah import create_app
from thaghrah.database import init_db

app = create_app()

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5001)
