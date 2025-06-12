from kedro.io import AbstractVersionedDataset
import pickle
import fsspec
from kedro.io.core import get_filepath_str, get_protocol_and_path
from pathlib import PurePosixPath
from typing import Any


class OptionalPickleDataset(AbstractVersionedDataset):
    """Custom PickleDataset that does not fail if file is missing."""

    def __init__(
        self,
        filepath: str,
        version=None,
        credentials: dict = None,
        load_args: dict = None,
        save_args: dict = None,
    ):
        # Kedro internally expects a Path-like object here
        self._filepath = PurePosixPath(filepath)
        self._protocol, self._path = get_protocol_and_path(filepath, version)
        self._credentials = credentials or {}
        self._fs = fsspec.filesystem(self._protocol, **self._credentials)

        self._load_args = load_args or {}
        self._save_args = save_args or {}

        super().__init__(filepath=self._filepath, version=version)

    def _load(self) -> Any:
        load_path = self._get_load_path()
        try:
            with self._fs.open(load_path, mode="rb") as f:
                return pickle.load(f, **self._load_args)
        except (FileNotFoundError, EOFError):
            return None

    def _save(self, data: Any) -> None:
        save_path = self._get_save_path()
        with self._fs.open(save_path, mode="wb") as f:
            pickle.dump(data, f, **self._save_args)

    def _get_load_path(self) -> str:
        if self._version and self._version.load:
            return f"{self._path}/{self._version.load}/{self._filepath.name}"
        return str(self._path)

    def _get_save_path(self) -> str:
        if self._version and self._version.save:
            return f"{self._path}/{self._version.save}/{self._filepath.name}"
        return str(self._path)

    def _get_versioned_path(self, version: str) -> PurePosixPath:
        # Required for Kedro to compute versioned save/load directories
        return PurePosixPath(self._filepath) / version / self._filepath.name

    def _describe(self) -> dict:
        return {
            "filepath": str(self._filepath),
            "version": self._version,
            "protocol": self._protocol,
        }
