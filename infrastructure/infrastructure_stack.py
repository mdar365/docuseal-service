from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
)
from constructs import Construct

class DocusealInfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the S3 Bucket for document processing
        pdf_bucket = s3.Bucket(
            self,
            "DocuSealPdfBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,  # Convenient for dev/testing cleanup
            auto_delete_objects=True,             # Clears bucket on stack destruction in dev
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.GET,
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.POST,
                    ],
                    allowed_origins=["*"],  # Restrict to your frontend domain in production
                    allowed_headers=["*"],
                )
            ],
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="AutoDeleteUploadsAfter24Hours",
                    prefix="uploads/",
                    expiration=Duration.days(1),
                )
            ],
        )