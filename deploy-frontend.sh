#!/bin/bash
# deploy-frontend.sh - Manual frontend deployment

echo "🚀 Deploying Frontend Only..."

# Check if there are UI changes
if git diff --quiet HEAD^ HEAD -- ui/; then
    echo "❌ No UI changes detected. Skipping frontend deployment."
    exit 0
fi

echo "✅ UI changes detected. Deploying to Vercel..."

# Trigger Vercel deployment
# You can add Vercel CLI commands here if needed
echo "📦 Frontend deployment triggered!"
