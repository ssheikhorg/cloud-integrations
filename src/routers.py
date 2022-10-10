import boto3

from utils.response import get_success, get_error, get_not_found

endpoint = "https://k2e7.ldn.idrivee2-18.com"
s3 = boto3.client("s3", endpoint_url=endpoint)



def create_bucket(bucket_name):
    try:
        bucket = s3.create_bucket(Bucket=bucket_name)
        if bucket:
            return get_success("Bucket created successfully")
        else:
            return get_error("Bucket not created")
    except Exception as e:
        return get_error(str(e))


def get_bucket(bucket_name):
    try:
        bucket = s3.head_bucket(Bucket=bucket_name)
        if bucket:
            return get_success("Bucket found")
        else:
            return get_not_found("Bucket not found")
    except Exception as e:
        return get_error(str(e))
