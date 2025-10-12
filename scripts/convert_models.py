#!/usr/bin/env python3
"""
Convert Rust models from PostgreSQL types to SQLite types
"""

import re
import sys


def convert_file(filepath):
    """Convert a Rust file from PostgreSQL to SQLite types"""

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Replace Uuid with String in struct fields
    content = re.sub(r"\bpub\s+(\w+):\s*Uuid\b", r"pub \1: String", content)

    # 2. Replace Option<Uuid> with Option<String>
    content = re.sub(r"\bOption<Uuid>", "Option<String>", content)

    # 3. Replace DateTime<Utc> with i64 (Unix timestamp)
    content = re.sub(r"\bDateTime<Utc>", "i64", content)

    # 4. Replace Option<DateTime<Utc>> with Option<i64>
    content = re.sub(r"\bOption<DateTime<Utc>>", "Option<i64>", content)

    # 5. Replace bool with i32 for SQLite compatibility
    content = re.sub(r"\bpub\s+(\w+):\s*bool\b", r"pub \1: i32", content)

    # 6. Update imports - remove chrono if not needed
    if "i64" in content and "DateTime" not in content:
        content = re.sub(r"use chrono::\{DateTime, Utc\};?\n?", "", content)

    # 7. Comment about UUID being String now
    if "// @generated" not in content and original != content:
        header = "// NOTE: Converted for SQLite - UUID types are now String, DateTime types are i64 (Unix timestamps)\n\n"
        content = header + content

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    if original != content:
        return True, "Modified"
    else:
        return False, "No changes needed"


if __name__ == "__main__":
    import glob

    # Find all model files
    model_files = [
        "backend/src/db/models.rs",
        "backend/src/db/models_analytics.rs",
    ]

    print("=" * 50)
    print("Converting models to SQLite types...")
    print("=" * 50)
    print()

    for filepath in model_files:
        try:
            changed, status = convert_file(filepath)
            icon = "✅" if changed else "⏭️"
            print(f"{icon} {filepath}: {status}")
        except FileNotFoundError:
            print(f"⚠️  {filepath}: Not found, skipping")
        except Exception as e:
            print(f"❌ {filepath}: ERROR - {e}")

    print()
    print("=" * 50)
    print("✅ Conversion complete!")
    print("=" * 50)
    print()
    print("NOTE: You may need to manually fix:")
    print("  - Uuid::new_v4() → Uuid::new_v4().to_string()")
    print("  - Utc::now() → Utc::now().timestamp()")
    print("  - bool comparisons (0/1 instead of true/false)")
    print()
