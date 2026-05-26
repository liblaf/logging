"""Detect development and prerelease files from installed distributions."""

from __future__ import annotations

import functools
import importlib.metadata
import os
from collections.abc import Generator
from importlib.metadata import Distribution
from pathlib import Path
from typing import TYPE_CHECKING

import attrs
import packaging.version
from packaging.version import InvalidVersion, Version

if TYPE_CHECKING:
    from _typeshed import StrPath


def _parse_pth(file: StrPath) -> Generator[str]:
    file: Path = Path(file)
    parent: Path = file.parent
    with file.open() as fp:
        for line_ in fp:
            line: str = line_.strip()
            if line and not line.startswith(("#", "import ", "import\t")):
                yield os.path.abspath(parent / line)  # noqa: PTH100


@attrs.frozen
class FilesIndex:
    """Index exact files and `.pth` source prefixes for release-type checks.

    Distribution metadata is read lazily, so stable distributions that do not
    affect the requested release type never pay the cost of expanding their file
    lists. A selected distribution's `.pth` files contribute source prefixes, so
    editable-style source trees can share that selected release classification
    without following installer-specific `direct_url.json` metadata.
    """

    distributions: list[Distribution] = attrs.field(repr=False, factory=list)

    def add(self, distribution: Distribution) -> None:
        """Index files from `distribution` lazily."""
        self.distributions.append(distribution)

    _cache: dict[str, bool] = attrs.field(repr=False, factory=dict)

    def has(self, file: StrPath) -> bool:
        """Return whether `file` is part of the index."""
        file: str = os.fsdecode(file)
        if file not in self._cache:
            self._cache[file] = self._has(file)
        return self._cache[file]

    def _has(self, file: str) -> bool:
        file: str = os.path.abspath(file)  # noqa: PTH100
        if file in self._files:
            return True
        return file.startswith(self._prefixes)

    @functools.cached_property
    def _files(self) -> frozenset[str]:
        files, _prefixes = self._files_prefixes
        return frozenset(files)

    @functools.cached_property
    def _prefixes(self) -> tuple[str, ...]:
        _files, prefixes = self._files_prefixes
        return tuple(prefix + os.sep for prefix in prefixes)

    @functools.cached_property
    def _files_prefixes(self) -> tuple[list[str], list[str]]:
        files: list[str] = []
        prefixes: list[str] = []
        for distribution in self.distributions:
            distribution_files = distribution.files
            if not distribution_files:
                continue
            for file in distribution_files:
                if file.suffix == ".pth":
                    prefixes.extend(_parse_pth(file.locate()))
                else:
                    files.append(os.path.abspath(file.locate()))  # noqa: PTH100
        return files, prefixes


@attrs.frozen
class ReleaseTypeIndex:
    """Classify files from selected installed distributions.

    `.devN` distributions are treated as development code. Prerelease
    distributions such as `a`, `b`, and `rc` releases are treated as prerelease
    code. Exact files and `.pth` source prefixes are taken only from those
    selected distributions; stable distribution metadata and `direct_url.json`
    are not followed. The `__main__` module is always classified as both so
    scripts get verbose defaults while they are being run directly.
    """

    def is_dev(self, file: StrPath | None = None, name: str | None = None) -> bool:
        """Return whether `file` belongs to development code."""
        if name == "__main__":
            return True
        return file is not None and self._dev_index.has(file)

    def is_pre(self, file: StrPath | None = None, name: str | None = None) -> bool:
        """Return whether `file` belongs to prerelease code."""
        if name == "__main__":
            return True
        return file is not None and self._pre_index.has(file)

    @functools.cached_property
    def _dev_index(self) -> FilesIndex:
        dev_index, _ = self._indexes
        return dev_index

    @functools.cached_property
    def _pre_index(self) -> FilesIndex:
        _, pre_index = self._indexes
        return pre_index

    @functools.cached_property
    def _indexes(self) -> tuple[FilesIndex, FilesIndex]:
        dev_index = FilesIndex()
        pre_index = FilesIndex()
        for distribution in importlib.metadata.distributions():
            try:
                version: Version = packaging.version.parse(distribution.version)
            except InvalidVersion:
                continue
            if version.is_devrelease:
                dev_index.add(distribution)
            if version.is_prerelease:
                pre_index.add(distribution)
        return dev_index, pre_index


_release_type_index = ReleaseTypeIndex()


def is_dev_release(file: StrPath | None = None, name: str | None = None) -> bool:
    """Return whether `file` should use development logging defaults.

    The `__main__` module is always treated as development code so directly
    executed scripts get the most verbose defaults.

    Examples:
        >>> is_dev_release(name="__main__")
        True
    """
    return _release_type_index.is_dev(file, name)


def is_pre_release(file: StrPath | None = None, name: str | None = None) -> bool:
    """Return whether `file` should use prerelease logging defaults.

    Examples:
        >>> is_pre_release(name="__main__")
        True
    """
    return _release_type_index.is_pre(file, name)
