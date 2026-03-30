"""
auto_push.py — Watch the dashboard project and auto-commit + push to GitHub
on any file change.

Usage:
    python tools/auto_push.py

Requirements:
    pip install watchdog

GitHub token must be set in env/.env as:
    GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
    GITHUB_REPO=richaldwinalcaraz-wq/Aldwin
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load env
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / "env" / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "richaldwinalcaraz-wq/Aldwin")
BRANCH = os.getenv("GITHUB_BRANCH", "main")

# Debounce: wait this many seconds after last change before pushing
DEBOUNCE_SECONDS = 5

# Files/dirs to ignore
IGNORE = {".git", "__pycache__", ".tmp", "env", ".DS_Store", "Thumbs.db"}


def run(cmd, cwd=ROOT):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def configure_remote():
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set in env/.env")
        print("  Add this line to env/.env:")
        print("  GITHUB_TOKEN=ghp_your_token_here")
        sys.exit(1)

    remote_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    
    # Check if remote exists
    code, out, _ = run(["git", "remote", "get-url", "origin"])
    if code != 0:
        run(["git", "remote", "add", "origin", remote_url])
        print(f"[+] Remote added: github.com/{GITHUB_REPO}")
    else:
        run(["git", "remote", "set-url", "origin", remote_url])
        print(f"[+] Remote updated: github.com/{GITHUB_REPO}")


def git_push(message=None):
    if message is None:
        from datetime import datetime
        message = f"Auto-save: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    code, out, err = run(["git", "add", "-A"])
    
    # Check if there's anything to commit
    code, out, _ = run(["git", "status", "--porcelain"])
    if not out:
        print("[~] No changes to push.")
        return

    code, out, err = run(["git", "commit", "-m", message])
    if code != 0:
        print(f"[!] Commit failed: {err}")
        return

    code, out, err = run(["git", "push", "-u", "origin", BRANCH])
    if code != 0:
        # Try setting upstream on first push
        code, out, err = run(["git", "push", "--set-upstream", "origin", BRANCH])
    
    if code == 0:
        print(f"[✓] Pushed: {message}")
    else:
        print(f"[!] Push failed: {err}")


def watch():
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("[!] watchdog not installed. Run: pip install watchdog")
        sys.exit(1)

    class Handler(FileSystemEventHandler):
        def __init__(self):
            self._pending = False
            self._last_event = 0

        def on_any_event(self, event):
            if event.is_directory:
                return
            # Skip ignored paths
            parts = Path(event.src_path).parts
            if any(p in IGNORE for p in parts):
                return
            self._last_event = time.time()
            self._pending = True

        def check_and_push(self):
            if self._pending and (time.time() - self._last_event) >= DEBOUNCE_SECONDS:
                self._pending = False
                git_push()

    configure_remote()

    # Do an initial push of everything
    print("[*] Initial sync to GitHub...")
    git_push("Initial sync: dashboard files")

    handler = Handler()
    observer = Observer()
    observer.schedule(handler, str(ROOT), recursive=True)
    observer.start()
    print(f"[*] Watching for changes in: {ROOT}")
    print(f"[*] Will auto-push to: github.com/{GITHUB_REPO} (branch: {BRANCH})")
    print("[*] Press Ctrl+C to stop.\n")

    try:
        while True:
            handler.check_and_push()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Watcher stopped.")
    observer.join()


if __name__ == "__main__":
    watch()
