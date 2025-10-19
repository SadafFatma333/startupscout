#!/bin/bash

# 🚀 StartupScout Monitoring Deployment Script
# Deploys Grafana and Prometheus to Railway

set -e

echo "🚀 Deploying StartupScout Monitoring to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

# Create or select project
echo "📁 Setting up Railway project..."
if [ -z "$RAILWAY_PROJECT_ID" ]; then
    echo "Creating new Railway project..."
    railway new
else
    echo "Using existing project: $RAILWAY_PROJECT_ID"
    railway link $RAILWAY_PROJECT_ID
fi

# Deploy Grafana
echo "📊 Deploying Grafana..."
railway up --service grafana-monitoring

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set GF_ADMIN_PASSWORD=${GF_ADMIN_PASSWORD:-$(openssl rand -base64 32)}
railway variables set STARTUPSCOUT_API_URL=${STARTUPSCOUT_API_URL:-https://startupscout-api.railway.app}
railway variables set PROMETHEUS_RETENTION_TIME=${PROMETHEUS_RETENTION_TIME:-7d}

# Get deployment URLs
echo "🔗 Getting deployment URLs..."
GRAFANA_URL=$(railway domain --service grafana-monitoring)
PROMETHEUS_URL=$(railway domain --service prometheus-monitoring)

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📊 Grafana Dashboard: https://$GRAFANA_URL"
echo "🔍 Prometheus Metrics: https://$PROMETHEUS_URL"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: Check Railway dashboard for GF_ADMIN_PASSWORD"
echo ""
echo "📋 Next Steps:"
echo "1. Update your StartupScout API URL in Railway dashboard"
echo "2. Access Grafana and import dashboards"
echo "3. Set up alerts and notifications"
echo "4. Configure custom domain (optional)"
echo ""
echo "🎉 Your monitoring stack is now live in the cloud!"
