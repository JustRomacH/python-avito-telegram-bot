from termcolor import cprint


def error(prefix, ex):
    cprint(f"[{prefix.upper()}_ERROR] {repr(ex)}", "red")


def info(text):
    cprint(f"[INFO] {text}", "green")
