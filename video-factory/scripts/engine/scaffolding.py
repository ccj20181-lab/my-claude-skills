import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, Any

class Scaffolder:
    def __init__(self, output_path: Path):
        self.output_path = output_path

    def create_project(self, project_name: str) -> Path:
        """
        Creates a new Remotion project using npx create-video.
        """
        if self.output_path.exists():
            print(f"⚠️  Directory already exists: {self.output_path}")
        else:
            self.output_path.mkdir(parents=True, exist_ok=True)

        print(f"📦 Creating Remotion project: {project_name} at {self.output_path}")

        try:
            # Check if npx is available
            subprocess.run(["npx", "--version"], check=True, capture_output=True)

            # We use 'blank' template to minimize bloat
            # create-video expects the directory to be empty or we pass the dir.
            # We will run it in the parent dir with the project name.

            cmd = ["npx", "create-video@latest", project_name, "--template", "blank", "--quiet"]

            # Only run if package.json doesn't exist
            if not (self.output_path / "package.json").exists():
                 subprocess.run(
                    cmd,
                    cwd=self.output_path.parent,
                    check=True
                )

            # Verify if package.json was actually created
            if not (self.output_path / "package.json").exists():
                print("⚠️  npx create-video finished but package.json is missing.")
                raise FileNotFoundError("npx create-video failed to create package.json")

            print("✅ Remotion project scaffolding complete.")

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️  npx create-video failed or npx not found: {e}")
            print("📝 Falling back to manual structure creation...")
            self._create_manual_structure(project_name)

        return self.output_path

    def _create_manual_structure(self, project_name: str):
        """Manually creates the minimal Remotion structure if npx fails."""
        self.output_path.mkdir(parents=True, exist_ok=True)

        package_json = {
            "name": project_name,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "start": "remotion studio",
                "build": "remotion render src/index.ts MyVideo out/video.mp4",
                "preview": "remotion preview"
            },
            "dependencies": {
                "@remotion/cli": "^4.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "remotion": "^4.0.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "typescript": "^5.0.0"
            }
        }

        with open(self.output_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # Basic tsconfig
        tsconfig = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "ESNext",
                "moduleResolution": "bundler",
                "jsx": "react-jsx",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "outDir": "dist"
            },
            "include": ["src/**/*"]
        }
        with open(self.output_path / "tsconfig.json", "w") as f:
            json.dump(tsconfig, f, indent=2)

        # Create minimal .gitignore
        with open(self.output_path / ".gitignore", "w") as f:
            f.write("node_modules\ndist\nout\n.env\n")

    def install_template_files(self, react_files: Dict[str, str]):
        """
        Writes the template-specific React files to src/.
        """
        src_path = self.output_path / "src"
        src_path.mkdir(exist_ok=True)

        for filename, content in react_files.items():
            file_path = src_path / filename
            # Ensure subdirectory exists if filename contains paths
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"✅ Installed {len(react_files)} template files to src/")

    def setup_config(self, width=1080, height=1440, fps=30):
        """
        Creates remotion.config.ts.
        """
        config_content = f"""
import {{ Config }} from "@remotion/cli/config";

Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);

export const videoConfig = {{
  width: {width},
  height: {height},
  fps: {fps},
}};
"""
        with open(self.output_path / "remotion.config.ts", "w") as f:
            f.write(config_content)
