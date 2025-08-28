"""
Validate Python import statements across the repository without executing modules.

This script walks selected directories, parses Python files with AST,
and validates that imported modules can be resolved using importlib.util.find_spec.

Usage:
  python tools/validate_imports.py [--root <repo_root>] [--paths path1 path2 ...] [--verbose]

Exit codes:
  0 - All imports resolved
  1 - One or more imports failed to resolve

Notes:
  - This uses find_spec to avoid executing imported modules.
  - Relative imports are resolved based on the file's package path.
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import importlib.util


DEFAULT_SCAN_PATHS = [
    "api",  # Main backend package
]


@dataclass
class ImportIssue:
    file_path: str
    line: int
    col: int
    import_str: str
    message: str


def iter_python_files(paths: Iterable[str]) -> Iterable[str]:
    for base in paths:
        if os.path.isfile(base) and base.endswith(".py"):
            yield base
        else:
            for root, _dirs, files in os.walk(base):
                for f in files:
                    if f.endswith(".py"):
                        yield os.path.join(root, f)


def to_package_name(repo_root: str, file_path: str) -> Optional[str]:
    # Convert a file path to the CONTAINING PACKAGE dotted name, if under repo_root
    try:
        rel = os.path.relpath(file_path, repo_root)
    except ValueError:
        return None
    if rel.startswith(".."):
        return None
    if rel.endswith("/__init__.py"):
        # For package __init__.py, the package is the directory itself
        pkg_rel = rel[: -len("/__init__.py")]
    elif rel.endswith(".py"):
        # For module files, the containing package is the parent directory
        mod_rel = rel[: -len(".py")]
        parts = mod_rel.split(os.sep)
        if len(parts) <= 1:
            return None
        pkg_rel = os.sep.join(parts[:-1])
    else:
        return None
    dotted = pkg_rel.replace(os.sep, ".")
    return dotted


def resolve_relative(module: Optional[str], level: int, current_pkg: str) -> Optional[str]:
    """Resolve a relative import to an absolute module name.

    For example, in package "api.components.retriever", from .faiss import X
    with level=1 and module="faiss" becomes "api.components.retriever.faiss".
    """
    if level <= 0:
        return module
    # Python semantics: level=1 means current package; level>1 goes up (level-1) parents
    parts = current_pkg.split(".") if current_pkg else []
    if not parts:
        return module
    up = max(level - 1, 0)
    if up > len(parts):
        return None
    base = ".".join(parts[: len(parts) - up])
    if not module:
        return base if base else None
    return f"{base}.{module}" if base else module


def find_spec_safe(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


def validate_file(repo_root: str, file_path: str) -> List[ImportIssue]:
    issues: List[ImportIssue] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        issues.append(
            ImportIssue(file_path=file_path, line=1, col=0, import_str="<read>", message=f"Failed to read file: {e}")
        )
        return issues

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        issues.append(
            ImportIssue(
                file_path=file_path,
                line=e.lineno or 1,
                col=e.offset or 0,
                import_str="<syntax>",
                message=f"Syntax error: {e.msg}",
            )
        )
        return issues

    current_pkg = to_package_name(repo_root, file_path) or ""

    INTERNAL_PREFIXES = ("api", "adalflow")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                # Only validate internal imports by prefix
                if not mod.startswith(INTERNAL_PREFIXES):
                    continue
                if not find_spec_safe(mod):
                    issues.append(
                        ImportIssue(
                            file_path=file_path,
                            line=node.lineno,
                            col=node.col_offset,
                            import_str=mod,
                            message="Module not found",
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            abs_mod = resolve_relative(module, node.level, current_pkg)
            if abs_mod is None:
                issues.append(
                    ImportIssue(
                        file_path=file_path,
                        line=node.lineno,
                        col=node.col_offset,
                        import_str=f"from {'.'*node.level}{module or ''}",
                        message="Unable to resolve relative import base",
                    )
                )
                continue

            # Validate the module itself first
            if abs_mod.startswith(INTERNAL_PREFIXES) and not find_spec_safe(abs_mod):
                issues.append(
                    ImportIssue(
                        file_path=file_path,
                        line=node.lineno,
                        col=node.col_offset,
                        import_str=f"{abs_mod}",
                        message="Module not found",
                    )
                )
                continue

            # Optionally validate imported names by checking submodule existence
            for alias in node.names:
                name = alias.name
                # Try submodule first: abs_mod.name
                candidate = f"{abs_mod}.{name}"
                if find_spec_safe(candidate):
                    continue
                # If not a submodule, it might be a symbol inside the module; we cannot validate without executing.
                # So we skip symbol-level validation to avoid imports with side-effects.

    return issues


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Python import statements without executing modules.")
    parser.add_argument("--root", default=os.getcwd(), help="Repository root (defaults to CWD)")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=DEFAULT_SCAN_PATHS,
        help="Paths (relative to root) to scan for Python files",
    )
    parser.add_argument("--verbose", action="store_true", help="Print per-file status")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = os.path.abspath(args.root)
    scan_paths = [os.path.join(repo_root, p) for p in args.paths]

    # Ensure repository root is at the front of sys.path so local packages
    # like `api` resolve before any site-packages with conflicting names.
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    all_issues: List[ImportIssue] = []
    files = list(iter_python_files(scan_paths))
    for fp in files:
        rel = os.path.relpath(fp, repo_root)
        issues = validate_file(repo_root, fp)
        if args.verbose:
            print(f"[OK] {rel}" if not issues else f"[ERR] {rel} ({len(issues)})")
        all_issues.extend(issues)

    if all_issues:
        print("Import validation found issues:\n")
        for issue in all_issues:
            rel = os.path.relpath(issue.file_path, repo_root)
            print(f"{rel}:{issue.line}:{issue.col}: {issue.import_str} -> {issue.message}")
        return 1

    print("All imports resolved successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


