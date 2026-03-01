#!/usr/bin/env python3
"""Set up a research project folder with initial JSON files."""

import json
import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: setup_research.py <folder-name>", file=sys.stderr)
        sys.exit(1)

    folder_name = sys.argv[1]
    folder_path = os.path.abspath(folder_name)

    # Create folder if needed
    if os.path.isdir(folder_path):
        print(f"Folder already exists: {folder_path}")
    else:
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created folder: {folder_path}")

    # Files to initialize: (filename, empty_value)
    files = [
        ("search-results.json", {}),
    ]

    for filename, empty_value in files:
        filepath = os.path.join(folder_path, filename)
        if os.path.exists(filepath):
            print(f"  {filename} — already exists, skipping")
        else:
            with open(filepath, "w") as f:
                json.dump(empty_value, f, indent=2)
                f.write("\n")
            print(f"  {filename} — created")

    print()
    print(f"Research folder ready: {folder_path}")
    print(f"  search-results.json  — source evaluations (keyed by URL)")


if __name__ == "__main__":
    main()
