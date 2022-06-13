import json
import urllib.parse
import boto3
import os

client = boto3.client('sns')


def handler(event, context):
    # Get the bucket name
    # bucket = event['Records'][0]['s3']['bucket']['name']

    # Get the file name
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    client.publish(
        TargetArn=os.environ.get('PI_MESSAGE_TOPIC_ARN'),
        Message="Intruder Detected!",
        MessageStructure='json'
    )

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        }
    }
