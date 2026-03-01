#!/usr/bin/env python3
"""Initialize ChromaDB vector store for research content."""

import importlib
import site
import subprocess
import sys
import os


def find_project_root():
    """Walk up from this script to find the directory containing .claude/."""
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".claude")):
            return d
        d = os.path.dirname(d)
    # Fallback: assume 4 levels up from scripts/init_vectordb.py
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def check_python():
    """Verify python3.13 is available."""
    print("Checking python3.13...", end=" ")
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True, text=True, check=True
        )
        print(f"OK ({result.stdout.strip()})")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FAILED")
        print("Error: python3.13 is required. Install it via: brew install python@3.13")
        return False


def install_chromadb():
    """Install chromadb if not already available."""
    print("Checking chromadb...", end=" ")
    try:
        import chromadb  # noqa: F401
        print("OK (already installed)")
        return True
    except ImportError:
        pass

    print("not found, installing...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user",
             "--break-system-packages", "chromadb"],
            check=True, capture_output=True, text=True
        )
        # Ensure user site-packages is on sys.path for the current process
        user_site = site.getusersitepackages()
        if user_site not in sys.path:
            sys.path.insert(0, user_site)
        importlib.invalidate_caches()
        print("  chromadb installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  FAILED to install chromadb: {e.stderr}")
        return False


def setup_gitignore(project_root):
    """Ensure research-memory/ is in .gitignore."""
    gitignore_path = os.path.join(project_root, ".gitignore")
    entry = ".research-memory/"
    print(f"Checking .gitignore for '{entry}'...", end=" ")

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            content = f.read()
        if entry in content.splitlines():
            print("OK (already present)")
            return True
        # Append entry
        with open(gitignore_path, "a") as f:
            if not content.endswith("\n"):
                f.write("\n")
            f.write(f"{entry}\n")
        print("OK (appended)")
    else:
        with open(gitignore_path, "w") as f:
            f.write(f"{entry}\n")
        print("OK (created)")
    return True


def fix_db_permissions(db_path):
    """Ensure the vectordb directory and its files have appropriate permissions."""
    for dirpath, _, filenames in os.walk(db_path):
        os.chmod(dirpath, 0o755)
        for filename in filenames:
            os.chmod(os.path.join(dirpath, filename), 0o644)


def smoke_test(project_root):
    """Create the ChromaDB persistent store and research collection."""
    print("Initializing ChromaDB...", end=" ")
    db_path = os.path.join(project_root, ".research-memory")

    try:
        import chromadb
        os.makedirs(db_path, mode=0o755, exist_ok=True)
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(
            name="research",
            metadata={"hnsw:space": "cosine"}
        )
        count = collection.count()
        fix_db_permissions(db_path)
        print(f"OK (collection 'research' has {count} documents)")
        print(f"  Database path: {db_path}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False


def main():
    print("=" * 50)
    print("Vector Store Initialization")
    print("=" * 50)
    print()

    project_root = find_project_root()
    print(f"Project root: {project_root}")
    print()

    steps = [
        ("Python check", lambda: check_python()),
        ("Install chromadb", lambda: install_chromadb()),
        ("Setup .gitignore", lambda: setup_gitignore(project_root)),
        ("Smoke test", lambda: smoke_test(project_root)),
    ]

    for name, fn in steps:
        if not fn():
            print(f"\nSetup failed at: {name}")
            sys.exit(1)
        print()

    print("=" * 50)
    print("Vector store initialized successfully!")
    print()
    print("Next steps:")
    print("  - Run /deep-research to populate the vector store")
    print("  - Run /ask-research <question> to query stored content")
    print("=" * 50)


if __name__ == "__main__":
    main()
