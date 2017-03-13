import boto3
elb = boto3.client('elb')
print(elb.describe_load_balancers())

