"""Tests the LocalDataStore."""

from insights_engine.data_store.local_filesystem import LocalFileSystem


def test_local_datastore():
    """Tests local datastore object and name."""
    local_obj = LocalFileSystem("/tmp")
    assert local_obj is not None
    assert local_obj.get_name() == "Local filesytem dir: /tmp"
