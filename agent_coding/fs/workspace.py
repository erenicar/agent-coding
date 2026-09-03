"""
Cross-Platform File System & Workspace Resolver.
Detects, maps, and links Windows directories (e.g. WSL /mnt/c/Users, C:\\Users) and Ubuntu/Linux directories (/home, /app).
"""

import os
import sys
import platform
from pathlib import Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class DirectoryNode(BaseModel):
    name: str
    path: str
    is_dir: bool
    platform_origin: str  # "Ubuntu/Linux" or "Windows"


class WorkspaceFolderMap(BaseModel):
    ubuntu_home: str
    ubuntu_current: str
    windows_users_path: Optional[str] = None
    connected_folders: List[DirectoryNode] = []


class WorkspaceResolver:
    """
    Resolves and links Windows and Ubuntu workspace folders for agents and Web UI.
    """
    def __init__(self):
        self.system = platform.system()

    def detect_windows_paths(self) -> Optional[str]:
        """
        Detects Windows user directories when running on WSL/Linux or native Windows.
        """
        # 1. Check WSL mount paths
        wsl_c_users = Path("/mnt/c/Users")
        if wsl_c_users.exists():
            return str(wsl_c_users)

        wsl_d_users = Path("/mnt/d")
        if wsl_d_users.exists():
            return str(wsl_d_users)

        # 2. Check Windows environment variables
        user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        if user_profile and ("Users" in user_profile or ":\\" in user_profile):
            return user_profile

        return None

    def get_workspace_map(self) -> WorkspaceFolderMap:
        ubuntu_home = str(Path.home().resolve())
        ubuntu_current = str(Path.cwd().resolve())
        win_path = self.detect_windows_paths()

        connected = [
            DirectoryNode(name="Ubuntu Home", path=ubuntu_home, is_dir=True, platform_origin="Ubuntu/Linux"),
            DirectoryNode(name="Current Workspace", path=ubuntu_current, is_dir=True, platform_origin="Ubuntu/Linux"),
        ]

        if win_path:
            connected.append(
                DirectoryNode(name="Windows Users Drive", path=win_path, is_dir=True, platform_origin="Windows")
            )

        return WorkspaceFolderMap(
            ubuntu_home=ubuntu_home,
            ubuntu_current=ubuntu_current,
            windows_users_path=win_path,
            connected_folders=connected
        )

    def list_files_in_path(self, target_path: str) -> List[DirectoryNode]:
        p = Path(target_path)
        if not p.exists() or not p.is_dir():
            return []

        nodes = []
        try:
            for item in p.iterdir():
                if item.name.startswith("."):
                    continue  # skip hidden
                origin = "Windows" if "/mnt/c" in str(item) or "C:\\" in str(item) else "Ubuntu/Linux"
                nodes.append(
                    DirectoryNode(
                        name=item.name,
                        path=str(item.resolve()),
                        is_dir=item.is_dir(),
                        platform_origin=origin
                    )
                )
        except PermissionError:
            pass

        return sorted(nodes, key=lambda x: (not x.is_dir, x.name.lower()))
