#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  Deploying ProofChain AWS Infrastructure"
echo "=========================================="

REGION="${AWS_REGION:-us-east-1}"
echo "Target Region: $REGION"

# 1. Verify caller identity
echo "Verifying AWS Identity..."
IDENTITY=$(aws sts get-caller-identity --output json)
ACCOUNT_ID=$(echo "$IDENTITY" | grep -o '"Account": "[^"]*' | cut -d'"' -f4)
ARN=$(echo "$IDENTITY" | grep -o '"Arn": "[^"]*' | cut -d'"' -f4)
echo "Authenticated as: $ARN (Account: $ACCOUNT_ID)"

BUCKET_NAME="proofchain-documents-${ACCOUNT_ID}"
TABLE_NAME="proofchain-state"

# 2. Provision S3 Bucket
echo "1. Checking S3 bucket '$BUCKET_NAME'..."
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "Bucket '$BUCKET_NAME' already exists."
else
    echo "Creating S3 bucket '$BUCKET_NAME' in $REGION..."
    if [ "$REGION" == "us-east-1" ]; then
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION"
    else
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION"
    fi
    # Block public access
    aws s3api put-public-access-block --bucket "$BUCKET_NAME" \
        --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
    # Default encryption
    aws s3api put-bucket-encryption --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
    echo "S3 bucket configured with AES256 encryption and public access block."
fi

# 3. Provision DynamoDB Table
echo "2. Checking DynamoDB table '$TABLE_NAME'..."
if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "DynamoDB table '$TABLE_NAME' already exists."
else
    echo "Creating DynamoDB table '$TABLE_NAME' (PAY_PER_REQUEST)..."
    aws dynamodb create-table \
        --table-name "$TABLE_NAME" \
        --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S \
        --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --region "$REGION"
    echo "Table '$TABLE_NAME' created successfully."
fi

# 4. Check Amazon Bedrock Models
echo "3. Verifying Bedrock Model Availability in $REGION..."
aws bedrock list-foundation-models --region "$REGION" --by-provider anthropic --query "modelSummaries[*].modelId" --output table || true

echo "=========================================="
echo "  AWS Infrastructure Ready!"
echo "  S3 Bucket: $BUCKET_NAME"
echo "  DynamoDB Table: $TABLE_NAME"
echo "  Region: $REGION"
echo "=========================================="
