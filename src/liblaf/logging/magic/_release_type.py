"""Detect development and prerelease files from installed distributions."""

from __future__ import annotations

import functools
import importlib.metadata
import json
import urllib.parse
import urllib.request
from importlib.metadata import Distribution
from pathlib import Path
from typing import TYPE_CHECKING

import attrs
import packaging.version
from packaging.version import InvalidVersion, Version

if TYPE_CHECKING:
    from _typeshed import StrPath


def _editable_root(distribution: Distribution) -> Path | None:
    metadata: object
    try:
        direct_url: str | None = distribution.read_text("direct_url.json")
        metadata = json.loads(direct_url) if direct_url is not None else None
    except (OSError, json.JSONDecodeError):
        metadata = None
    if not isinstance(metadata, dict):
        return None
    dir_info = metadata.get("dir_info")
    url = metadata.get("url")
    if not (
        isinstance(dir_info, dict)
        and dir_info.get("editable") is True
        and isinstance(url, str)
    ):
        return None
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "file":
        return None
    path: str = urllib.request.url2pathname(parsed.path)
    if parsed.netloc and parsed.netloc != "localhost":
        path = f"//{parsed.netloc}{path}"
    return Path(path).resolve()


@attrs.frozen
class FilesIndex:
    """Index exact files and source prefixes for release-type checks."""

    distributions: list[Distribution] = attrs.field(repr=False, factory=list)
    prefixes: list[Path] = attrs.field(repr=False, factory=list)

    def add(self, distribution: Distribution) -> None:
        """Index files from `distribution` lazily."""
        self.distributions.append(distribution)

    def add_prefix(self, prefix: StrPath) -> None:
        """Mark every file below `prefix` as indexed."""
        self.prefixes.append(Path(prefix).resolve())

    _cache: dict[str, bool] = attrs.field(repr=False, factory=dict)

    def has(self, name: StrPath) -> bool:
        """Return whether `name` is part of the index."""
        path = Path(name).resolve()
        key = str(path)
        if key not in self._cache:
            self._cache[key] = self._has(path)
        return self._cache[key]

    def _has(self, path: Path) -> bool:
        if str(path) in self.files:
            return True
        return any(path.is_relative_to(prefix) for prefix in self.prefixes)

    @functools.cached_property
    def files(self) -> frozenset[str]:
        files: list[str] = []
        for distribution in self.distributions:
            distribution_files = distribution.files
            if not distribution_files:
                continue
            files.extend(
                str(Path(file.locate()).resolve()) for file in distribution_files
            )
        return frozenset(files)


@attrs.frozen
class ReleaseTypeIndex:
    """Classify files as development or prerelease code."""

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
            editable_root: Path | None = _editable_root(distribution)
            if editable_root is not None:
                dev_index.add_prefix(editable_root)
            try:
                version: Version = packaging.version.parse(distribution.version)
            except InvalidVersion:
                continue
            if version.is_devrelease:
                dev_index.add(distribution)
            if version.is_prerelease:
                pre_index.add(distribution)
                if editable_root is not None:
                    pre_index.add_prefix(editable_root)
        return dev_index, pre_index


_release_type_index = ReleaseTypeIndex()


def is_dev_release(file: StrPath | None = None, name: str | None = None) -> bool:
    """Return whether `file` should use development logging defaults."""
    return _release_type_index.is_dev(file, name)


def is_pre_release(file: StrPath | None = None, name: str | None = None) -> bool:
    """Return whether `file` should use prerelease logging defaults."""
    return _release_type_index.is_pre(file, name)
