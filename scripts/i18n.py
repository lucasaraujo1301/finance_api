from babel.messages.frontend import CommandLineInterface


def make_messages() -> None:
    cli = CommandLineInterface()

    cli.run(
        [
            "pybabel",
            "extract",
            "-F",
            "pyproject.toml",
            "-o",
            "locales/messages.pot",
            ".",
        ]
    )

    cli.run(
        [
            "pybabel",
            "update",
            "-i",
            "locales/messages.pot",
            "-d",
            "locales",
        ]
    )


def compile_messages() -> None:
    CommandLineInterface().run(
        [
            "pybabel",
            "compile",
            "-d",
            "locales",
        ]
    )
