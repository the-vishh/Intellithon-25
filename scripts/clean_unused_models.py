#!/usr/bin/env python3
"""
Clean up models.rs - remove references to non-existent tables
"""

import re


def clean_models():
    file_path = "backend/src/db/models.rs"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and remove Scan model section (lines ~52-100)
    # Find and remove ModelMetrics section
    # Find and remove GlobalStats section

    # Pattern to match struct and impl blocks
    sections_to_remove = [
        (r"// SCAN MODEL.*?(?=// .*? MODEL|\Z)", "Scan"),
        (r"// MODEL METRICS MODEL.*?(?=// .*? MODEL|\Z)", "ModelMetrics"),
        (r"// GLOBAL STATS MODEL.*?(?=// .*? MODEL|\Z)", "GlobalStats"),
    ]

    for pattern, name in sections_to_remove:
        # Use DOTALL to match across newlines
        matches = list(re.finditer(pattern, content, re.DOTALL))
        if matches:
            print(f"Found {len(matches)} {name} section(s)")
            content = re.sub(pattern, "", content, flags=re.DOTALL)

    # Clean up any remaining impl blocks for removed structs
    content = re.sub(r"impl NewScan \{.*?\n\}\n", "", content, flags=re.DOTALL)
    content = re.sub(r"impl NewModelMetrics \{.*?\n\}\n", "", content, flags=re.DOTALL)

    # Clean up multiple blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Cleaned up {file_path}")


if __name__ == "__main__":
    clean_models()
