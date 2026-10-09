import type { WorkspaceConfig } from '../types/index.ts';
import * as path from 'path';

export class WorkspaceManager {
  private config: WorkspaceConfig;

  constructor(baseDir: string = process.cwd()) {
    this.config = {
      currentDir: path.resolve(baseDir),
      linkedDirs: []
    };
    this.resolveCrossPlatformPaths();
  }

  public resolveCrossPlatformPaths(): WorkspaceConfig {
    const cwd = this.config.currentDir;

    // Detect Windows WSL or mapped paths
    if (cwd.startsWith('/mnt/c/') || cwd.startsWith('/mnt/d/')) {
      const drive = cwd.substring(5, 6).toUpperCase();
      const rest = cwd.substring(7).replace(/\//g, '\\');
      this.config.windowsPath = `${drive}:\\${rest}`;
      this.config.ubuntuPath = cwd;
    } else if (/^[A-Za-z]:\\/.test(cwd)) {
      const drive = cwd.substring(0, 1).toLowerCase();
      const rest = cwd.substring(3).replace(/\\/g, '/');
      this.config.windowsPath = cwd;
      this.config.ubuntuPath = `/mnt/${drive}/${rest}`;
    } else {
      this.config.ubuntuPath = cwd;
      this.config.windowsPath = `C:\\Users\\workspace\\${path.basename(cwd)}`;
    }

    return this.config;
  }

  public getConfig(): WorkspaceConfig {
    return this.config;
  }
}
