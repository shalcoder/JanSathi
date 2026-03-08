# Connect Vercel Frontend to AWS Lambda Backend

## Current Status
- ✅ Backend: Deployed on AWS Lambda (function name: `jansathi-backend`)
- ✅ Frontend: Deployed on Vercel
- ❌ Connection: Frontend still pointing to `localhost:5010`

## Step 1: Get Your Lambda API Gateway URL

You need to find your API Gateway endpoint URL. Run this command:

```bash
aws apigatewayv2 get-apis --region us-east-1 --query "Items[?Name=='jansathi-api'].ApiEndpoint" --output text
```

If that doesn't return anything, try listing all APIs:

```bash
aws apigatewayv2 get-apis --region us-east-1
```

Look for an API with name `jansathi-api` and copy the `ApiEndpoint` value.

**Alternative: Check AWS Console**

1. Go to: https://console.aws.amazon.com/apigateway/home?region=us-east-1
2. Look for `jansathi-api` in the list
3. Click on it and copy the "Invoke URL"

The URL should look like: `https://abc123xyz.execute-api.us-east-1.amazonaws.com`

## Step 2: Update Frontend Environment Variables

Once you have the API Gateway URL, update your Vercel deployment:

### Option A: Via Vercel Dashboard (Recommended)

1. Go to: https://vercel.com/dashboard
2. Select your `JanSathi` project
3. Go to **Settings** → **Environment Variables**
4. Find `NEXT_PUBLIC_API_URL` or add it if it doesn't exist
5. Set the value to your API Gateway URL (e.g., `https://abc123xyz.execute-api.us-east-1.amazonaws.com`)
6. Click **Save**
7. Go to **Deployments** tab
8. Click the three dots on the latest deployment → **Redeploy**

### Option B: Via Vercel CLI

```bash
cd JanSathi/frontend

# Install Vercel CLI if not already installed
npm i -g vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production

# When prompted, enter your API Gateway URL
# Example: https://abc123xyz.execute-api.us-east-1.amazonaws.com

# Redeploy
vercel --prod
```

## Step 3: Update Local Environment (Optional)

Update `JanSathi/frontend/.env.local` for local development:

```env
# Backend API - Production Lambda
NEXT_PUBLIC_API_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com

# Or keep localhost for local testing
# NEXT_PUBLIC_API_URL=http://localhost:5010
```

## Step 4: Configure CORS on Lambda

Your Lambda backend needs to allow requests from Vercel. Update the backend `.env`:

```env
ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,https://your-vercel-domain.vercel.app,http://localhost:3000
```

Then redeploy the Lambda function:

```bash
cd JanSathi/backend
python create_minimal_package.py
aws s3 cp function-minimal.zip s3://jansathi-lambda-deploy-YOUR_ACCOUNT_ID/
aws lambda update-function-code \
  --function-name jansathi-backend \
  --s3-bucket jansathi-lambda-deploy-YOUR_ACCOUNT_ID \
  --s3-key function-minimal.zip \
  --region us-east-1
```

## Step 5: Test the Connection

After redeploying Vercel:

1. Open your Vercel site: https://jan-sathi-five.vercel.app
2. Open browser DevTools (F12) → Console tab
3. Try using the chat feature
4. Check the Network tab for API calls
5. Verify requests are going to your Lambda URL (not localhost)

### Test API Directly

```bash
# Test health endpoint
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health

# Test query endpoint
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/query \
  -H 'Content-Type: application/json' \
  -d '{"text_query": "pradhan mantri awas yojana", "language": "hi"}'
```

## Troubleshooting

### Issue: "Network Error" or "CORS Error"

**Solution:** Update Lambda CORS configuration

```bash
# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name jansathi-backend \
  --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app}" \
  --region us-east-1
```

### Issue: "API Gateway not found"

**Solution:** Create API Gateway if it doesn't exist

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create API Gateway
API_ID=$(aws apigatewayv2 create-api \
  --name jansathi-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:${ACCOUNT_ID}:function:jansathi-backend \
  --region us-east-1 \
  --query 'ApiId' \
  --output text)

# Give API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name jansathi-backend \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:${ACCOUNT_ID}:${API_ID}/*/*" \
  --region us-east-1

# Get the API endpoint
aws apigatewayv2 get-api --api-id $API_ID --region us-east-1 --query 'ApiEndpoint' --output text
```

### Issue: "502 Bad Gateway" from Lambda

**Solution:** Check Lambda logs

```bash
# View recent Lambda logs
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1
```

Common causes:
- Lambda function not deployed correctly
- Missing dependencies in Lambda package
- Lambda timeout (increase to 60s)
- Lambda memory too low (increase to 1024 MB)

### Issue: Knowledge Base features not working

**Solution:** Ensure Lambda has Bedrock permissions

1. Go to Lambda console: https://console.aws.amazon.com/lambda/home?region=us-east-1
2. Click on `jansathi-backend`
3. Go to **Configuration** → **Permissions**
4. Click on the execution role
5. Add policy: `AmazonBedrockFullAccess`

## Quick Commands Reference

```bash
# Get API Gateway URL
aws apigatewayv2 get-apis --region us-east-1 --query "Items[?Name=='jansathi-api'].ApiEndpoint" --output text

# Update Vercel environment variable
vercel env add NEXT_PUBLIC_API_URL production

# Redeploy Vercel
vercel --prod

# Test Lambda API
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health

# View Lambda logs
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1
```

## Next Steps

After successful connection:

1. ✅ Test all features on Vercel site
2. ✅ Test Knowledge Base upload and query
3. ✅ Test chat functionality
4. ✅ Monitor Lambda logs for errors
5. ✅ Set up CloudWatch alarms for production monitoring

---

**Need Help?**

If you're stuck, run this diagnostic command and share the output:

```bash
echo "=== Lambda Function ==="
aws lambda get-function --function-name jansathi-backend --region us-east-1 --query 'Configuration.[FunctionName,Runtime,Timeout,MemorySize]' --output table

echo "=== API Gateway ==="
aws apigatewayv2 get-apis --region us-east-1 --query "Items[?Name=='jansathi-api'].[Name,ApiEndpoint]" --output table

echo "=== Lambda Environment ==="
aws lambda get-function-configuration --function-name jansathi-backend --region us-east-1 --query 'Environment.Variables' --output json
```
