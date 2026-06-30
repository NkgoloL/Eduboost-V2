"""Semantic versioning utility for POPIA consent version management.

Implements MAJOR.MINOR.PATCH version comparison and migration detection.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VersionChangeType(Enum):
    """Type of version change for consent migration."""
    PATCH = "patch"  # 1.0.0 -> 1.0.1: Auto-renewal
    MINOR = "minor"  # 1.0.0 -> 1.1.0: Manual renewal required
    MAJOR = "major"  # 1.0.0 -> 2.0.0: Manual renewal required


@dataclass(frozen=True)
class SemanticVersion:
    """Semantic version (MAJOR.MINOR.PATCH)."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version_string: str) -> SemanticVersion:
        """Parse version string like '1.0.0' into SemanticVersion."""
        parts = version_string.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_string}. Expected MAJOR.MINOR.PATCH")
        try:
            return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))
        except ValueError as e:
            raise ValueError(f"Invalid version numbers in: {version_string}") from e

    def __str__(self) -> str:
        """Return version string representation."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def compare(self, other: SemanticVersion) -> int:
        """Compare versions. Returns -1 if self < other, 0 if equal, 1 if self > other."""
        if self.major != other.major:
            return -1 if self.major < other.major else 1
        if self.minor != other.minor:
            return -1 if self.minor < other.minor else 1
        if self.patch != other.patch:
            return -1 if self.patch < other.patch else 1
        return 0

    def __lt__(self, other: SemanticVersion) -> bool:
        return self.compare(other) < 0

    def __le__(self, other: SemanticVersion) -> bool:
        return self.compare(other) <= 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self.compare(other) == 0

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self.compare(other) != 0

    def __gt__(self, other: SemanticVersion) -> bool:
        return self.compare(other) > 0

    def __ge__(self, other: SemanticVersion) -> bool:
        return self.compare(other) >= 0

    def detect_change_type(self, other: SemanticVersion) -> VersionChangeType:
        """Detect the type of version change from self to other."""
        if self.major != other.major:
            return VersionChangeType.MAJOR
        if self.minor != other.minor:
            return VersionChangeType.MINOR
        return VersionChangeType.PATCH


def detect_version_change(current_version: str, new_version: str) -> VersionChangeType:
    """Detect the type of version change between two version strings."""
    current = SemanticVersion.parse(current_version)
    new = SemanticVersion.parse(new_version)
    return current.detect_change_type(new)


def requires_manual_renewal(current_version: str, new_version: str) -> bool:
    """Check if version change requires manual renewal (MAJOR or MINOR)."""
    change_type = detect_version_change(current_version, new_version)
    return change_type in {VersionChangeType.MAJOR, VersionChangeType.MINOR}


def is_same_major_minor(current_version: str, new_version: str) -> bool:
    """Check if versions have same MAJOR.MINOR (PATCH changes only)."""
    current = SemanticVersion.parse(current_version)
    new = SemanticVersion.parse(new_version)
    return current.major == new.major and current.minor == new.minor
