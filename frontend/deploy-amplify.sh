#!/bin/bash
set -e

echo "🚀 Preparing for AWS Amplify Deployment..."
echo ""

# Ensure we're in the frontend directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm ci
else
    echo "✅ Dependencies already installed"
fi

# Run build to verify everything works
echo ""
echo "🔨 Testing build..."
npm run build

echo ""
echo "✅ Build successful!"
echo ""
echo "📋 Next Steps:"
echo "   1. Commit your changes:"
echo "      git add ."
echo "      git commit -m 'Prepare for AWS Amplify deployment'"
echo "      git push origin main"
echo ""
echo "   2. Go to AWS Amplify Console:"
echo "      https://console.aws.amazon.com/amplify/"
echo ""
echo "   3. Click 'New app' → 'Host web app'"
echo ""
echo "   4. Connect your Git repository"
echo ""
echo "   5. Configure build settings (auto-detected for Next.js)"
echo ""
echo "   6. Add environment variables:"
echo "      NEXT_PUBLIC_API_URL=https://your-backend-api.com"
echo ""
echo "   7. Deploy!"
echo ""
echo "🎉 Your app will be live at: https://main.xxxxx.amplifyapp.com"
