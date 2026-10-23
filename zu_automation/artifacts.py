"""Persist Appium recordings and screenshots for later inspection."""

import base64
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


def artifact_name(test_id):
    safe_test_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_id).strip("._")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{safe_test_id}_{timestamp}"


def save_recording(driver, name, test_node):
    video_dir = ARTIFACTS_DIR / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    video_path = video_dir / f"{name}.mp4"

    try:
        recording = driver.stop_recording_screen()
        if not recording:
            print("\n[artifacts] O Appium não devolveu dados de vídeo.")
            return

        video_path.write_bytes(base64.b64decode(recording))
        print(f"\n[artifacts] Vídeo guardado: {video_path.relative_to(PROJECT_ROOT)}")

        report = getattr(test_node, "rep_call", None)
        if report is not None and report.passed and _is_portfolio_test(test_node):
            build_readme_gif(video_path)
    except Exception as error:
        print(f"\n[artifacts] Não foi possível guardar o vídeo: {error}")


def save_screenshot(driver, name, test_node):
    screenshot_dir = ARTIFACTS_DIR / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshot_dir / f"{name}.png"

    try:
        screenshot = driver.get_screenshot_as_png()
        screenshot_path.write_bytes(screenshot)
        print(
            f"\n[artifacts] Screenshot guardado: "
            f"{screenshot_path.relative_to(PROJECT_ROOT)}"
        )

        report = getattr(test_node, "rep_call", None)
        if report is not None and report.passed and _is_portfolio_test(test_node):
            preview_path = PROJECT_ROOT / "docs" / "assets" / "app-screen.png"
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            preview_path.write_bytes(screenshot)
            print(
                "[artifacts] Screenshot de portfólio: "
                f"{preview_path.relative_to(PROJECT_ROOT)}"
            )
    except Exception as error:
        print(f"\n[artifacts] Não foi possível guardar o screenshot: {error}")


def build_readme_gif(video_path):
    converter = PROJECT_ROOT / "scripts" / "build_demo_gif.py"
    command = [
        sys.executable,
        str(converter),
        "--input",
        str(video_path),
        "--output",
        str(PROJECT_ROOT / "docs" / "assets" / "demo.gif"),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    message = result.stdout.strip() or result.stderr.strip()
    if result.returncode == 0:
        print(f"[artifacts] {message}")
    else:
        print(f"[artifacts] GIF não gerado: {message}")


def _is_portfolio_test(test_node):
    """Only designated tests may replace the checked-in portfolio media."""
    return test_node.get_closest_marker("portfolio") is not None
