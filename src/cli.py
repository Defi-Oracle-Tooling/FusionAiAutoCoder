"""Command-line interface for FusionAiAutoCoder."""

from typing import Dict, Any
import argparse
import sys

from src.validation import validate_language, validate_file_path
from src.config.constants import SUPPORTED_LANGUAGES, DEFAULT_PORT
from src.types import ConfigurationError


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="FusionAiAutoCoder - AI-powered code generation and optimization"
    )

    parser.add_argument("--config", type=str, help="Path to configuration file")

    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Port for the API server"
    )

    parser.add_argument(
        "--language",
        type=str,
        choices=SUPPORTED_LANGUAGES,
        default="python",
        help="Target programming language",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    parser.add_argument(
        "--use-gpu", action="store_true", help="Enable GPU acceleration if available"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code")
    generate_parser.add_argument(
        "prompt", type=str, help="Prompt describing the code to generate"
    )
    generate_parser.add_argument("--output", type=str, help="Output file path")

    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Optimize code")
    optimize_parser.add_argument("input", type=str, help="Input file path")
    optimize_parser.add_argument(
        "--target",
        choices=["performance", "memory", "readability"],
        default="performance",
        help="Optimization target",
    )

    return parser.parse_args()


def validate_cli_args(args: argparse.Namespace) -> Dict[str, Any]:
    """Validate and process command-line arguments."""
    try:
        config: Dict[str, Any] = {
            "language": validate_language(args.language),
            "log_level": args.log_level,
            "use_gpu": args.use_gpu,
        }

        if args.config:
            config["config_path"] = validate_file_path(args.config)

        if args.command == "generate":
            if args.output:
                config["output_path"] = validate_file_path(args.output)
            config["prompt"] = args.prompt

        elif args.command == "optimize":
            input_path = validate_file_path(args.input)
            if not input_path.exists():
                raise ConfigurationError(f"Input file does not exist: {input_path}")
            config["input_path"] = input_path
            config["target"] = args.target

        return config

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    args = parse_args()
    config = validate_cli_args(args)

    if args.command == "generate":
        from src.main import run_workflow

        result = run_workflow(
            task_type="code_generation",
            task_data={
                "prompt": config["prompt"],
                "language": config["language"],
                "use_gpu": config["use_gpu"],
            },
        )

        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        if "output_path" in config:
            with open(config["output_path"], "w") as f:
                f.write(result["code"])
        else:
            print(result["code"])

    elif args.command == "optimize":
        from src.main import run_workflow

        with open(config["input_path"]) as f:
            code = f.read()

        result = run_workflow(
            task_type="code_optimization",
            task_data={
                "code": code,
                "language": config["language"],
                "target": config["target"],
                "use_gpu": config["use_gpu"],
            },
        )

        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(result["optimized_code"])


if __name__ == "__main__":
    main()
