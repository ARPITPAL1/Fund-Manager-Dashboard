#!/usr/bin/env python
"""
FinTrend Analytics & AI Command Center Runner
Launches the Django ASGI backend (HTTP + WebSockets) & Pure HTML5/CSS Frontend on Port 8000.
"""

import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DJANGO_DIR = ROOT_DIR / "backend_django"

def main():
    print("=" * 65)
    print("🚀 Booting FinTrend Mutual Fund Analytics Command Center")
    print("⚡ Python 3.14 + Django 6.1 + SQL + AI/ML + Vector RAG + Pure HTML/CSS")
    print("=" * 65)

    print("\n[1/3] Running database migrations...")
    subprocess.run([sys.executable, "manage.py", "migrate"], cwd=DJANGO_DIR)

    print("\n[2/3] Verifying database seeding & ML models...")
    subprocess.run([sys.executable, "manage.py", "seed_data"], cwd=DJANGO_DIR)

    print("\n[3/3] Launching web server at: http://127.0.0.1:8000/")
    print("=" * 65)
    print("🌐 Open http://127.0.0.1:8000/ in your browser")
    print("=" * 65 + "\n")

    subprocess.run([sys.executable, "manage.py", "runserver", "8000"], cwd=DJANGO_DIR)

if __name__ == '__main__':
    main()
