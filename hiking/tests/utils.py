import re

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def ansi_escape(value: str):
    return ANSI_ESCAPE.sub("", value)
