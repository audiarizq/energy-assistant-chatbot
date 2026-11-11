"""Versi command-line EnergyBot.

Jalankan dari folder proyek dengan:
    python cli.py

Tema dapat diganti jika proyek memiliki lebih dari satu file tema:
    python cli.py --theme energybot
"""
import argparse
import os
import sys
from pathlib import Path

from chatbot import EnergyBotEngine, load_themes


BASE_DIR = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(description="Chat dengan chatbot tematik melalui terminal")
    parser.add_argument("--theme", default="energybot", help="ID tema yang digunakan (default: energybot)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=float(os.environ.get("THRESHOLD", "0.45")),
        help="Ambang pengenalan intent (default: 0.45)",
    )
    return parser.parse_args()


def main():
    # Terminal Windows lama sering memakai cp1252 dan tidak dapat mencetak
    # emoji avatar dari file tema.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    themes = load_themes(BASE_DIR / "themes")

    if args.theme not in themes:
        available = ", ".join(sorted(themes)) or "(tidak ada)"
        raise SystemExit(f"Tema '{args.theme}' tidak ditemukan. Pilihan: {available}")

    theme = themes[args.theme]
    bot = EnergyBotEngine(theme, args.threshold)
    context = {}

    print(f"{theme['avatar']} {theme['bot_name']} - mode CLI")
    print(theme["greeting"])
    print("Ketik 'exit' atau 'keluar' untuk mengakhiri.\n")

    while True:
        try:
            message = input("Anda: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa!")
            break

        if message.lower() in {"exit", "quit", "keluar"}:
            print("Sampai jumpa!")
            break
        if not message:
            continue

        result = bot.reply(message, context)
        print(f"{theme['bot_name']}: {result['reply']}\n")


if __name__ == "__main__":
    main()
