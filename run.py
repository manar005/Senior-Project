#!/usr/bin/env python3
from thaghrah import create_app
from thaghrah.db import init_db


def main():
    init_db()
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5001)


if __name__ == "__main__":
    main()
