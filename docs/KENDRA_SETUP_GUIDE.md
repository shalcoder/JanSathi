# JanSathi - AWS Kendra Setup Guide

This guide walks you through setting up Amazon Kendra to provide verified government scheme knowledge to the JanSathi Bedrock Agent.

---

## 📋 Prerequisites

- AWS Account with Bedrock and Kendra access
- Some sample scheme PDFs or text documents to index

---

## Step 1: Create an S3 Bucket for Knowledge

Before creating a Kendra index, you need a place to store your documents.

1. Go to the **S3 Console**.
2. Click **Create bucket**.
3. Name it something unique, e.g., `jansathi-knowledge-base-[your-account-id]`.
4. Region: `us-east-1` (Must match your Lambda and Bedrock region).
5. Leave all other settings as default and click **Create bucket**.
6. Open the bucket and click **Upload**.
7. Upload your scheme documents (PDFs, TXT, DOCX), such as guidelines for PM-Kisan, Ayushman Bharat, etc.

---

## Step 2: Create a Kendra Index

This represents the search engine for your documents.

1. Go to the **Amazon Kendra Console**.
2. Click **Create an index**.
3. **Index name**: `jansathi-index`
4. **IAM role**: Select **Create a new role** and set a suffix (e.g., `jansathi-kendra-role`).
5. **Edition**: Choose **Developer Edition** (Recommended for hackathons to save costs: 2.50 USD/Hour).
6. Click **Next**, leave Access control as default, click **Next** again, then **Create**.
7. **Wait**: It takes about 15-30 minutes for the Kendra Index to provision completely.

---

## Step 3: Add the S3 Data Source

Once the index is Active, you need to connect your S3 bucket to it.

1. Inside your `jansathi-index`, go to **Data sources** via the left menu.
2. Under "Amazon S3", click **Add connector**.
3. **Data source name**: `jansathi-s3-source`.
4. **Source**: Select the S3 bucket you created in Step 1.
5. **IAM role**: Select **Create a new role** (e.g., `kendra-s3-access-role`).
6. **Sync schedule**: Choose **Run on demand**.
7. Click **Next**, review, and click **Add data source**.

---

## Step 4: Sync the Data

The documents won't be searchable until you sync them.

1. Go back to your data source `jansathi-s3-source`.
2. Click **Sync now**.
3. Wait for the sync state to change from `Syncing` to `Succeeded`.
4. You can test your index by going to the **Search console** tab in Kendra and typing a query like *"What is PM Kisan?"*.

---

## Step 5: Update the JanSathi Backend

Now that Kendra is running, you must connect the JanSathi backend to it.

1. Go to the Kendra **Index settings**.
2. Copy the **Index ID** (It will look like a UUID: `12345678-1234-1234-1234-123456789abc`).
3. Open `JanSathi/backend/.env`.
4. Update the `KENDRA_INDEX_ID` variable with this exact 36-character ID:

```env
KENDRA_INDEX_ID=your-36-character-uuid-here
```

5. **Redeploy the backend** to AWS using the deployment script so the Lambda environment picks up the new Index ID.

---

## Troubleshooting

- **Validation Error `Invalid length for parameter IndexId`**: Ensure the ID in `.env` is exactly 36 characters (the UUID), not the index name.
- **Agent giving generic answers**: Check if your most recent S3 document upload was synced to Kendra. If the sync didn't run, the Bedrock agent can't see the new files.
- **Cost Warning**: Remember to **Delete the Kendra Index** after the hackathon to avoid incurring the high hourly charges!
