#!/bin/bash
# Pre-commit quality gate for ContentBot
# Runs automatically before git commits

echo "Running pre-commit checks..."

# Python syntax check
if git diff --cached --name-only | grep -q '\.py$'; then
    echo "  → Checking Python syntax..."
    for file in $(git diff --cached --name-only | grep '\.py$'); do
        python -m py_compile "$file"
        if [ $? -ne 0 ]; then
            echo "❌ Syntax error in $file"
            exit 1
        fi
    done
    echo "  ✓ Python syntax OK"
fi

# Frontend build check
if git diff --cached --name-only | grep -q 'contentbot-ui/src/'; then
    echo "  → Verifying frontend build..."
    cd contentbot-ui && npm run build > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "❌ Frontend build failed"
        cd ..
        exit 1
    fi
    cd ..
    echo "  ✓ Frontend builds OK"
fi

# Run unit tests for changed Python files
if git diff --cached --name-only | grep -q '\.py$'; then
    echo "  → Running unit tests..."
    pytest tests/unit/ -x --tb=short -q
    if [ $? -ne 0 ]; then
        echo "❌ Unit tests failed"
        exit 1
    fi
    echo "  ✓ Tests pass"
fi

echo "✅ All pre-commit checks passed"
exit 0
