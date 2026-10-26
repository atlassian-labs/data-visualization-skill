"""SKILL.md frontmatter follows the Agent Skills spec: https://agentskills.io/specification

Mirrors the checks in the reference validator (skills-ref validate).
"""
import re

import pytest
import yaml

from conftest import SKILL_DIR, SKILL_MD, split_frontmatter

ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


@pytest.fixture(scope="module")
def frontmatter():
    raw, _ = split_frontmatter(SKILL_MD.read_text())
    data = yaml.safe_load(raw)
    assert isinstance(data, dict), "Frontmatter must be a YAML mapping"
    return data


def test_only_spec_fields(frontmatter):
    extra = set(frontmatter) - ALLOWED_FIELDS
    assert not extra, f"Fields not in the Agent Skills spec: {sorted(extra)}"


def test_name(frontmatter):
    name = frontmatter.get("name")
    assert isinstance(name, str) and 1 <= len(name) <= 64
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name), (
        "name must be lowercase letters, digits and single hyphens, not starting or ending with a hyphen"
    )
    assert name == SKILL_DIR.name, "name must match the skill's directory name"


def test_description(frontmatter):
    description = frontmatter.get("description")
    assert isinstance(description, str) and description.strip()
    assert len(description) <= 1024


def test_compatibility(frontmatter):
    if "compatibility" in frontmatter:
        compatibility = frontmatter["compatibility"]
        assert isinstance(compatibility, str) and 1 <= len(compatibility) <= 500


def test_metadata_is_string_map(frontmatter):
    metadata = frontmatter.get("metadata", {})
    assert isinstance(metadata, dict)
    for key, value in metadata.items():
        assert isinstance(key, str) and isinstance(value, str), (
            f"metadata.{key} must be a string (quote it in YAML), got {type(value).__name__}"
        )


def test_allowed_tools(frontmatter):
    if "allowed-tools" in frontmatter:
        assert isinstance(frontmatter["allowed-tools"], str)
