#!/usr/bin/env python3
# auto_push.py — buruniverse-website 自動 git push
# content/ 以下の .md ファイルが変化したら git pull → add → commit → push

import subprocess
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ─────────────────────────────────────────
# 設定
# ─────────────────────────────────────────

REPO_DIR   = Path(__file__).parent          # buruniverse-website/
WATCH_DIR  = REPO_DIR / "content"           # 監視対象
LOG_FILE   = REPO_DIR / "auto_push.log"
DEBOUNCE   = 8.0   # 秒（連続保存でも1回だけ走らせる）

# ─────────────────────────────────────────
# ログ設定
# ─────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────
# git 操作
# ─────────────────────────────────────────

def run_git(args: list[str]) -> tuple[int, str]:
    """git コマンドを実行して (returncode, output) を返す。"""
    result = subprocess.run(
        ["git"] + args,
        cwd=str(REPO_DIR),
        capture_output=True,
        text=True,
    )
    out = (result.stdout + result.stderr).strip()
    return result.returncode, out


def try_push() -> bool:
    """push だけ試みる。成功したら True。"""
    code, out = run_git(["push", "origin", "main"])
    if code == 0:
        log.info("git push OK ✅")
        return True
    else:
        log.warning(f"git push 失敗（オフライン？）— 後でリトライ:\n{out}")
        return False


def auto_push(changed_files: list[str]):
    """pull → add → commit → push を実行する。pushはオフラインでも後でリトライ。"""
    log.info(f"変更検出: {', '.join(changed_files)}")

    # 1. pull（失敗してもcommitは続ける）
    code, out = run_git(["pull", "--rebase", "origin", "main"])
    if code == 0:
        log.info("git pull OK")
    else:
        log.warning(f"git pull スキップ（オフライン？）:\n{out}")

    # 2. add（content/ 以下だけ）
    code, out = run_git(["add", "content/"])
    if code != 0:
        log.error(f"git add 失敗:\n{out}")
        return

    # 3. 変更があるか確認
    code, out = run_git(["diff", "--cached", "--name-only"])
    if not out.strip():
        log.info("差分なし、スキップ")
        return

    staged_files = out.strip().split("\n")
    commit_msg = f"auto: {', '.join(Path(f).name for f in staged_files)}"

    # 4. commit（オフラインでもローカルには必ず残す）
    code, out = run_git(["commit", "-m", commit_msg])
    if code != 0:
        log.error(f"git commit 失敗:\n{out}")
        return
    log.info(f"git commit: {commit_msg}")

    # 5. push（失敗してもリトライループが拾う）
    try_push()


def retry_push_loop():
    """未pushのコミットがあれば60秒ごとにpushをリトライする。"""
    import threading

    def _loop():
        while True:
            time.sleep(60)
            # unpushed commits があるか確認
            code, out = run_git(["log", "origin/main..HEAD", "--oneline"])
            if code == 0 and out.strip():
                log.info(f"未pushコミット検出、リトライ: {out.strip()[:80]}")
                # pull してから push
                run_git(["pull", "--rebase", "origin", "main"])
                try_push()

    t = threading.Thread(target=_loop, daemon=True)
    t.start()

# ─────────────────────────────────────────
# ファイル監視
# ─────────────────────────────────────────

class MDHandler(FileSystemEventHandler):
    def __init__(self):
        self._timer      = None
        self._changed    = []

    def _schedule(self, path: str):
        """デバウンス: DEBOUNCE 秒後に auto_push を1回だけ呼ぶ。"""
        if path not in self._changed:
            self._changed.append(path)

        if self._timer is not None:
            self._timer.cancel()

        import threading
        self._timer = threading.Timer(DEBOUNCE, self._fire)
        self._timer.start()

    def _fire(self):
        files = list(self._changed)
        self._changed.clear()
        self._timer = None
        auto_push(files)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            self._schedule(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            self._schedule(event.src_path)


# ─────────────────────────────────────────
# エントリポイント
# ─────────────────────────────────────────

if __name__ == "__main__":
    log.info(f"auto_push 起動 — 監視: {WATCH_DIR}")

    # オフライン時の未pushコミットをバックグラウンドでリトライ
    retry_push_loop()

    observer = Observer()
    observer.schedule(MDHandler(), str(WATCH_DIR), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("停止")
        observer.stop()
    observer.join()
