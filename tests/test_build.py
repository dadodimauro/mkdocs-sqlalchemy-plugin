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

    content = models_page.read_text(encoding="utf-8")
    assert "users" in content, "User model not documented."
    assert "posts" in content, "Post model not documented."
    assert "user_profiles" in content, "UserProfile model not documented."


def test_filter_fields(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/filter_fields"), tmp_path
    )

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"

    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    user_page = output_dir / "users/index.html"
    assert user_page.exists(), "User page was not generated."

    content = user_page.read_text(encoding="utf-8")
    assert "column" in content, "Column 'column' should be documented."
    assert "type" in content, "Column 'type' should be documented."
    assert "nullable" in content, "Column 'nullable' should be documented."
    assert "default" not in content, "Column 'default' should not be documented."

    post_page = output_dir / "posts/index.html"
    assert post_page.exists(), "Post page was not generated."

    content = post_page.read_text(encoding="utf-8")
    assert "column" in content, "Column 'column' should be documented."
    assert "unique" in content, "Column 'unique' should be documented."
    assert "nullable" not in content, "Column 'nullable' should not be documented."


def test_single_tables(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/single_tables"), tmp_path
    )

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"

    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    user_page = output_dir / "users/index.html"
    assert user_page.exists(), "User page was not generated."

    content = user_page.read_text(encoding="utf-8")
    assert "users" in content, "User table not documented."

    post_page = output_dir / "posts/index.html"
    assert post_page.exists(), "Post page was not generated."

    content = post_page.read_text(encoding="utf-8")
    assert "posts" in content, "Post table not documented."


def test_table_not_found(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/table_not_found"), tmp_path
    )

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"

    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert "<!-- Table 'not-found' not found -->" in content, (
        "Expected 'not found' comment"
    )


def test_table_style(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/table_style"), tmp_path
    )

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"

    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    user_page = output_dir / "users/index.html"
    assert user_page.exists(), "User page was not generated."

    content = user_page.read_text(encoding="utf-8")
    assert 'style="text-align: left;"' in content, (
        "Expected text alignment style not found"
    )
    assert '<h2 id="table-users">Table: <code>users</code></h2>' in content, (
        "Expected heading level h2 not found"
    )

    post_page = output_dir / "posts/index.html"
    assert post_page.exists(), "Post page was not generated."

    content = post_page.read_text(encoding="utf-8")
    assert 'style="text-align: center;"' in content, (
        "Expected text alignment style not found"
    )
    assert '<h3 id="table-posts">Table: <code>posts</code></h3>' in content, (
        "Expected heading level h3 not found"
    )


def test_theme(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(Path("tests/fixtures/theme"), tmp_path)

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert "users" in content, "User model not documented."
    assert "posts" in content, "Post model not documented."
    assert "user_profiles" in content, "UserProfile model not documented."


def test_by_schema(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(Path("tests/fixtures/by_schema"), tmp_path)

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert "users" in content, "User model not documented."
    assert "posts" in content, "Post model not documented."
    assert "user_profiles" in content, "UserProfile model not documented."
    assert "profiles" in content, "Schema 'profiles' not documented."
    assert "blog" in content, "Schema 'blog' not documented."


def test_by_schema_default(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/by_schema_default"), tmp_path
    )

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert "users" in content, "User model not documented."
    assert "posts" in content, "Post model not documented."
    assert "user_profiles" in content, "UserProfile model not documented."
    assert "default" in content, "Schema 'default' not documented."


def test_show_sql(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(Path("tests/fixtures/show_sql"), tmp_path)

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert "users" in content, "User model not documented."
    assert "posts" in content, "Post model not documented."
    assert "user_profiles" in content, "UserProfile model not documented."
    assert "View SQL" in content, "Expected SQL DDL not found in documentation."


def test_mermaid(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(Path("tests/fixtures/mermaid"), tmp_path)

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert 'div class="mermaid"' in content, (
        "Mermaid diagram not found in documentation."
    )


def test_mermaid_schema(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/mermaid_schema"), tmp_path
    )

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert 'div class="mermaid"' in content, (
        "Mermaid diagram not found in documentation."
    )


def test_mermaid_not_found(tmp_path: Path) -> None:
    project_path = setup_clean_mkdocs_folder(
        Path("tests/fixtures/mermaid_table_not_found"), tmp_path
    )

    result = build_docs_setup(project_path)
    assert result.exit_code == 0, (
        f"Build failed with exit code {result.exit_code}: {result.output}"
    )

    output_dir = project_path / "site"
    assert output_dir.exists(), "Output directory does not exist."

    models_page = output_dir / "index.html"
    assert models_page.exists(), "Models page was not generated."

    content = models_page.read_text(encoding="utf-8")
    assert "<!-- No tables to include in mermaid diagram -->" in content, (
        "Expected 'not found' comment"
    )
    assert 'div class="mermaid"' not in content, (
        "Mermaid diagram not found in documentation."
    )
