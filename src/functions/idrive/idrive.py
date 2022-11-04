import boto3

from ..utils.response import Response as Rs


# list all regions containing s3 buckets
regions = {
    "Oregon": "us-west-2",
    "Los Angeles": "us-west-1",
    "Virginia": "us-east-1",
    "Dallas": "us-east-2",
    "Phoenix": "us-west-3",
    "Chicago": "us-central-1",
    "San Jose": "us-central-2",
    "Miami": "us-south-1",
    "Montreal": "ca-central-1",
    "Ireland": "eu-west-1",
    "London": "eu-west-2",
    "Frankfurt": "eu-central-1",
    "Paris": "eu-west-3",
}




"""
endpoint = "https://k2e7.ldn.idrivee2-18.com"
s3 = boto3.client("s3", endpoint_url=endpoint)


def create_bucket(bucket_name):
    try:
        bucket = s3.create_bucket(Bucket=bucket_name)
        if bucket:
            return Rs.created(msg="Bucket created")
        return Rs.error(msg="Something went wrong")
    except Exception as e:
        return Rs.server_error(str(e))


def get_bucket(bucket_name):
    try:
        bucket = s3.head_bucket(Bucket=bucket_name)
        if bucket:
            return Rs.success(msg="Bucket found")
        else:
            return Rs.not_found(msg="Bucket not found")
    except Exception as e:
        return Rs.server_error(str(e))
"""