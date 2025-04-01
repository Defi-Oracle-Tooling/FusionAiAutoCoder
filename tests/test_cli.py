"""Test command-line interface functionality."""

from typing import Dict, Any
import pytest  # type: ignore
from unittest.mock import patch, MagicMock  # type: ignore
import argparse
from pathlib import Path

from src.cli import parse_args, validate_cli_args, main


def test_parse_args() -> None:
    """Test argument parsing."""
    with patch(
        "sys.argv", ["script.py", "--language", "python", "generate", "test prompt"]
    ):
        args: argparse.Namespace = parse_args()
        assert args.language == "python"
        assert args.command == "generate"
        assert args.prompt == "test prompt"


def test_validate_cli_args(tmp_path: Path) -> None:
    """Test CLI argument validation."""
    # Create a test file
    test_file: Path = tmp_path / "test.py"
    test_file.touch()

    # Test generate command
    args = argparse.Namespace(
        language="python",
        log_level="INFO",
        use_gpu=False,
        config=None,
        command="generate",
        prompt="test prompt",
        output=None,
    )

    config: Dict[str, Any] = validate_cli_args(args)
    assert config["language"] == "python"
    assert config["prompt"] == "test prompt"

    # Test optimize command
    args = argparse.Namespace(
        language="python",
        log_level="INFO",
        use_gpu=False,
        config=None,
        command="optimize",
        input=str(test_file),
        target="performance",
    )

    config = validate_cli_args(args)
    assert config["language"] == "python"
    assert config["target"] == "performance"
    assert config["input_path"] == test_file


def test_invalid_language() -> None:
    """Test invalid language handling."""
    args = argparse.Namespace(
        language="invalid",
        log_level="INFO",
        use_gpu=False,
        config=None,
        command="generate",
        prompt="test",
    )

    with pytest.raises(SystemExit):
        validate_cli_args(args)


@patch("src.main.run_workflow")
def test_main_generate(mock_run_workflow: MagicMock, tmp_path: Path) -> None:
    """Test main function with generate command."""
    output_file: Path = tmp_path / "output.py"

    mock_run_workflow.return_value = {"code": "def test(): pass", "language": "python"}

    with patch(
        "sys.argv",
        [
            "script.py",
            "--language",
            "python",
            "generate",
            "test prompt",
            "--output",
            str(output_file),
        ],
    ):
        main()

    assert output_file.exists()
    assert output_file.read_text() == "def test(): pass"


@patch("src.main.run_workflow")
def test_main_optimize(mock_run_workflow: MagicMock, tmp_path: Path) -> None:
    """Test main function with optimize command."""
    input_file: Path = tmp_path / "input.py"
    input_file.write_text("def test(): pass")

    mock_run_workflow.return_value = {
        "optimized_code": "def optimized_test(): pass",
        "language": "python",
    }

    with patch(
        "sys.argv",
        [
            "script.py",
            "--language",
            "python",
            "optimize",
            str(input_file),
            "--target",
            "performance",
        ],
    ):
        main()

    mock_run_workflow.assert_called_once()
