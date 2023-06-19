# pylint: disable=invalid-name, missing-function-docstring
import logging
import os
import typing as t

import boto3
import botocore
import dotenv
import urllib3

dotenv.load_dotenv()


def lambda_handler(event, context) -> t.Dict[str, t.Any]:
    set_logger()
    try:
        logging.info("Received for download: %s", event["Records"][0]["body"])
        file_url = event["Records"][0]["body"]
        obj_name = "/".join(file_url.split("/")[-3:])
        upload_file_to_s3(file_url, os.getenv("S3_PIE_MIK_LAMBDA_B_TARGET"), obj_name)
        logging.info("Sucessfuly downloaded: %s", event["Records"][0]["body"])
        return {"statusCode": 200, "body": "File successfully uploaded."}
    except (IndexError, KeyError) as e:
        logging.exception(e)
        logging.critical(e, exc_info=True)
        return {"statusCode": 400, "body": "IndexError or KeyError"}
    except botocore.exceptions.ClientError as e:
        logging.exception(e)
        logging.critical(e, exc_info=True)
        return {"statusCode": 401, "body": "botocore.exceptions.ClientError"}


def set_logger() -> None:
    if logging.getLogger().hasHandlers():
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)


def upload_file_to_s3(file_url: str, bucket_name: str, obj_name: str) -> None:
    """
    Upload a file-like object (in binary mode) to S3. This is managed transfer
    which will perform a multipart upload in multiple threads if necessary.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/upload_fileobj.html

    For urllib3.PoolManager see:
    https://urllib3.readthedocs.io/en/stable/reference/urllib3.poolmanager.html
    """
    client = boto3.client("s3")
    http = urllib3.PoolManager()
    client.upload_fileobj(http.request("GET", file_url), bucket_name, obj_name)
