from pyfiglet import Figlet
from termcolor import cprint

# Functions for colorful logging


def error(prefix: str, ex: Exception) -> None:
    cprint(f"[{prefix.upper()}_ERROR] {repr(ex)}", "red")


def info(text: str) -> None:
    cprint(f"[INFO] {text}", "green")


def special_info(text: str) -> None:
    cprint(f"[INFO] {text}", "yellow")


def progress(counter: int, max_pos: int) -> None:
    cprint(f"[+] Обработано {counter}/{max_pos} страниц", "cyan")


def logo(color: str) -> None:
    preview = Figlet(font="doom")
    logo_str = f"{preview.renderText('RomacH').strip()}\n"
    cprint(logo_str, color)
