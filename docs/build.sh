#!/bin/bash

# Build and serve LLM-Dispatcher documentation

echo "🏗️  Building LLM-Dispatcher documentation..."

# Install dependencies if not already installed
if ! command -v mkdocs &> /dev/null; then
    echo "📦 Installing MkDocs dependencies..."
    pip install -r requirements.txt
fi

# Build the documentation
echo "🔨 Building documentation..."
mkdocs build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Documentation built successfully!"
    echo "📁 Site files are in the 'site' directory"
    echo ""
    echo "🚀 To serve the documentation locally, run:"
    echo "   mkdocs serve"
    echo ""
    echo "🌐 To deploy to GitHub Pages, run:"
    echo "   mkdocs gh-deploy"
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi
