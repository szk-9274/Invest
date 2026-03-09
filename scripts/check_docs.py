from __future__ import annotations

import re
from pathlib import Path

from doc_gardening import expected_managed_files

LINK_PATTERN = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
REQUIRED_FILES = [
    'README.md',
    'ARCHITECTURE.md',
    'COMMAND.md',
    'docs/DOCUMENTATION_SYSTEM.md',
    'docs/QUALITY_SCORE.md',
    'docs/design-docs/index.md',
    'docs/decision-log/index.md',
    'docs/exec-plans/active/index.md',
    'docs/exec-plans/completed/index.md',
    'docs/product-specs/index.md',
    'docs/working-memory/index.md',
    'docs/generated/doc-inventory.md',
    '.github/workflows/ci.yml',
    '.github/workflows/docs-governance.yml',
]
REQUIRED_NAVIGATION_LINKS = {
    'README.md': [
        'ARCHITECTURE.md',
        'COMMAND.md',
        'docs/DOCUMENTATION_SYSTEM.md',
    ],
    'ARCHITECTURE.md': [
        'docs/DOCUMENTATION_SYSTEM.md',
        'COMMAND.md',
    ],
    'docs/DOCUMENTATION_SYSTEM.md': [
        '../README.md',
        '../ARCHITECTURE.md',
        '../COMMAND.md',
        'design-docs/index.md',
        'decision-log/index.md',
        'exec-plans/active/index.md',
        'exec-plans/completed/index.md',
        'product-specs/index.md',
        'working-memory/index.md',
        'generated/doc-inventory.md',
    ],
}
REQUIRED_COMMANDS = [
    'python scripts/check_docs.py',
    'python scripts/doc_gardening.py',
    'pytest backend/tests --cov=backend --cov-report=term --cov-fail-under=80',
    'python -m backend.scripts.export_frontend_contracts',
    'npm --prefix frontend run build',
    'npm --prefix frontend run test:coverage',
    'npm run test:e2e',
    'npm run build',
    'docker compose config',
    'docker compose build',
]


def markdown_files(repo_root: Path) -> list[Path]:
    docs_files = sorted((repo_root / 'docs').rglob('*.md')) if (repo_root / 'docs').exists() else []
    root_files = [repo_root / name for name in ('README.md', 'ARCHITECTURE.md', 'COMMAND.md') if (repo_root / name).exists()]
    return root_files + docs_files


def resolve_link(source_path: Path, link_target: str) -> Path | None:
    if link_target.startswith(('http://', 'https://', 'mailto:')):
        return None
    clean_target = link_target.split('#', 1)[0]
    if not clean_target:
        return None
    return (source_path.parent / clean_target).resolve()


def markdown_link_targets(text: str) -> set[str]:
    return {
        target.split('#', 1)[0]
        for target in LINK_PATTERN.findall(text)
        if target and not target.startswith(('http://', 'https://', 'mailto:'))
    }


def find_broken_internal_links(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in markdown_files(repo_root):
        text = path.read_text(encoding='utf-8')
        for match in LINK_PATTERN.finditer(text):
            target = resolve_link(path, match.group(1))
            if target is None:
                continue
            if not target.exists():
                relative_path = path.relative_to(repo_root).as_posix()
                errors.append(
                    f'Broken internal link in {relative_path}: {match.group(1)}'
                )
    return errors


def find_missing_navigation_links(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for relative_path, expected_links in REQUIRED_NAVIGATION_LINKS.items():
        path = repo_root / relative_path
        if not path.exists():
            continue
        targets = markdown_link_targets(path.read_text(encoding='utf-8'))
        for expected in expected_links:
            if expected not in targets:
                errors.append(
                    f'Missing required navigation link in {relative_path}: {expected}'
                )
    return errors


def find_missing_required_files(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (repo_root / relative).exists():
            errors.append(f'Missing required documentation file: {relative}')
    return errors


def find_stale_managed_files(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path, expected_content in expected_managed_files(repo_root).items():
        if not path.exists():
            errors.append(f'Managed documentation file is missing: {path.relative_to(repo_root).as_posix()}')
            continue
        actual_content = path.read_text(encoding='utf-8')
        if actual_content != expected_content:
            errors.append(
                f'Managed documentation file is stale: {path.relative_to(repo_root).as_posix()}. Run python scripts/doc_gardening.py'
            )
    return errors


def find_missing_documented_commands(repo_root: Path) -> list[str]:
    command_doc = repo_root / 'COMMAND.md'
    if not command_doc.exists():
        return []

    text = command_doc.read_text(encoding='utf-8')
    return [
        f'Missing documented command in COMMAND.md: {command}'
        for command in REQUIRED_COMMANDS
        if command not in text
    ]


def run_checks(repo_root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(find_missing_required_files(repo_root))
    errors.extend(find_broken_internal_links(repo_root))
    errors.extend(find_missing_navigation_links(repo_root))
    errors.extend(find_missing_documented_commands(repo_root))
    errors.extend(find_stale_managed_files(repo_root))
    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    errors = run_checks(repo_root)
    if errors:
        print('Documentation integrity check failed:')
        for error in errors:
            print(f'- {error}')
        return 1
    print('Documentation integrity check passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
