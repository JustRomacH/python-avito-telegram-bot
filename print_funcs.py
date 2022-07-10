from termcolor import cprint

# ? Functions for colorful logging


def error(prefix, ex):
    cprint(f"[{prefix.upper()}_ERROR] {repr(ex)}", "red")


def info(text):
    cprint(f"[INFO] {text}", "green")
