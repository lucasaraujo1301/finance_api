import argparse
import re
import sys

from pathlib import Path

MODULE_FILES = {
    "__init__.py": "",
    "models.py": "",
    "schemas.py": "",
    "services.py": "",
    "exceptions.py": "",
    "repository.py": "",
    "dependencies.py": "",
    "router.py": """from fastapi import APIRouter

router = APIRouter()
""",
    "tests/__init__.py": "",
}

MODULE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def start_module(name: str) -> None:
    if not MODULE_NAME_PATTERN.fullmatch(name):
        raise SystemExit(
            "Module name must use snake_case, start with a letter, "
            "and contain only lowercase letters, numbers, and underscores."
        )

    module_dir = Path("modules") / name

    if module_dir.exists():
        raise SystemExit(f"Module already exists: {module_dir}")

    for filename, content in MODULE_FILES.items():
        file_path = module_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    sys.stdout.write(f"Created module: {module_dir}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new application module.")
    parser.add_argument("name", help="Module name, e.g. entry, transaction, bank_account")
    args = parser.parse_args()

    start_module(args.name)


if __name__ == "__main__":
    main()
