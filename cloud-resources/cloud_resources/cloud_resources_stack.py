from aws_cdk import (
    App,
    Aws,
    CfnOutput,
    Stack,
    aws_iam as iam,
    aws_sns as sns,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3objectlambda as s3_object_lambda,
    aws_secretsmanager as secrets_manager,
    aws_lambda_event_sources
)

class CloudResourcesStack(Stack):

    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        # Set up a bucket
        bucket = s3.Bucket(self, "PiImageBucket",
                           bucket_name="pi-fr-images",
                           access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                           encryption=s3.BucketEncryption.S3_MANAGED,
                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL)

        # Configure the lambda Event Source
        s3_event_source = aws_lambda_event_sources.S3EventSource(bucket, events=[s3.EventType.OBJECT_CREATED_PUT])

        # Creating the Pi "User" Creds
        pi_user = iam.User(self, "PiUser", user_name="pi_user")
        access_key = iam.AccessKey(self, "PiAccessKey", user=pi_user)

        # Storing the pi user creds as secrets
        secrets_manager.Secret(self,
                               "PiUserAccessKeySecret",
                               secret_name="pi-user-secret",
                               secret_string_value=access_key.secret_access_key)

        # Create the topic which will send the text message notifications
        message_topic = sns.Topic(self, "PiMessageTopic", topic_name="pi-messages")

        # Give the pi user permission to PUT objects in the bucket
        pi_user.attach_inline_policy(
            iam.Policy(self, "pi-fr-user-policy",
                       statements=[
                           iam.PolicyStatement(
                               actions=["kms:GenerateDataKey",
                                        "s3:PutObject",
                                        "s3:PutObjectAcl",
                                        "s3:GetObject",
                                        "s3:GetObjectAcl",
                                        "s3:DeleteObject"],
                               resources=[bucket.bucket_arn],
                               effect=iam.Effect.ALLOW
                           ),
                           iam.PolicyStatement(
                               actions=['sns:Publish'],
                               resources=[message_topic.topic_arn],
                               effect=iam.Effect.ALLOW
                           )
                       ]))

        # Create the Lambda function which will build and send the text message
        # send_message_lambda = _lambda.Function(
        #    self,
        #    'SendMessageLambda',
        #    function_name='pi-send-message',
        #    runtime=_lambda.Runtime.PYTHON_3_8,
        #    code=_lambda.Code.from_asset('cloud_resources/lambda'),
        #    handler='send-message-lambda.handler',
        # )

        # Add ability to publish to the topic
        # send_message_lambda.add_to_role_policy(iam.PolicyStatement(
        #            actions=['sns:Publish'],
        #            resources=[message_topic.topic_arn],
        #            effect=iam.Effect.ALLOW
        #        ))

        # Push the message topic ARN into the lambda method
        # send_message_lambda.add_environment('PI_MESSAGE_TOPIC_ARN', message_topic.topic_arn)

        # Wire up the s3 bucket to trigger the lambda
        # send_message_lambda.add_event_source(s3_event_source)

        # Print out the access key
        CfnOutput(self, "PiUserAccessKeyId", value=access_key.access_key_id)
