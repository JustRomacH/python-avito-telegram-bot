from logging import exception
from pyfiglet import Figlet
from termcolor import cprint

# ? Functions for colorful logging


def error(prefix: str, ex):
    cprint(f"[{prefix.upper()}_ERROR] {repr(ex)}", "red")


def info(text: str):
    cprint(f"[INFO] {text}", "green")


def logo(color: str):
    preview = Figlet(font="doom")
    cprint(preview.renderText("RomacH"), color)
