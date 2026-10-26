import re
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "visualization"
SKILL_MD = SKILL_DIR / "SKILL.md"
PATTERNS_MD = SKILL_DIR / "references" / "chart-patterns.md"

CODE_BLOCK = re.compile(r"^```python\n(.*?)^```", re.S | re.M)
HEADING = re.compile(r"^#{2,3} (.+)$", re.M)


def split_frontmatter(text):
    """Return (frontmatter_yaml, body) from a Markdown file that starts with a '---' block."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        raise ValueError("SKILL.md does not start with a '---' YAML frontmatter block")
    return match.group(1), match.group(2)


def preamble_code():
    """The style preamble: the first Python block in SKILL.md that defines get_layout."""
    for block in CODE_BLOCK.findall(SKILL_MD.read_text()):
        if "def get_layout" in block:
            return block
    raise ValueError("No preamble (def get_layout) found in SKILL.md")


def pattern_blocks():
    """Every Python block in chart-patterns.md, keyed by the nearest heading above it."""
    text = PATTERNS_MD.read_text()
    headings = [(m.start(), m.group(1).strip()) for m in HEADING.finditer(text)]
    blocks = {}
    for match in CODE_BLOCK.finditer(text):
        heading = [title for pos, title in headings if pos < match.start()][-1]
        assert heading not in blocks, f"Two code blocks under '{heading}'; give each its own heading"
        blocks[heading] = match.group(1)
    return blocks


@pytest.fixture
def preamble_ns():
    """A fresh namespace with the SKILL.md preamble executed in it."""
    ns = {}
    exec(preamble_code(), ns)
    return ns
