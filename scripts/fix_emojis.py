#!/usr/bin/env python3
"""Remove emojis from Python files for Windows compatibility"""

import re
from pathlib import Path


def remove_emojis(text):
    """Remove all emojis from text"""
    # Pattern to match emojis
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002500-\U00002bef"  # chinese char
        "\U00002702-\U000027b0"
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2b55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        re.UNICODE,
    )

    return emoji_pattern.sub("", text)


def fix_file(filepath):
    """Remove emojis from a file"""
    print(f"Processing {filepath}...")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove emojis
    clean_content = remove_emojis(content)

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(clean_content)

    print(f"  Done! Removed emojis from {filepath}")


if __name__ == "__main__":
    # Get all Python files in ml-model directory
    ml_model_dir = Path(__file__).parent / "ml-model"

    if ml_model_dir.exists():
        python_files = list(ml_model_dir.rglob("*.py"))
        print(f"Found {len(python_files)} Python files in ml-model directory\n")

        for py_file in python_files:
            fix_file(py_file)
    else:
        print(f"ml-model directory not found at {ml_model_dir}")

    print("\nAll files processed!")
