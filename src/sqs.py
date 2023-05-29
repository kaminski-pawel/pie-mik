import boto3
from botocore.client import BaseClient
import dotenv
import os
import typing as t
import uuid

dotenv.load_dotenv()  # TODO: replace virtual env with sth more secure


class ResponseWrapper:
    """
    Wrapper around responses from AWS SQS
    in order to simplify accesing response properties.
    """

    def __init__(self, response):
        self.response = response

    @property
    def msg_body(self):
        return self.response["Messages"][0]["Body"]

    @property
    def status_code(self):
        return self.response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    def is_ok(self):
        return self.status_code == 200

    def get_receipt_handle(self):
        try:
            return self.response["Messages"][0]["ReceiptHandle"]
        except KeyError:
            return None


def get_client() -> BaseClient:
    """
    Returns a low-level client representing Amazon Simple Queue Service (SQS).
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#client
    """
    return boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_SECRET_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION_NAME"),
    )


def send_message(
    client: BaseClient,
    message_body: str,
) -> t.Dict[str, t.Any]:
    """
    Delivers a message to the specified queue.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.send_message
    """
    message_group_id = uuid.uuid4().hex
    return client.send_message(
        QueueUrl=os.getenv("SQS_ENDPOINT_URL"),
        MessageBody=message_body,
        MessageDeduplicationId=str(hash(message_body)),
        MessageGroupId=message_group_id,
    )


def _split_into_chunks(lst: t.List[t.Any], chunk_size: int) -> t.List[t.List[t.Any]]:
    """
    Splits a single list into many lists of length not greater than `chunk_size`.
    """
    return [lst[x : x + chunk_size] for x in range(0, len(lst), chunk_size)]


def _add_sqs_metadata(
    entry: str,
    message_group_id: str,
) -> t.Dict[str, str]:
    return {
        "Id": str(hash(entry)),
        "MessageBody": entry,
        "MessageDeduplicationId": str(hash(entry)),
        "MessageGroupId": message_group_id,
    }


def send_message_batch(client: BaseClient, messages: t.List[t.Dict[str, str]]):
    """
    Delivers up to ten messages to the specified queue.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.send_message_batch
    """
    max_batch_size = 10
    group_id = uuid.uuid4().hex
    responses = []
    for batch in _split_into_chunks(messages, max_batch_size):
        responses.append(
            ResponseWrapper(
                client.send_message_batch(
                    QueueUrl=os.getenv("SQS_ENDPOINT_URL"),
                    Entries=[_add_sqs_metadata(entry, group_id) for entry in batch],
                )
            )
        )
    return responses


def receive_message(client: BaseClient) -> ResponseWrapper:
    """
    Retrieves one or more messages (up to 10), from the specified queue.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.receive_message
    """
    return ResponseWrapper(
        client.receive_message(
            QueueUrl=os.getenv("SQS_ENDPOINT_URL"),
        )
    )


def delete_message(client: BaseClient, receipt_handle: str) -> None:
    """
    Deletes the specified message from the specified queue.
    To select the message to delete, use the ReceiptHandle of the message.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.delete_message
    """
    return ResponseWrapper(
        client.delete_message(
            QueueUrl=os.getenv("SQS_ENDPOINT_URL"),
            ReceiptHandle=receipt_handle,
        )
    )
