"""
Bholu AI — Project Launcher

Usage:
    python run.py part1    → Launch the vulnerable Bholu agent demo
    python run.py part2    → Launch the secure dual-agent demo
    python run.py both     → Launch both (on different ports)
"""

import sys
import subprocess
import os


def launch(part: str):
    if part == "part1":
        print("🤖 Launching Part 1 — Bholu AI (Vulnerable Agent)...")
        print("   URL: http://localhost:8501")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            os.path.join("part1_vulnerable", "app.py"),
            "--server.port", "8501",
            "--server.headless", "false"
        ])

    elif part == "part2":
        print("🛡️ Launching Part 2 — Secure Dual-Agent Framework...")
        print("   URL: http://localhost:8502")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            os.path.join("part2_secure", "app.py"),
            "--server.port", "8502",
            "--server.headless", "false"
        ])

    elif part == "both":
        import threading
        print("🚀 Launching both parts...")
        print("   Part 1 (Vulnerable): http://localhost:8501")
        print("   Part 2 (Secure):     http://localhost:8502")

        def run_part1():
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                os.path.join("part1_vulnerable", "app.py"),
                "--server.port", "8501",
                "--server.headless", "true"
            ])

        def run_part2():
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                os.path.join("part2_secure", "app.py"),
                "--server.port", "8502",
                "--server.headless", "true"
            ])

        t1 = threading.Thread(target=run_part1)
        t2 = threading.Thread(target=run_part2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    else:
        print("Usage: python run.py [part1|part2|both]")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py [part1|part2|both]")
        sys.exit(1)
    launch(sys.argv[1])
