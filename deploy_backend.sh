#!/bin/bash
# Guardia Lingua - Backend Cloud Run Deployment Script
# ---------------------------------------------------

# 1. Configuration
PROJECT_ID="your-google-cloud-project-id"
SERVICE_NAME="cyberguard-backend"
REGION="us-central1"

echo "🚀 Starting Deployment for $SERVICE_NAME..."

# 2. Build the Container (using Google Cloud Build)
echo "📦 Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# 3. Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="USE_OLLAMA=False,DATABASE_URL=postgresql://postgres:your-password@db.nnoddmdwwladxasorzkh.supabase.co:5432/postgres"

# 4. Success Output
echo "✅ Deployment Successful!"
echo "🔗 Your Backend is live at:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'
