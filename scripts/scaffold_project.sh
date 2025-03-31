#!/bin/bash
# Project Scaffolding Script for FusionAiAutoCoder

set -e

# Default values
PROJECT_NAME="my-ai-project"
PROJECT_TYPE="standard"
LANGUAGE="python"
OUTPUT_DIR="$(pwd)"

# Display help
function show_help {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                Show this help message"
    echo "  -n, --name NAME           Project name (default: my-ai-project)"
    echo "  -t, --type TYPE           Project type: standard, web, api, ml (default: standard)"
    echo "  -l, --language LANGUAGE   Programming language: python, typescript, javascript (default: python)"
    echo "  -o, --output-dir DIR      Output directory (default: current directory)"
    echo ""
    echo "Example:"
    echo "  $0 --name my-cool-project --type api --language typescript"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            ;;
        -n|--name)
            PROJECT_NAME="$2"
            shift
            shift
            ;;
        -t|--type)
            PROJECT_TYPE="$2"
            shift
            shift
            ;;
        -l|--language)
            LANGUAGE="$2"
            shift
            shift
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

PROJECT_DIR="$OUTPUT_DIR/$PROJECT_NAME"

echo "Creating project: $PROJECT_NAME"
echo "Project type: $PROJECT_TYPE"
echo "Language: $LANGUAGE"
echo "Output directory: $PROJECT_DIR"

# Create the project directory
mkdir -p "$PROJECT_DIR"

# Create common directories
mkdir -p "$PROJECT_DIR/src"
mkdir -p "$PROJECT_DIR/tests"
mkdir -p "$PROJECT_DIR/docs"
mkdir -p "$PROJECT_DIR/scripts"
mkdir -p "$PROJECT_DIR/config"

# Create Python-specific files if language is Python
if [ "$LANGUAGE" == "python" ]; then
    # Create virtual environment
    echo "Creating Python virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
    
    # Create setup.py
    cat > "$PROJECT_DIR/setup.py" << EOL
from setuptools import setup, find_packages

setup(
    name="${PROJECT_NAME}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "black",
        "flake8",
    ],
)
EOL
    
    # Create requirements.txt
    cat > "$PROJECT_DIR/requirements.txt" << EOL
# Development dependencies
pytest==7.3.1
black==23.3.0
flake8==6.0.0
pytest-cov==4.1.0

# Project dependencies
EOL

    # Create src module
    mkdir -p "$PROJECT_DIR/src/$PROJECT_NAME"
    touch "$PROJECT_DIR/src/$PROJECT_NAME/__init__.py"
    
    # Create main.py
    cat > "$PROJECT_DIR/src/$PROJECT_NAME/main.py" << EOL
"""Main module for $PROJECT_NAME."""

def main():
    """Run the main function."""
    print("Hello from $PROJECT_NAME!")

if __name__ == "__main__":
    main()
EOL
    
    # Create tests
    mkdir -p "$PROJECT_DIR/tests"
    touch "$PROJECT_DIR/tests/__init__.py"
    
    cat > "$PROJECT_DIR/tests/test_main.py" << EOL
"""Tests for main module."""
from src.$PROJECT_NAME.main import main

def test_main():
    """Test the main function."""
    # This is just a placeholder test
    assert True
EOL

elif [ "$LANGUAGE" == "typescript" ] || [ "$LANGUAGE" == "javascript" ]; then
    # Create package.json
    if [ "$LANGUAGE" == "typescript" ]; then
        cat > "$PROJECT_DIR/package.json" << EOL
{
  "name": "${PROJECT_NAME}",
  "version": "0.1.0",
  "description": "",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "start": "node dist/index.js"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "@types/node": "^18.15.11",
    "@typescript-eslint/eslint-plugin": "^5.57.1",
    "@typescript-eslint/parser": "^5.57.1",
    "eslint": "^8.38.0",
    "jest": "^29.5.0",
    "ts-jest": "^29.1.0",
    "typescript": "^5.0.4"
  },
  "dependencies": {}
}
EOL
        
        # Create tsconfig.json
        cat > "$PROJECT_DIR/tsconfig.json" << EOL
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "**/*.test.ts"]
}
EOL
        
        # Create src/index.ts
        cat > "$PROJECT_DIR/src/index.ts" << EOL
/**
 * Main entry point for $PROJECT_NAME
 */

export function main(): void {
  console.log('Hello from $PROJECT_NAME!');
}

if (require.main === module) {
  main();
}
EOL
        
        # Create test file
        mkdir -p "$PROJECT_DIR/src/__tests__"
        cat > "$PROJECT_DIR/src/__tests__/index.test.ts" << EOL
import { main } from '../index';

describe('main', () => {
  it('should execute without errors', () => {
    expect(() => main()).not.toThrow();
  });
});
EOL
        
    else
        # JavaScript version
        cat > "$PROJECT_DIR/package.json" << EOL
{
  "name": "${PROJECT_NAME}",
  "version": "0.1.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {
    "test": "jest",
    "lint": "eslint src/**/*.js",
    "start": "node src/index.js"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "eslint": "^8.38.0",
    "jest": "^29.5.0"
  },
  "dependencies": {}
}
EOL
        
        # Create src/index.js
        cat > "$PROJECT_DIR/src/index.js" << EOL
/**
 * Main entry point for $PROJECT_NAME
 */

function main() {
  console.log('Hello from $PROJECT_NAME!');
}

if (require.main === module) {
  main();
}

module.exports = { main };
EOL
        
        # Create test file
        mkdir -p "$PROJECT_DIR/src/__tests__"
        cat > "$PROJECT_DIR/src/__tests__/index.test.js" << EOL
const { main } = require('../index');

describe('main', () => {
  it('should execute without errors', () => {
    expect(() => main()).not.toThrow();
  });
});
EOL
    fi
fi

# Create a basic README.md
cat > "$PROJECT_DIR/README.md" << EOL
# $PROJECT_NAME

## Description

A brief description of the project.

## Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/username/$PROJECT_NAME.git
cd $PROJECT_NAME
\`\`\`

### Python Setup
\`\`\`bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
\`\`\`

### JavaScript/TypeScript Setup
\`\`\`bash
# Install dependencies
npm install
\`\`\`

## Usage

Describe how to use the project.

## Testing

### Python
\`\`\`bash
pytest
\`\`\`

### JavaScript/TypeScript
\`\`\`bash
npm test
\`\`\`

## License

This project is licensed under the ISC License.
EOL

# Create .gitignore
cat > "$PROJECT_DIR/.gitignore" << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
venv/
.coverage
htmlcov/

# JavaScript/TypeScript
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
dist/
coverage/

# IDEs and editors
.idea/
.vscode/
*.swp
*.swo
.DS_Store
EOL

echo "Project scaffold complete!"
echo "To get started:"
echo "  cd $PROJECT_DIR"

if [ "$LANGUAGE" == "python" ]; then
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
elif [ "$LANGUAGE" == "typescript" ] || [ "$LANGUAGE" == "javascript" ]; then
    echo "  npm install"
    echo "  npm test"
fi