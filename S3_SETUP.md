# S3 Setup Guide for StartupScout

This guide helps you set up AWS S3 for storing StartupScout data files, reducing Docker image size.

## 🎯 Why S3?

- **Docker image size:** Reduces from 8.5GB to ~500MB
- **Faster deployments:** No large data files to upload
- **Scalability:** Data files accessible from multiple instances
- **Cost effective:** S3 storage is very cheap

## 📋 Prerequisites

1. **AWS Account** - Create at https://aws.amazon.com
2. **AWS CLI** - Install locally (optional, for setup)

## 🔧 Setup Steps

### Step 1: Create S3 Bucket

```bash
# Using AWS CLI (recommended)
aws s3 mb s3://startupscout-data --region us-west-2

# Or create via AWS Console:
# 1. Go to https://s3.console.aws.amazon.com
# 2. Click "Create bucket"
# 3. Name: startupscout-data
# 4. Region: us-west-2
# 5. Keep default settings
```

### Step 2: Create IAM User

```bash
# Create IAM user with S3 access
aws iam create-user --user-name startupscout-s3-user

# Create access policy
aws iam put-user-policy --user-name startupscout-s3-user --policy-name S3Access --policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::startupscout-data",
        "arn:aws:s3:::startupscout-data/*"
      ]
    }
  ]
}'

# Create access keys
aws iam create-access-key --user-name startupscout-s3-user
```

### Step 3: Upload Data Files

```bash
# Set your AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export S3_BUCKET_NAME=startupscout-data

# Upload data files to S3
python3 upload_to_s3.py
```

### Step 4: Add Environment Variables to Railway

In your Railway project dashboard, add these variables:

```
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
S3_BUCKET_NAME=startupscout-data
AWS_REGION=us-west-2
```

## 🚀 Deploy

```bash
# Commit changes
git add .
git commit -m "Add S3 storage support"
git push origin main

# Deploy to Railway
railway up
```

## 📊 Expected Results

- **Docker image size:** ~500MB (down from 8.5GB)
- **Deployment time:** ~2-3 minutes (down from 10+ minutes)
- **Functionality:** Same as before, data files downloaded on startup

## 🔍 Troubleshooting

### Data files not downloading?
- Check AWS credentials in Railway
- Verify S3 bucket name and permissions
- Check Railway logs: `railway logs`

### App startup slow?
- First startup downloads files (2-3 minutes)
- Subsequent restarts use cached files
- Consider using EFS for persistent caching

## 💰 Cost Estimate

- **S3 storage:** ~$0.023/GB/month
- **Data transfer:** ~$0.09/GB (first download)
- **Total:** <$1/month for typical usage

## 🔄 Alternative: Use Railway Volumes

If you prefer not to use S3, you can use Railway volumes:

```bash
# Create volume
railway volume create --name data --mount-path /app/data

# Mount volume in railway.toml
[deploy]
volumes = ["data:/app/data"]
```

But S3 is more cost-effective and scalable.
