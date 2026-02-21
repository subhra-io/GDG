#!/bin/bash

echo "🚀 Deploying PolicySentinel Frontend to Vercel..."
echo ""

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm i -g vercel
fi

# Navigate to frontend
cd frontend

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building frontend..."
npm run build

echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy the deployment URL from above"
echo "2. Add it to your submission form as 'Live Demo URL'"
echo "3. Note: Backend runs locally (for API key security)"
echo ""
