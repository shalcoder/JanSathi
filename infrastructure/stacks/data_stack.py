"""
JanSathi Data Stack — DynamoDB Tables + S3 Buckets
From AWS_PRODUCTION_ARCHITECTURE.md Section 2: Data Layer
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
)
from constructs import Construct


class DataStack(Stack):
    """
    Creates:
    - DynamoDB: Conversations table (UserId HASH, Timestamp RANGE, TTL 90 days)
    - DynamoDB: CacheEntries table (QueryHash HASH, TTL for cache expiry)
    - S3: Audio bucket (lifecycle: 30d → Glacier → 90d delete)
    - S3: Uploads bucket (document storage)
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ============================================================
        # DynamoDB: Conversations Table
        # ============================================================
        self.conversations_table = dynamodb.Table(
            self, "ConversationsTable",
            table_name="JanSathi-Conversations",
            partition_key=dynamodb.Attribute(
                name="UserId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # Free Tier: 25 WCU/RCU
            removal_policy=RemovalPolicy.RETAIN,  # Don't delete data on stack destroy
            time_to_live_attribute="ttl",  # Auto-delete after 90 days
            point_in_time_recovery=True,  # RPO < 1 hour
        )

        # GSI: Query by conversation ID
        self.conversations_table.add_global_secondary_index(
            index_name="ConversationIdIndex",
            partition_key=dynamodb.Attribute(
                name="ConversationId",
                type=dynamodb.AttributeType.STRING
            ),
        )

        # ============================================================
        # DynamoDB: Cache Table (Response Caching)
        # ============================================================
        self.cache_table = dynamodb.Table(
            self, "CacheTable",
            table_name="JanSathi-Cache",
            partition_key=dynamodb.Attribute(
                name="QueryHash",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # Cache can be rebuilt
            time_to_live_attribute="ttl",  # Auto-expire cached responses
        )

        # ============================================================
        # S3: Audio Bucket (Polly output, Transcribe input)
        # ============================================================
        self.audio_bucket = s3.Bucket(
            self, "AudioBucket",
            bucket_name=None,  # Auto-generated unique name
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="MoveToGlacier",
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30),
                        )
                    ],
                    expiration=Duration.days(90),
                ),
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    max_age=3600,
                )
            ],
        )

        # ============================================================
        # S3: Uploads Bucket (User documents, images)
        # ============================================================
        self.uploads_bucket = s3.Bucket(
            self, "UploadsBucket",
            bucket_name=None,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ExpireUploads",
                    expiration=Duration.days(90),
                ),
            ],
        )

        # ============================================================
        # Outputs
        # ============================================================
        cdk.CfnOutput(self, "ConversationsTableName",
                       value=self.conversations_table.table_name,
                       description="DynamoDB Conversations table name")
        cdk.CfnOutput(self, "CacheTableName",
                       value=self.cache_table.table_name,
                       description="DynamoDB Cache table name")
        cdk.CfnOutput(self, "AudioBucketName",
                       value=self.audio_bucket.bucket_name,
                       description="S3 Audio bucket name")
        cdk.CfnOutput(self, "UploadsBucketName",
                       value=self.uploads_bucket.bucket_name,
                       description="S3 Uploads bucket name")
