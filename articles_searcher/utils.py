import re


def change_string_for_redis_search_input(input_string):
    input_string = input_string.replace(" ", "")
    escaped = re.escape(input_string)
    escaped = escaped.translate(
        str.maketrans(
            {
                "!": r"\!",
                "@": r"\@",
                "=": r"\=",
                ";": r"\;",
                ":": r"\:",
                "'": r"\'",
                '"': r"\"",
                ",": r"\,",
                "<": r"\<",
                ">": r"\>",
                "/": r"\/",
                "\\": r"\\",
                ".": r"\.",
                "-": r"\-",
                "_": r"\_",
                "[": r"\[",
                "]": r"\]",
            }
        )
    )
    return escaped