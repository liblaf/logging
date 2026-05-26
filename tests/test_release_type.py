from __future__ import annotations

import dataclasses
from importlib.metadata import Distribution
from pathlib import Path
from typing import cast

import pytest

import liblaf.logging.magic._release_type as release_type


@dataclasses.dataclass(frozen=True)
class FakePackagePath:
    path: Path

    @property
    def suffix(self) -> str:
        return self.path.suffix

    def locate(self) -> Path:
        return self.path


@dataclasses.dataclass(frozen=True)
class FakeDistribution:
    version: str
    _files: list[FakePackagePath] | None = None
    fail_on_files: bool = False

    @property
    def files(self) -> list[FakePackagePath] | None:
        if self.fail_on_files:
            msg = "stable distribution files should not be indexed"
            raise AssertionError(msg)
        return self._files

    def read_text(self, filename: str) -> str | None:
        msg = f"{filename} should not be inspected"
        raise AssertionError(msg)


@dataclasses.dataclass
class CountingDistribution:
    file: Path
    calls: int = 0

    @property
    def files(self) -> list[FakePackagePath]:
        self.calls += 1
        return [FakePackagePath(self.file)]


def test_main_module_is_development_script(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    installed_file: Path = tmp_path / "site-packages" / "stable.py"
    distributions: list[FakeDistribution] = [
        FakeDistribution(version="1.0.0", fail_on_files=True)
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(installed_file) is False
    assert index.is_pre(installed_file) is False
    assert index.is_dev(installed_file, name="__main__") is True
    assert index.is_pre(installed_file, name="__main__") is True


def test_stable_distribution_files_are_not_indexed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source_file: Path = tmp_path / "site-packages" / "package" / "module.py"
    distributions: list[FakeDistribution] = [
        FakeDistribution(version="1.0.0", fail_on_files=True)
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is False
    assert index.is_pre(source_file) is False


def test_direct_url_metadata_is_not_followed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_root: Path = tmp_path / "project"
    source_file: Path = project_root / "src" / "package" / "module.py"
    distributions: list[FakeDistribution] = [
        FakeDistribution(version="1.0.0", fail_on_files=True)
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is False
    assert index.is_pre(source_file) is False


def test_development_distribution_indexes_exact_files_as_dev_and_pre(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source_file = tmp_path / "site-packages" / "package" / "module.py"
    source_file.parent.mkdir(parents=True)
    distributions: list[FakeDistribution] = [
        FakeDistribution(
            version="1.0.0.dev1",
            _files=[FakePackagePath(source_file)],
        ),
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is True
    assert index.is_pre(source_file) is True


def test_prerelease_distribution_indexes_exact_files_as_pre_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source_file = tmp_path / "site-packages" / "package" / "module.py"
    source_file.parent.mkdir(parents=True)
    distributions: list[FakeDistribution] = [
        FakeDistribution(
            version="1.0.0rc1",
            _files=[FakePackagePath(source_file)],
        ),
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is False
    assert index.is_pre(source_file) is True


def test_prerelease_pth_prefix_indexes_source_tree_as_pre_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    site_packages = tmp_path / "site-packages"
    project_root = site_packages / "checkout"
    source_file = project_root / "src" / "package" / "module.py"
    sibling_file = site_packages / "checkout-sibling" / "module.py"
    pth_file = site_packages / "pre_editable.pth"
    pth_file.parent.mkdir(parents=True)
    pth_file.write_text("# ignored comment\nimport generated_bootstrap\ncheckout/src\n")
    distributions: list[FakeDistribution] = [
        FakeDistribution(version="1.0.0", fail_on_files=True),
        FakeDistribution(version="1.0.0rc1", _files=[FakePackagePath(pth_file)]),
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is False
    assert index.is_pre(source_file) is True
    assert index.is_pre(sibling_file) is False


def test_development_pth_prefix_indexes_source_tree_as_dev_and_pre(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    site_packages = tmp_path / "site-packages"
    source_file = tmp_path / "checkout" / "src" / "package" / "module.py"
    pth_file = site_packages / "dev_editable.pth"
    pth_file.parent.mkdir(parents=True)
    pth_file.write_text("../checkout/src\n")
    distributions: list[FakeDistribution] = [
        FakeDistribution(version="1.0.0.dev1", _files=[FakePackagePath(pth_file)]),
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is True
    assert index.is_pre(source_file) is True


def test_invalid_distribution_version_is_ignored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source_file = tmp_path / "site-packages" / "package" / "module.py"
    source_file.parent.mkdir(parents=True)
    distributions: list[FakeDistribution] = [
        FakeDistribution(
            version="not-a-version",
            _files=[FakePackagePath(source_file)],
        )
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is False
    assert index.is_pre(source_file) is False


def test_files_index_caches_path_membership(tmp_path: Path) -> None:
    source_file = tmp_path / "site-packages" / "package" / "module.py"
    source_file.parent.mkdir(parents=True)
    distribution = CountingDistribution(source_file)
    index = release_type.FilesIndex(distributions=[cast("Distribution", distribution)])

    assert index.has(source_file) is True
    assert index.has(source_file) is True
    assert distribution.calls == 1


def test_release_type_helpers_delegate_to_global_index(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, object, str | None]] = []

    class FakeIndex:
        def is_dev(self, file: object = None, name: str | None = None) -> bool:
            calls.append(("dev", file, name))
            return True

        def is_pre(self, file: object = None, name: str | None = None) -> bool:
            calls.append(("pre", file, name))
            return False

    monkeypatch.setattr(release_type, "_release_type_index", FakeIndex())

    assert release_type.is_dev_release("module.py", "package.module") is True
    assert release_type.is_pre_release("module.py", "package.module") is False
    assert calls == [
        ("dev", "module.py", "package.module"),
        ("pre", "module.py", "package.module"),
    ]
