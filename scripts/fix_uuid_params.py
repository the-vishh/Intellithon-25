#!/usr/bin/env python3
"""
Fix function parameter Uuid → String conversions
"""

import re


def fix_uuid_params(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Fix: user_id: Uuid → user_id: String in function parameters
    content = re.sub(r"\buser_id:\s*Uuid\b", "user_id: String", content)
    content = re.sub(r"\buser_id:\s*&Uuid\b", "user_id: &str", content)

    # Fix: Option<Uuid> in function params
    content = re.sub(
        r"\(\s*user_id:\s*Option<Uuid>\s*\)", "(user_id: Option<String>)", content
    )

    # Fix impl signatures
    content = re.sub(
        r"pub fn new\(user_id: Uuid\)", "pub fn new(user_id: String)", content
    )
    content = re.sub(
        r"pub fn from_\w+\(user_id: Uuid",
        lambda m: m.group(0).replace("Uuid", "String"),
        content,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return original != content


if __name__ == "__main__":
    files = [
        "backend/src/db/models_analytics.rs",
        "backend/src/db/models.rs",
    ]

    for f in files:
        try:
            if fix_uuid_params(f):
                print(f"✅ Fixed {f}")
            else:
                print(f"⏭️  {f} - no changes")
        except Exception as e:
            print(f"❌ {f}: {e}")
