from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".example",
    ".ini",
    ".json",
    ".md",
    ".markdown",
    ".toml",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {"Dockerfile", "Dockerfile.prod", "Caddyfile.example"}
PLACEHOLDER_MARKERS = (
    "$",
    "<",
    "[credential_",
    "cambiar_",
    "change_me",
    "coloque_",
    "example",
    "placeholder",
    "not-a-secret",
    "test-",
    "ci-only-",
)
ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:export\s+)?(?P<name>[A-Z0-9_]*(?:PASSWORD|PASSWD|SECRET|API_KEY|PRIVATE_KEY)[A-Z0-9_]*|[A-Z0-9_]+_TOKEN|TOKEN)\s*[:=]\s*(?P<value>[^\r\n#]+)"
)
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "cloud access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "credential URI": re.compile(r"(?i)\b(?:postgres(?:ql)?|redis|mysql|mongodb(?:\+srv)?|https?)://[^\s/:]+:(?![^@\s]*(?:CAMBIAR|PASSWORD|PLACEHOLDER|EXAMPLE|\$|<|\[))[^\s/@]+@"),
    "known compromised credential family": re.compile(r"(?i)\b(?:rosa\d{4}pg|redissst\d{4}|eneldov\d{4})[^\s`]*"),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode("utf-8", "surrogateescape") for item in output.split(b"\0") if item]


def is_scannable(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES


def is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("'\"").lower()
    return not normalized or any(marker in normalized for marker in PLACEHOLDER_MARKERS)


def scan() -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for path in tracked_files():
        if not is_scannable(path):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        relative = path.relative_to(ROOT).as_posix()
        for label, pattern in PATTERNS.items():
            if pattern.search(content):
                findings.append((relative, label))
        for match in ASSIGNMENT.finditer(content):
            value = match.group("value")
            if not is_placeholder(value):
                findings.append((relative, f"non-placeholder {match.group('name')}"))
    return sorted(set(findings))


def main() -> int:
    findings = scan()
    if findings:
        print("Potential secrets found in tracked files:")
        for path, category in findings:
            print(f"- {path}: {category}")
        return 1
    print("Secret scan passed for tracked Markdown and configuration files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
