#!/usr/bin/env python3
import os
import aws_cdk as cdk

from infrastructure_stack import DocusealInfrastructureStack

app = cdk.App()

DocusealInfrastructureStack(
    app, 
    "DocusealInfrastructureStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)

app.synth()