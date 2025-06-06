from kedro.io import AbstractVersionedDataset
import pickle
import fsspec
from kedro.io.core import get_filepath_str, get_protocol_and_path
from pathlib import Path


class OptionalPickleDataset(AbstractVersionedDataset):
    """Custom dataset that prevents an error to raise if there is no model on s3 yet."""
    def __init__(self, filepath, version=None, credentials=None, load_args=None, save_args=None):
        self._filepath = filepath
        self._credentials = credentials or {}
        self._protocol, self._path = get_protocol_and_path(filepath, version)
        self._fs = fsspec.filesystem(self._protocol, **self._credentials)

        self._load_args = load_args or {}
        self._save_args = save_args or {}

        super().__init__(filepath=filepath, version=version)

    def _load(self):
        load_path = get_filepath_str(self._get_load_path(), self._protocol)
        try:
            with self._fs.open(load_path, mode="rb") as f:
                return pickle.load(f, **self._load_args)
        except FileNotFoundError:
            return None

    def _save(self, data) -> None:
        save_path = get_filepath_str(self._get_save_path(), self._protocol)
        with self._fs.open(save_path, mode="wb") as f:
            pickle.dump(data, f, **self._save_args)

    def _get_load_path(self) -> Path:
        if self._version and self._version.load:
            return Path(self._path) / self._version.load
        return Path(self._path)

    def _get_save_path(self) -> Path:
        if self._version and self._version.save:
            return Path(self._path) / self._version.save
        return Path(self._path)

    def _describe(self):
        return {
            "filepath": self._filepath,
            "version": self._version,
            "protocol": self._protocol,
        }