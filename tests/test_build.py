import os
import shutil
from pathlib import Path

from click.testing import CliRunner, Result
from mkdocs.__main__ import build_command


def setup_clean_mkdocs_folder(input_path: Path, output_path: Path) -> Path:
    """
    Sets up a clean MkDocs folder for testing.

    Args:
        input_path (Path): Path to the input MkDocs project directory.
        output_path (Path): Path to the output MkDocs project directory.

    Returns:
        Path: The path to the temporary MkDocs directory.
    """
    tmp_project_path = output_path / input_path.name
    if tmp_project_path.exists():
        shutil.rmtree(tmp_project_path)
    shutil.copytree(input_path, tmp_project_path)
    return tmp_project_path


def build_docs_setup(project_path: Path) -> Result:
    """
    Builds the MkDocs documentation for the given project path.

    Args:
        project_path (Path): Path to the MkDocs project directory.

    Returns:
        Result: The result of the MkDocs build command.
    """

    cwd = os.getcwd()
    os.chdir(project_path)

    try:
        runner = CliRunner()
        return runner.invoke(build_command, [])
    except:
        raise
    finally:
        os.chdir(cwd)


def test_basic_setup(tmp_path: Path) -> None:
    """
    Test the basic setup of the MkDocs SQLAlchemy plugin.

    This test sets up a simple MkDocs project with a single model file
    and verifies that the documentation is generated correctly.
    """
    # Setup a clean MkDocs folder
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/basic_setup"), tmp_path
    )

    # Build the documentation
    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    # Verify the output
    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text()
    assert "users" in content, "User model not documented."
    assert "posts" in content, "Post model not documented."
    assert "user_profiles" in content, "UserProfile model not documented."
