"""
Test runner script with options for different test suites
"""
import subprocess
import sys
import argparse


def run_tests(suite="all", verbose=False, coverage=True):
    """
    Run test suite
    
    Args:
        suite: Test suite to run (all, rag, database, tools, prompts, unit, integration)
        verbose: Verbose output
        coverage: Generate coverage report
    """
    cmd = ["pytest"]
    
    # Select test files based on suite
    if suite == "all":
        cmd.append("tests/")
    elif suite == "rag":
        cmd.extend(["-m", "rag", "tests/test_rag.py"])
    elif suite == "database":
        cmd.extend(["-m", "database", "tests/test_database.py"])
    elif suite == "tools":
        cmd.extend(["-m", "tools", "tests/test_tools.py"])
    elif suite == "prompts":
        cmd.extend(["-m", "prompts", "tests/test_prompts.py"])
    elif suite == "unit":
        cmd.extend(["-m", "unit"])
    elif suite == "integration":
        cmd.extend(["-m", "integration"])
    else:
        print(f"Unknown suite: {suite}")
        return 1
    
    # Add verbosity
    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=agent",
            "--cov=database",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Disable warnings
    cmd.append("--disable-warnings")
    
    print(f"\n{'='*60}")
    print(f"Running tests: {suite}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    # Run pytest
    result = subprocess.run(cmd)
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run ClaimFlow AI tests")
    parser.add_argument(
        "suite",
        nargs="?",
        default="all",
        choices=["all", "rag", "database", "tools", "prompts", "unit", "integration"],
        help="Test suite to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--no-cov",
        action="store_true",
        help="Disable coverage report"
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        suite=args.suite,
        verbose=args.verbose,
        coverage=not args.no_cov
    )
    
    if exit_code == 0:
        print(f"\n{'='*60}")
        print("✅ All tests passed!")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print("❌ Some tests failed")
        print(f"{'='*60}\n")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
