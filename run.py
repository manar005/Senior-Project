#!/usr/bin/env python3
"""Development entrypoint: initializes the DB then starts the Flask server."""
from thaghrah import create_app
from thaghrah.database import init_db


def main():
    init_db()
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5001)


if __name__ == "__main__":
    main()
