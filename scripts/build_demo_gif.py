"""Create a compact GIF preview from an Appium test recording."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_DIR = PROJECT_ROOT / "artifacts" / "videos"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "assets" / "demo.gif"


def _latest_recording() -> Path:
    recordings = list(VIDEO_DIR.glob("*.mp4"))
    if not recordings:
        raise SystemExit(
            f"Não encontrei gravações em {VIDEO_DIR}. Execute primeiro um teste Appium."
        )
    return max(recordings, key=lambda path: path.stat().st_mtime)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Converte uma gravação MP4 do Appium num GIF para o README."
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Gravação MP4 de origem. Por omissão, usa a gravação mais recente.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Ficheiro GIF de destino (por omissão: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=0,
        help="Segundo da gravação em que começa o GIF.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=12,
        help="Duração do GIF em segundos (máximo recomendado: 15).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=420,
        help="Largura do GIF em píxeis; a altura mantém a proporção.",
    )
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit(
            "Não encontrei o FFmpeg no PATH. Instale o FFmpeg para gerar o GIF; "
            "a gravação MP4 continua disponível em artifacts/videos/."
        )

    input_path = args.input.resolve() if args.input else _latest_recording()
    if not input_path.is_file():
        raise SystemExit(f"A gravação não existe: {input_path}")
    if args.duration <= 0 or args.width <= 0 or args.start < 0:
        raise SystemExit("A duração e a largura têm de ser positivas e o início não negativo.")

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    filter_graph = (
        f"fps=8,scale={args.width}:-1:flags=lanczos,split[s0][s1];"
        "[s0]palettegen=max_colors=96[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=3"
    )
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        str(args.start),
        "-i",
        str(input_path),
        "-t",
        str(args.duration),
        "-an",
        "-filter_complex",
        filter_graph,
        "-loop",
        "0",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise SystemExit(f"O FFmpeg não conseguiu criar o GIF:\n{result.stderr.strip()}")

    try:
        display_path = output_path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = output_path
    print(f"GIF criado: {display_path}")


if __name__ == "__main__":
    main()
