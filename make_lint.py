"""
Linting and code formatting module for Fireflies Meeting Fetcher

This module provides utilities to format and lint all Python code in the project
according to Python best practices and PEP 8 standards.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class LintFormatter:
    """
    A class to handle code linting and formatting operations.

    This class provides methods to format Python code using black, isort, and flake8
    to ensure consistent code style and quality across the project.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the LintFormatter.

        Args:
            project_root: Root directory of the project (defaults to current directory)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.python_files = self._find_python_files()

    def _find_python_files(self) -> List[Path]:
        """
        Find all Python files in the project.

        Returns:
            List of Python file paths
        """
        python_files = []
        for file_path in self.project_root.rglob("*.py"):
            # Skip __pycache__ directories and virtual environments
            if "__pycache__" not in str(file_path) and "venv" not in str(file_path):
                python_files.append(file_path)
        return python_files

    def _run_command(self, command: List[str], description: str) -> bool:
        """
        Run a shell command and return success status.

        Args:
            command: Command to run as a list of strings
            description: Description of what the command does

        Returns:
            True if command succeeded, False otherwise
        """
        print(f"Running {description}...")
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed with exit code {e.returncode}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ Command not found. Please install the required tool.")
            return False

    def format_with_black(self, check_only: bool = False) -> bool:
        """
        Format code using black formatter.

        Args:
            check_only: If True, only check formatting without making changes

        Returns:
            True if formatting succeeded or code is already formatted
        """
        command = ["black", "--line-length", "88"]
        if check_only:
            command.append("--check")
        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "Black code formatting")

    def sort_imports_with_isort(self, check_only: bool = False) -> bool:
        """
        Sort imports using isort.

        Args:
            check_only: If True, only check import order without making changes

        Returns:
            True if import sorting succeeded or imports are already sorted
        """
        command = ["isort", "--profile", "black"]
        if check_only:
            command.append("--check-only")
        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "Import sorting with isort")

    def lint_with_flake8(self) -> bool:
        """
        Lint code using flake8.

        Returns:
            True if linting passed without errors
        """
        command = [
            "flake8",
            "--max-line-length=88",
            "--extend-ignore=E203,W503,E501",  # Compatible with black
            "--exclude=venv,__pycache__,.git",
        ]
        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "Code linting with flake8")

    def lint_with_pylint(self) -> bool:
        """
        Lint code using pylint for more comprehensive analysis.

        Returns:
            True if linting passed without critical errors
        """
        command = [
            "pylint",
            "--disable=C0114,C0116",  # Disable docstring warnings
            "--max-line-length=88",
        ]
        command.extend([str(f) for f in self.python_files])

        return self._run_command(command, "Code analysis with pylint")

    def run_all_formatting(self, check_only: bool = False) -> bool:
        """
        Run all formatting and linting operations.

        Args:
            check_only: If True, only check formatting without making changes

        Returns:
            True if all operations succeeded
        """
        print(f"🔍 Formatting and linting {len(self.python_files)} Python files...")
        print(f"Project root: {self.project_root}")
        print(f"Files to process: {[f.name for f in self.python_files]}")
        print("-" * 50)

        success = True

        # Sort imports first
        if not self.sort_imports_with_isort(check_only):
            success = False

        # Format code with black
        if not self.format_with_black(check_only):
            success = False

        # Lint with flake8 (only if not in check-only mode)
        if not check_only:
            if not self.lint_with_flake8():
                success = False

        print("-" * 50)
        if success:
            print("✅ All formatting and linting operations completed successfully!")
        else:
            print("❌ Some formatting or linting operations failed.")
            print("Please review the output above and fix any issues.")

        return success

    def install_dependencies(self) -> bool:
        """
        Install required linting and formatting dependencies.

        Returns:
            True if all dependencies were installed successfully
        """
        dependencies = [
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
        ]

        print("Installing linting and formatting dependencies...")
        for dep in dependencies:
            command = [sys.executable, "-m", "pip", "install", dep]
            if not self._run_command(command, f"Installing {dep}"):
                return False

        print("✅ All dependencies installed successfully!")
        return True


def main():
    """
    Main function to run linting and formatting operations.

    This function can be called from the command line to format all code in the project.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Format and lint Python code")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check formatting without making changes",
    )
    parser.add_argument(
        "--install-deps", action="store_true", help="Install required dependencies"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        help="Project root directory (defaults to current directory)",
    )

    args = parser.parse_args()

    formatter = LintFormatter(args.project_root)

    if args.install_deps:
        success = formatter.install_dependencies()
        sys.exit(0 if success else 1)

    success = formatter.run_all_formatting(args.check_only)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
