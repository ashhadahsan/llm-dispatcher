#!/bin/bash

# Deploy LLM-Dispatcher documentation to GitHub Pages

echo "🚀 Deploying LLM-Dispatcher documentation to GitHub Pages..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "   Consider committing your changes before deploying"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Build the documentation
echo "🔨 Building documentation..."
mkdocs build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please fix the errors and try again."
    exit 1
fi

# Deploy to GitHub Pages
echo "🌐 Deploying to GitHub Pages..."
mkdocs gh-deploy

if [ $? -eq 0 ]; then
    echo "✅ Documentation deployed successfully!"
    echo "🌐 Your documentation is now available at:"
    echo "   https://ashhadahsan.github.io/llm-dispatcher/"
else
    echo "❌ Deployment failed. Please check the error messages above."
    exit 1
fi
