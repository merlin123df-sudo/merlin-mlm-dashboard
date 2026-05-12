#!/bin/bash

# Merlin MLM Dashboard - Streamlit Cloud Deployment Script
# This script sets up your project for deployment to Streamlit Cloud

echo "🚀 Merlin MLM Dashboard - Deployment Setup"
echo "==========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git from https://git-scm.com"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Initialize git if needed
if [ ! -d .git ]; then
    echo "📝 Initializing git repository..."
    git init
    git config user.name "MLM Dashboard Dev"
    git config user.email "dev@merlin-mlm.local"
    echo "✅ Git initialized"
else
    echo "✅ Git repository already initialized"
fi

echo ""
echo "📋 Checking required files..."

# Check required files
required_files=(
    "app.py"
    "ml_engine.py"
    "pipeline.py"
    "requirements.txt"
    "README.md"
    ".gitignore"
    ".streamlit/config.toml"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo ""
    echo "✅ All required files are present!"
else
    echo ""
    echo "⚠️  Missing files: ${missing_files[@]}"
    echo "Please create them before deploying."
    exit 1
fi

echo ""
echo "📦 Checking dependencies..."

# Check if requirements are installable
if pip install -r requirements.txt --dry-run > /dev/null 2>&1; then
    echo "✅ All dependencies can be installed"
else
    echo "⚠️  Some dependencies may have issues"
fi

echo ""
echo "📊 Checking database..."

if [ -f "processed_db/warehouse.db" ]; then
    db_size=$(ls -lh processed_db/warehouse.db | awk '{print $5}')
    echo "✅ Database exists (Size: $db_size)"
else
    echo "⚠️  Database not found. It will be created on first run."
fi

echo ""
echo "🚀 Ready to Deploy!"
echo ""
echo "Next steps:"
echo "1. Create repository on GitHub (https://github.com/new)"
echo "2. Run: git add . && git commit -m 'Initial commit'"
echo "3. Run: git remote add origin https://github.com/USERNAME/merlin-mlm-dashboard.git"
echo "4. Run: git push -u origin main"
echo "5. Go to https://share.streamlit.io and deploy!"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"
echo ""
