import os
import sys
from typing import List
import boto3
from dotenv import load_dotenv
load_dotenv()

class AWSConnectionConfig:

    s3_client=None
    s3_resource = None
    def __init__(self, region_name):

        if AWSConnectionConfig.s3_resource==None or AWSConnectionConfig.s3_client==None:
            __access_key_id = os.environ["AWS_ACCESS_KEY_ID_ENV_KEY"]
            __secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY_ENV_KEY"]
            if __access_key_id is None:
                raise Exception(f"Environment variable: AWS_ACCESS_KEY_ID_ENV_KEY is not not set.")
            if __secret_access_key is None:
                raise Exception(f"Environment variable: AWS_SECRET_ACCESS_KEY_ENV_KEY is not set.")
        
            AWSConnectionConfig.s3_resource = boto3.resource('s3',
                                            aws_access_key_id=__access_key_id,
                                            aws_secret_access_key=__secret_access_key,
                                            region_name=region_name
                                            )
            AWSConnectionConfig.s3_client = boto3.client('s3',
                                        aws_access_key_id=__access_key_id,
                                        aws_secret_access_key=__secret_access_key,
                                        region_name=region_name
                                        )
        self.s3_resource = AWSConnectionConfig.s3_resource
        self.s3_client = AWSConnectionConfig.s3_client

class SimpleStorageService:

    def __init__(self, region_name, s3_bucket_name):
        aws_connection_config = AWSConnectionConfig(region_name=region_name)
        self.client = aws_connection_config.s3_client
        self.resource = aws_connection_config.s3_resource
        response = self.client.list_buckets()
        available_buckets = [bucket['Name'] for bucket in response['Buckets']]
        if s3_bucket_name not in available_buckets:
            location = {'LocationConstraint': region_name}
            self.client.create_bucket(Bucket=s3_bucket_name,
                                      CreateBucketConfiguration=location)
        self.bucket = self.resource.Bucket(s3_bucket_name)
        self.bucket_name = s3_bucket_name

    def list_files(self, key: str, extension: str = "csv") -> List[str]:
        try:
            if not key.endswith("/"):
                key = f"{key}/"
            paths = []
            for key_summary in self.bucket.objects.filter(Prefix=key):
                if key_summary.key.endswith(extension):
                    paths.append(key_summary.key)
            return paths
        except Exception as e:
            raise e

    def delete_file(self, key) -> bool:
        try:
            self.resource.Object(self.bucket_name, key).delete()
            return True
        except Exception as e:
            raise e

    def copy(self, source_key: str, destination_dir_key: str) -> bool:
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }

            self.client.copy(copy_source,
                             self.bucket_name,
                             os.path.join(destination_dir_key,
                                          os.path.dirname(source_key)))
            return True

        except Exception as e:
            raise e

    def move(self, source_key, destination_dir_key) -> bool:
        try:
            self.copy(source_key, destination_dir_key)
            return self.delete_file(key=source_key)
        except Exception as e:
            raise e

    def download_file(self, s3_key, local_file_path):
        try:
            self.client.download_file(self.bucket_name, s3_key, local_file_path)
        except Exception as e:
            raise e

    def upload_file(self, s3_key, local_file_path):
        try:
            self.client.upload_file(local_file_path, self.bucket_name, s3_key)
        except Exception as e:
            raise e
