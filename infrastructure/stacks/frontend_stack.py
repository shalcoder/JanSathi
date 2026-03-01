"""
JanSathi Frontend Stack — S3 + CloudFront
From AWS_PRODUCTION_ARCHITECTURE.md Section 2: Edge Layer
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class FrontendStack(Stack):
    """
    Creates:
    - S3 bucket (static hosting, private)
    - CloudFront distribution (HTTPS, Brotli, OAI)
    - Origin Access Identity for secure S3 access
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api_url: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ============================================================
        # S3: Frontend Assets Bucket
        # ============================================================
        self.frontend_bucket = s3.Bucket(
            self, "FrontendBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # ============================================================
        # CloudFront: CDN Distribution
        # ============================================================
        self.distribution = cloudfront.Distribution(
            self, "FrontendDistribution",
            comment="JanSathi Frontend CDN",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    self.frontend_bucket
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,  # Brotli + gzip
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
            ),
            # SPA fallback: all routes → index.html
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
            ],
            default_root_object="index.html",
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Low cost
        )

        # ============================================================
        # Outputs
        # ============================================================
        cdk.CfnOutput(self, "FrontendUrl",
                       value=f"https://{self.distribution.domain_name}",
                       description="CloudFront frontend URL")
        cdk.CfnOutput(self, "FrontendBucketName",
                       value=self.frontend_bucket.bucket_name,
                       description="S3 bucket for frontend assets")
        cdk.CfnOutput(self, "DistributionId",
                       value=self.distribution.distribution_id,
                       description="CloudFront distribution ID")
        cdk.CfnOutput(self, "ApiEndpoint",
                       value=api_url,
                       description="Backend API Gateway URL")
