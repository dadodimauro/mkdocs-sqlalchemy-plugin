#!/usr/bin/env python3
"""
Script to run mkdocs serve for a test fixture directory.

Usage:
    python scripts/serve_fixture.py basic_setup
    python scripts/serve_fixture.py basic_setup --port 8001
    python scripts/serve_fixture.py basic_setup --dev-addr 0.0.0.0:8000
"""

import argparse
import sys
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Run mkdocs serve for a test fixture directory"
    )
    parser.add_argument(
        "fixture",
        help="Name of the fixture directory (e.g., 'basic_setup')",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)",
    )
    parser.add_argument(
        "--dev-addr",
        "-a",
        help="Development server address (default: localhost:PORT)",
    )
    parser.add_argument(
        "--no-livereload",
        action="store_true",
        help="Disable live reloading",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Find the fixture directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    fixture_dir = project_root / "tests" / "fixtures" / args.fixture

    if not fixture_dir.exists():
        print(f"❌ Error: Fixture directory not found: {fixture_dir}")
        print("\nAvailable fixtures:")
        fixtures_dir = project_root / "tests" / "fixtures"
        if fixtures_dir.exists():
            for item in sorted(fixtures_dir.iterdir()):
                if item.is_dir():
                    print(f"  - {item.name}")
        sys.exit(1)

    mkdocs_yml = fixture_dir / "mkdocs.yml"
    if not mkdocs_yml.exists():
        print(f"❌ Error: mkdocs.yml not found in {fixture_dir}")
        sys.exit(1)

    # Build the mkdocs serve command
    cmd = ["mkdocs", "serve", "-f", str(mkdocs_yml)]


    if args.dev_addr:
        cmd.extend(["--dev-addr", args.dev_addr])
    else:
        cmd.extend(["--dev-addr", f"localhost:{args.port}"])

    if args.no_livereload:
        cmd.append("--no-livereload")

    if args.verbose:
        cmd.append("--verbose")

    print(f"🚀 Serving fixture: {args.fixture}")
    print(f"📂 Directory: {fixture_dir}")
    print(f"🌐 URL: http://localhost:{args.port}")
    print(f"🔧 Command: {' '.join(cmd)}")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    try:
        subprocess.run(cmd, cwd=fixture_dir, check=True)
    except KeyboardInterrupt:
        print("\n\n✨ Server stopped")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running mkdocs serve: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
