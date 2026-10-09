"""
Unit tests for Cross-Platform Workspace Directory Resolver.
"""

import pytest
from agent_coding.fs import WorkspaceResolver, WorkspaceFolderMap


def test_workspace_resolver_get_map():
    resolver = WorkspaceResolver()
    ws_map = resolver.get_workspace_map()

    assert isinstance(ws_map, WorkspaceFolderMap)
    assert ws_map.ubuntu_home is not None
    assert ws_map.ubuntu_current is not None
    assert len(ws_map.connected_folders) >= 2


def test_list_files_in_path():
    resolver = WorkspaceResolver()
    ws_map = resolver.get_workspace_map()
    files = resolver.list_files_in_path(ws_map.ubuntu_current)

    assert isinstance(files, list)
    assert len(files) > 0
