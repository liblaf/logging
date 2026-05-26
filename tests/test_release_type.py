from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

import liblaf.logging.magic._release_type as release_type


@dataclasses.dataclass(frozen=True)
class FakePackagePath:
    path: Path

    def locate(self) -> Path:
        return self.path

    def read_text(self) -> str:
        msg = ".pth contents should not be inspected"
        raise AssertionError(msg)


@dataclasses.dataclass(frozen=True)
class FakeDistribution:
    version: str
    _files: list[FakePackagePath] | None = None
    fail_on_files: bool = False
    direct_url: str | None = None

    @property
    def files(self) -> list[FakePackagePath] | None:
        if self.fail_on_files:
            msg = "stable distribution files should not be indexed"
            raise AssertionError(msg)
        return self._files

    def read_text(self, filename: str) -> str | None:
        if filename == "direct_url.json":
            return self.direct_url
        return None


def test_pth_files_do_not_claim_files_from_other_distributions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    stable_file: Path = tmp_path / "site-packages" / "stable" / "module.py"
    stable_file.parent.mkdir(parents=True)
    pth_file: Path = tmp_path / "site-packages" / "pre_editable.pth"
    distributions: list[FakeDistribution] = [
        FakeDistribution(version="1.0.0", fail_on_files=True),
        FakeDistribution(
            version="1.0.0rc1",
            _files=[FakePackagePath(pth_file)],
        ),
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(stable_file) is False
    assert index.is_pre(stable_file) is False
    assert index.is_pre(pth_file) is True


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


def test_editable_distribution_source_is_development_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_root: Path = tmp_path / "project"
    source_file: Path = project_root / "src" / "package" / "module.py"
    sibling_file: Path = tmp_path / "project-sibling" / "module.py"
    editable_metadata: str = json.dumps(
        {
            "dir_info": {"editable": True},
            "url": project_root.as_uri(),
        }
    )
    distributions: list[FakeDistribution] = [
        FakeDistribution(
            version="1.0.0",
            fail_on_files=True,
            direct_url=editable_metadata,
        )
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(source_file) is True
    assert index.is_pre(source_file) is False
    assert index.is_dev(sibling_file) is False


def test_invalid_editable_direct_url_metadata_is_ignored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    distributions: list[FakeDistribution] = [
        FakeDistribution("1.0.0", direct_url="{"),
        FakeDistribution(
            "1.0.0",
            direct_url=json.dumps(
                {
                    "dir_info": {"editable": True},
                    "url": "https://example.test/project",
                }
            ),
        ),
    ]
    monkeypatch.setattr(
        release_type.importlib.metadata, "distributions", lambda: distributions
    )

    index = release_type.ReleaseTypeIndex()

    assert index.is_dev(tmp_path / "project" / "module.py") is False


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


def test_prerelease_editable_source_is_development_and_prerelease(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project_root = tmp_path / "project"
    source_file = project_root / "src" / "package" / "module.py"
    editable_metadata = json.dumps(
        {
            "dir_info": {"editable": True},
            "url": project_root.as_uri(),
        }
    )
    distributions: list[FakeDistribution] = [
        FakeDistribution(
            version="1.0.0rc1",
            _files=[],
            direct_url=editable_metadata,
        )
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
