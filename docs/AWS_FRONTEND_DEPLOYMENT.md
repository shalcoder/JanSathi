# AWS Frontend Deployment Guide - JanSathi

Complete guide to deploy Next.js frontend to AWS (migrating from Vercel).

---

## 🎯 Deployment Options

### Option 1: AWS Amplify (Recommended - Easiest)
- ✅ Automatic builds from Git
- ✅ Built-in CI/CD
- ✅ Custom domain support
- ✅ Free tier available
- ✅ Similar to Vercel experience

### Option 2: S3 + CloudFront (Most Cost-Effective)
- ✅ Static hosting
- ✅ Global CDN
- ✅ Very cheap (~$1-5/month)
- ⚠️ Requires manual builds

### Option 3: ECS Fargate (Most Flexible)
- ✅ Full control
- ✅ Docker-based
- ✅ Auto-scaling
- ⚠️ More expensive (~$15-30/month)

---

## 🚀 Option 1: AWS Amplify (Recommended)

### Step 1: Prepare Your Repository

Ensure your code is in GitHub/GitLab/Bitbucket:
```bash
cd JanSathi
git add .
git commit -m "Prepare for AWS Amplify deployment"
git push origin main
```

### Step 2: Create Amplify App

#### Via AWS Console:

1. **Go to AWS Amplify Console**
   ```
   https://console.aws.amazon.com/amplify/
   ```

2. **Click "New app" → "Host web app"**

3. **Connect Repository**
   - Select: GitHub (or your Git provider)
   - Authorize AWS Amplify
   - Select repository: `JanSathi`
   - Select branch: `main`

4. **Configure Build Settings**
   
   Amplify will auto-detect Next.js. Verify the build settings:
   
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: frontend/.next
       files:
         - '**/*'
     cache:
       paths:
         - frontend/node_modules/**/*
   ```

5. **Environment Variables**
   
   Add these in Amplify Console → Environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.com
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_key
   ```

6. **Advanced Settings**
   - Build image: `Amazon Linux:2023`
   - Node version: `18` or `20`
   - Root directory: `frontend`

7. **Click "Save and Deploy"**

### Step 3: Configure Custom Domain (Optional)

1. **In Amplify Console → Domain management**
2. **Add domain**
   - Enter your domain: `jansathi.com`
   - Amplify will provide DNS records
3. **Update DNS in your domain registrar**
4. **Wait for SSL certificate (5-10 minutes)**

### Step 4: Verify Deployment

```bash
# Your app will be available at:
https://main.d1234567890.amplifyapp.com

# Or your custom domain:
https://jansathi.com
```

---

## 🚀 Option 2: S3 + CloudFront (Static Export)

### Step 1: Configure Next.js for Static Export

Update `frontend/next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',  // Enable static export
  images: {
    unoptimized: true,  // Required for static export
  },
  trailingSlash: true,  // Better for S3
  // Remove any server-side features
};

export default nextConfig;
```

### Step 2: Build Static Site

```bash
cd frontend
npm run build
```

This creates `frontend/out/` directory with static files.

### Step 3: Create S3 Bucket

```bash
# Set variables
BUCKET_NAME="jansathi-frontend"
REGION="us-east-1"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Enable static website hosting
aws s3 website s3://$BUCKET_NAME \
  --index-document index.html \
  --error-document 404.html

# Set bucket policy for public access
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket $BUCKET_NAME \
  --policy file://bucket-policy.json
```

### Step 4: Upload Files to S3

```bash
cd frontend

# Upload all files
aws s3 sync out/ s3://$BUCKET_NAME/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html" \
  --exclude "*.json"

# Upload HTML with shorter cache
aws s3 sync out/ s3://$BUCKET_NAME/ \
  --delete \
  --cache-control "public, max-age=0, must-revalidate" \
  --exclude "*" \
  --include "*.html" \
  --include "*.json"
```

### Step 5: Create CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name $BUCKET_NAME.s3-website-$REGION.amazonaws.com \
  --default-root-object index.html
```

Or via AWS Console:

1. **Go to CloudFront Console**
2. **Create Distribution**
   - Origin domain: Select your S3 bucket
   - Origin access: Public
   - Viewer protocol policy: Redirect HTTP to HTTPS
   - Allowed HTTP methods: GET, HEAD, OPTIONS
   - Cache policy: CachingOptimized
   - Default root object: `index.html`

3. **Custom Error Pages**
   - 404 → `/404.html` (404)
   - 403 → `/index.html` (200) - For SPA routing

4. **Click "Create Distribution"**

5. **Note the CloudFront URL:**
   ```
   https://d1234567890.cloudfront.net
   ```

### Step 6: Configure Custom Domain (Optional)

1. **Request SSL Certificate in ACM (us-east-1)**
   ```bash
   aws acm request-certificate \
     --domain-name jansathi.com \
     --domain-name www.jansathi.com \
     --validation-method DNS \
     --region us-east-1
   ```

2. **Add CNAME to CloudFront Distribution**
   - Alternate domain names: `jansathi.com`, `www.jansathi.com`
   - SSL certificate: Select your ACM certificate

3. **Update DNS**
   - Create CNAME: `jansathi.com` → `d1234567890.cloudfront.net`

---

## 🚀 Option 3: ECS Fargate (Docker)

### Step 1: Create Dockerfile

Create `frontend/Dockerfile.aws`:

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Build
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Copy built files
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

Update `frontend/next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  output: 'standalone',  // For Docker deployment
};
```

### Step 2: Build and Push to ECR

```bash
# Set variables
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"
REPO_NAME="jansathi-frontend"

# Create ECR repository
aws ecr create-repository \
  --repository-name $REPO_NAME \
  --region $REGION

# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build image
cd frontend
docker build -f Dockerfile.aws -t $REPO_NAME .

# Tag image
docker tag $REPO_NAME:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
```

### Step 3: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster \
  --cluster-name jansathi-cluster \
  --region $REGION

# Create task definition
cat > task-definition.json <<EOF
{
  "family": "jansathi-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NEXT_PUBLIC_API_URL",
          "value": "https://your-backend-api.com"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jansathi-frontend",
          "awslogs-region": "$REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json
```

### Step 4: Create Application Load Balancer

```bash
# Create security group for ALB
aws ec2 create-security-group \
  --group-name jansathi-alb-sg \
  --description "Security group for JanSathi ALB" \
  --vpc-id vpc-xxxxx

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Create ALB (via console is easier)
# Go to EC2 → Load Balancers → Create
```

### Step 5: Create ECS Service

```bash
aws ecs create-service \
  --cluster jansathi-cluster \
  --service-name jansathi-frontend-service \
  --task-definition jansathi-frontend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx,subnet-yyyyy],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=frontend,containerPort=3000"
```

---

## 📋 Deployment Scripts

### Create `frontend/deploy-amplify.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying to AWS Amplify..."

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build
echo "🔨 Building application..."
npm run build

echo "✅ Build complete! Push to Git to trigger Amplify deployment."
echo "   git add ."
echo "   git commit -m 'Deploy to Amplify'"
echo "   git push origin main"
```

### Create `frontend/deploy-s3.sh`:

```bash
#!/bin/bash
set -e

BUCKET_NAME="jansathi-frontend"
DISTRIBUTION_ID="E1234567890ABC"  # Your CloudFront distribution ID

echo "🚀 Deploying to S3 + CloudFront..."

# Build
echo "🔨 Building application..."
npm run build

# Upload to S3
echo "📤 Uploading to S3..."
aws s3 sync out/ s3://$BUCKET_NAME/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html" \
  --exclude "*.json"

aws s3 sync out/ s3://$BUCKET_NAME/ \
  --delete \
  --cache-control "public, max-age=0, must-revalidate" \
  --exclude "*" \
  --include "*.html" \
  --include "*.json"

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"

echo "✅ Deployment complete!"
echo "   URL: https://$BUCKET_NAME.s3-website-us-east-1.amazonaws.com"
```

Make scripts executable:
```bash
chmod +x frontend/deploy-amplify.sh
chmod +x frontend/deploy-s3.sh
```

---

## 🔧 Environment Variables

Create `frontend/.env.production`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.jansathi.com

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxxxx
CLERK_SECRET_KEY=sk_live_xxxxx

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_KNOWLEDGE_BASE=true
```

---

## 💰 Cost Comparison

| Option | Monthly Cost | Best For |
|--------|-------------|----------|
| **Amplify** | $0-15 | Easy deployment, CI/CD |
| **S3 + CloudFront** | $1-5 | Static sites, low cost |
| **ECS Fargate** | $15-30 | Dynamic apps, full control |

---

## ✅ Post-Deployment Checklist

- [ ] Frontend deployed and accessible
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Environment variables set
- [ ] API connection working
- [ ] Authentication working (Clerk)
- [ ] Knowledge Base page accessible
- [ ] All routes working
- [ ] Performance optimized
- [ ] Monitoring enabled

---

## 🎯 Recommended Approach

**For JanSathi, I recommend AWS Amplify because:**

1. ✅ Easiest migration from Vercel
2. ✅ Automatic deployments from Git
3. ✅ Built-in CI/CD
4. ✅ Free tier available
5. ✅ Custom domain support
6. ✅ Similar developer experience

---

## 📞 Quick Start Commands

### Deploy with Amplify (Recommended):

```bash
# 1. Push code to Git
git push origin main

# 2. Go to AWS Amplify Console
# 3. Connect repository
# 4. Deploy automatically!
```

### Deploy with S3 + CloudFront:

```bash
cd frontend
./deploy-s3.sh
```

---

## 🔗 Next Steps

After frontend deployment:
1. ✅ Frontend deployed
2. ⏭️ Deploy Backend (Lambda or ECS)
3. ⏭️ Configure API Gateway
4. ⏭️ Set up DynamoDB
5. ⏭️ Configure Bedrock Knowledge Base

---

**Ready to deploy? Let's start with AWS Amplify!** 🚀
