#!/bin/bash
# Auto-format hook for PostToolUse (Write|Edit|MultiEdit)
# Runs ruff for Python files, biome for TypeScript/JavaScript files

set -e

# Read JSON input from stdin
INPUT=$(cat)

# Extract file_path from tool_input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# If no file path, exit silently
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Get file extension
EXT="${FILE_PATH##*.}"

# Get project directory
PROJECT_DIR="$CLAUDE_PROJECT_DIR"
if [ -z "$PROJECT_DIR" ]; then
    PROJECT_DIR=$(pwd)
fi

# Determine if file is in backend or frontend
case "$FILE_PATH" in
    */backend/*.py|*backend/*.py)
        # Python file in backend - run ruff
        cd "$PROJECT_DIR/backend"

        # Run ruff check with auto-fix (suppress output on success)
        if uv run ruff check "$FILE_PATH" --fix --quiet 2>/dev/null; then
            : # Success, no output
        fi

        # Run ruff format (suppress output on success)
        if uv run ruff format "$FILE_PATH" --quiet 2>/dev/null; then
            : # Success, no output
        fi

        echo "Auto-formatted: $(basename "$FILE_PATH")"
        ;;

    */frontend/*.ts|*/frontend/*.tsx|*/frontend/*.js|*/frontend/*.jsx)
        # TypeScript/JavaScript file in frontend - run biome
        cd "$PROJECT_DIR/frontend"

        # Run biome check with auto-fix (suppress output on success)
        if bun run biome check "$FILE_PATH" --write --unsafe 2>/dev/null; then
            : # Success, no output
        fi

        echo "Auto-formatted: $(basename "$FILE_PATH")"
        ;;

    *.py)
        # Python file outside backend (e.g., poc/) - try ruff if available
        if command -v ruff &> /dev/null; then
            ruff check "$FILE_PATH" --fix --quiet 2>/dev/null || true
            ruff format "$FILE_PATH" --quiet 2>/dev/null || true
            echo "Auto-formatted: $(basename "$FILE_PATH")"
        fi
        ;;

    *)
        # Other file types - no action
        exit 0
        ;;
esac

exit 0
