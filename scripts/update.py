#!/usr/bin/env python3
"""
HuyNex Agent Kit — Auto-Update Client & Background Daemon (update.py)
-------------------------------------------------------------------
Tự động phát hiện phiên bản mới trên GitHub, kéo về và cập nhật toàn bộ Agent Clients:
1. So sánh Git commit HEAD vs origin/main.
2. Nếu có bản mới: git pull + tự động chạy install.py --all.
3. Hỗ trợ cài đặt Background Daemon (Launchd trên macOS, Task Scheduler trên Windows, Cron trên Linux).
4. Bắn Desktop Notification thông báo cho người dùng khi có bài học/kỹ năng mới từ Huy.
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = KIT_ROOT / "scripts"
INSTALL_SCRIPT = SCRIPTS_DIR / "install.py"
LOGS_DIR = Path.home() / ".huynex/logs"


def send_notification(title: str, message: str):
    """Gửi thông báo desktop đa nền tảng."""
    try:
        if sys.platform == "darwin":
            script = f'display notification "{message}" with title "{title}" sound name "default"'
            subprocess.run(["osascript", "-e", script], capture_output=True)
        elif sys.platform.startswith("linux"):
            subprocess.run(["notify-send", title, message], capture_output=True)
        elif sys.platform == "win32":
            ps_cmd = f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); [System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    except Exception:
        pass


def check_git_status() -> tuple[bool, str]:
    """
    Kiểm tra xem repo có cập nhật mới trên GitHub hay không.
    Trả về (has_update, status_message).
    """
    if not (KIT_ROOT / ".git").is_dir():
        return False, "Thư mục không phải là Git repository."

    try:
        # Fetch ngầm từ remote origin
        fetch_res = subprocess.run(
            ["git", "-C", str(KIT_ROOT), "fetch", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if fetch_res.returncode != 0:
            return False, f"Không thể kết nối đến GitHub: {fetch_res.stderr.strip()}"

        # Lấy commit hash local vs remote
        local_hash = subprocess.run(
            ["git", "-C", str(KIT_ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        remote_hash = subprocess.run(
            ["git", "-C", str(KIT_ROOT), "rev-parse", "origin/main"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        if local_hash != remote_hash:
            # Lấy thông điệp commit mới
            log_res = subprocess.run(
                ["git", "-C", str(KIT_ROOT), "log", "-1", "--format=%s (%h)", "origin/main"],
                capture_output=True,
                text=True,
            )
            commit_msg = log_res.stdout.strip() if log_res.returncode == 0 else "Bản cập nhật mới"
            return True, f"Phát hiện bản cập nhật mới trên GitHub: {commit_msg}"
        else:
            return False, "Hệ thống đang ở phiên bản mới nhất."

    except subprocess.TimeoutExpired:
        return False, "Quá thời gian kết nối (Timeout) khi kiểm tra GitHub."
    except Exception as e:
        return False, f"Lỗi kiểm tra git: {str(e)}"


def perform_update() -> bool:
    """Thực hiện git pull và chạy install.py --all."""
    print("=" * 65)
    print("HUYNEX AGENT KIT — TIẾN HÀNH CẬP NHẬT TỰ ĐỘNG")
    print(f"Thời gian: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 65)

    try:
        # 1. Git pull
        print("\n[1] Đang kéo mã nguồn mới nhất từ GitHub...")
        pull_res = subprocess.run(
            ["git", "-C", str(KIT_ROOT), "pull", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if pull_res.returncode != 0:
            print(f"❌ Git pull thất bại: {pull_res.stderr}")
            return False

        print(pull_res.stdout.strip())

        # 2. Cài đặt / cập nhật kỹ năng vào mọi client
        print("\n[2] Đang đồng bộ kỹ năng & quy tắc vào các AI Agent...")
        install_res = subprocess.run(
            [sys.executable, str(INSTALL_SCRIPT), "--all"],
            capture_output=True,
            text=True,
        )
        print(install_res.stdout.strip())

        if install_res.returncode == 0:
            print("\n✅ Cập nhật thành công toàn bộ hệ thống!")
            send_notification(
                "HuyNex Agent Kit",
                "🎉 Đã tự động cập nhật kỹ năng & bài học mới nhất từ Huy!",
            )
            return True
        else:
            print(f"⚠️ Lỗi khi cài đặt kỹ năng: {install_res.stderr}")
            return False

    except Exception as e:
        print(f"❌ Lỗi trong quá trình cập nhật: {e}")
        return False


def setup_daemon():
    """Cài đặt daemon tự động kiểm tra và cập nhật ngầm."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    python_exe = sys.executable
    script_path = str(SCRIPTS_DIR / "update.py")

    if sys.platform == "darwin":
        # macOS: Launchd
        launch_agents_dir = Path.home() / "Library/LaunchAgents"
        launch_agents_dir.mkdir(parents=True, exist_ok=True)
        plist_path = launch_agents_dir / "com.huynex.agentkit.updater.plist"

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.huynex.agentkit.updater</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{script_path}</string>
        <string>--auto</string>
    </array>
    <key>StartInterval</key>
    <integer>21600</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{LOGS_DIR}/updater.log</string>
    <key>StandardErrorPath</key>
    <string>{LOGS_DIR}/updater_err.log</string>
</dict>
</plist>
"""
        plist_path.write_text(plist_content, encoding="utf-8")
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        res = subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, text=True)
        if res.returncode == 0:
            print("✅ Đã kích hoạt Background Daemon (macOS Launchd) thành công!")
            print(f"   Lịch trình: Tự động kiểm tra cập nhật mỗi 6 giờ và mỗi khi đăng nhập.")
            print(f"   File cấu hình: {plist_path}")
        else:
            print(f"⚠️ Không thể nạp launchd plist: {res.stderr}")

    elif sys.platform == "win32":
        # Windows: Task Scheduler
        cmd = f'schtasks /create /tn "HuyNexAgentKitUpdater" /tr "{python_exe} \\"{script_path}\\" --auto" /sc daily /st 09:00 /f'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            print("✅ Đã tạo Windows Task Scheduler thành công (Chạy hằng ngày vào 09:00).")
        else:
            print(f"⚠️ Không thể tạo Windows Scheduled Task: {res.stderr}")

    else:
        # Linux: Cron
        cron_job = f"0 */6 * * * {python_exe} {script_path} --auto >> {LOGS_DIR}/updater.log 2>&1\n"
        print("💡 Trên Linux, hãy thêm dòng sau vào crontab (`crontab -e`):")
        print(f"   {cron_job}")


def remove_daemon():
    """Hủy kích hoạt daemon."""
    if sys.platform == "darwin":
        plist_path = Path.home() / "Library/LaunchAgents/com.huynex.agentkit.updater.plist"
        if plist_path.is_file():
            subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
            plist_path.unlink()
            print("✅ Đã hủy kích hoạt Background Daemon trên macOS.")
    elif sys.platform == "win32":
        subprocess.run('schtasks /delete /tn "HuyNexAgentKitUpdater" /f', shell=True, capture_output=True)
        print("✅ Đã xóa Windows Scheduled Task.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Kiểm tra xem có cập nhật mới trên GitHub không")
    parser.add_argument("--pull", action="store_true", help="Kéo bản cập nhật mới và cài đặt ngay lập tức")
    parser.add_argument("--auto", action="store_true", help="Chế độ chạy ngầm (dành cho background daemon)")
    parser.add_argument("--enable-auto-update", action="store_true", help="Kích hoạt Background Daemon tự động cập nhật ngầm")
    parser.add_argument("--disable-auto-update", action="store_true", help="Hủy kích hoạt Background Daemon")

    args = parser.parse_args()

    if args.check:
        has_update, msg = check_git_status()
        print(f"🔍 Trạng thái: {msg}")
        if has_update:
            print("💡 Hãy chạy `python3 scripts/update.py --pull` để cập nhật ngay.")

    elif args.pull:
        has_update, msg = check_git_status()
        if not has_update and "mới nhất" in msg:
            print(f"✅ {msg}")
            return
        perform_update()

    elif args.auto:
        # Chế độ chạy ngầm của daemon
        has_update, msg = check_git_status()
        if has_update:
            perform_update()

    elif args.enable_auto_update:
        setup_daemon()

    elif args.disable_auto_update:
        remove_daemon()

    else:
        # Mặc định: kiểm tra và hỏi cập nhật
        has_update, msg = check_git_status()
        print(f"🔍 {msg}")
        if has_update:
            perform_update()


if __name__ == "__main__":
    main()
