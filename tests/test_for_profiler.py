"""Test for profiling.

This test can be useful for profiling, as most of the execution time
will be spent parsing and rendering instead of managing pytest execution
environment. The test simply ensures that the README and Markdown docs
in this project are formatted. To get and read profiler results:
  - `tox -e profile`
  - `firefox .tox/prof/combined.svg`
"""

from pathlib import Path

from md_kx._cli import run

PROJECT_ROOT = Path(__file__).parent.parent
# Make a few asserts to ensure this actually is the project root
# (a safeguard against refactorings where this file is moved).
assert (PROJECT_ROOT / "docs").exists()
assert (PROJECT_ROOT / "README.md").exists()
assert (PROJECT_ROOT / "src" / "md_kx").exists()


def test_for_profiler():
    # docs/ 为模板资产目录（禁格式化），只检查 README.md
    readme_path = str(PROJECT_ROOT / "README.md")
    assert run([readme_path, "--check"]) == 0
    # Also profile --wrap=INT code
    run([readme_path, "--check", "--wrap", "50"])
