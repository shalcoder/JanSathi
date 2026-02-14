import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("--- Environment Variable Verification ---")

# Required Variables for Production (and recommended for Dev)
required_vars = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_REGION',
    'S3_BUCKET_NAME',
    'BEDROCK_MODEL_ID',
    'DATABASE_URL',
    'SECRET_KEY'
]

missing = []
for var in required_vars:
    value = os.getenv(var)
    if not value:
        missing.append(var)
        print(f"❌ {var} is MISSING or EMPTY")
    else:
        # Mask secrets
        if 'KEY' in var or 'SECRET' in var:
            masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
            print(f"✅ {var} is set (Value: {masked})")
        else:
            print(f"✅ {var} is set (Value: {value})")

print("-" * 30)
if missing:
    print(f"⚠️  Missing {len(missing)} required environment variables.")
    print("Please open 'backend/.env' and fill in the missing values.")
else:
    print("ALL GOOD! Environment seems correctly configured.")
