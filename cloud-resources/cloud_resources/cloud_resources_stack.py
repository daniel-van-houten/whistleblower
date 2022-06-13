from aws_cdk import (
    App,
    Aws,
    CfnOutput,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3objectlambda as s3_object_lambda,
    aws_secretsmanager as secrets_manager,
    SecretValue
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

        # Creating the Pi "User" Creds
        pi_user = iam.User(self, "PiUser", user_name="pi_user")
        access_key = iam.AccessKey(self, "PiAccessKey", user=pi_user)

        # Storing the pi user creds as secrets
        access_key_secret_secret = secrets_manager.Secret(self,
                                                          "PiUserAccessKeySecret",
                                                          secret_name="pi-user-secret",
                                                          secret_string_value=access_key.secret_access_key)

        # Create an administrative policy to retrieve the secret created for pi user
        read_secret_policy = iam.Policy(self, "PiAdminSecretPolicy",
                                        policy_name="read_pi_project_secrets",
                                        statements=[iam.PolicyStatement(
                                            effect=iam.Effect.ALLOW,
                                            actions=["secretsmanager:GetResourcePolicy",
                                                     "secretsmanager:GetSecretValue",
                                                     "secretsmanager:DescribeSecret",
                                                     "secretsmanager:ListSecretVersionIds"],
                                            resources=[access_key_secret_secret.secret_full_arn]),
                                            iam.PolicyStatement(
                                                effect=iam.Effect.ALLOW,
                                                actions=["secretsmanager:ListSecrets"],
                                                resources=["*"])
                                        ])

        # Give the pi user permission to PUT objects in the bucket
        pi_user.attach_inline_policy(
            iam.Policy(self, "pi-fr-user-policy",
                       statements=[iam.PolicyStatement(
                           actions=["s3:PutObject"],
                           resources=[bucket.bucket_arn]
                       )]))

        CfnOutput(self, "PiUserAccessKeyId", value=access_key.access_key_id)
