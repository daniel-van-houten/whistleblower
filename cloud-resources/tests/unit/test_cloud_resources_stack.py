import aws_cdk as core
import aws_cdk.assertions as assertions

from cloud_resources.cloud_resources_stack import CloudResourcesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cloud_resources/cloud_resources_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CloudResourcesStack(app, "cloud-resources")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
