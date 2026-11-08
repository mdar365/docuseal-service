import os
import aws_cdk as cdk
from infrastructure_stack import DocusealInfrastructureStack

app = cdk.App()

DocusealInfrastructureStack(
    app,
    "DocusealInfrastructureStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION"),
    ),
)

app.synth()