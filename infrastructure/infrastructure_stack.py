from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambda_python,
    aws_s3_notifications as s3n,
)
from constructs import Construct

class DocusealInfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket
        bucket = s3.Bucket(
            self, "DocuSealPdfBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST],
                allowed_origins=["*"],
                allowed_headers=["*"]
            )],
            lifecycle_rules=[s3.LifecycleRule(
                id="AutoDeleteUploadsAfter24Hours",
                prefix="uploads/",
                expiration=Duration.days(1)
            )],
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Lambda Handler with automated Python asset bundling
        watermark_lambda = _lambda.Function(
            self, "WatermarkProcessorHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handlers.watermark_processor.lambda_handler",
            code=_lambda.Code.from_asset("../src"),
            timeout=Duration.seconds(30),
            memory_size=512
        )

        # Grant Read/Write S3 permissions to Lambda
        bucket.grant_read_write(watermark_lambda)

        # Configure S3 Event Notification
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(watermark_lambda),
            s3.NotificationKeyFilter(prefix="uploads/", suffix=".pdf")
        )