import boto3
import bs4
import dotenv
import os
import logging
import json
import requests
import typing as t


dotenv.load_dotenv()


def lambda_handler(event, context):
    set_logger()
    links = LinksRetriever().retrieve()
    logging.info("Retrieved links: {}".format(json.dumps(links)))
    responses = sqs_send_message_batch(links)
    responses_as_str = json.dumps(responses)
    logging.info("SQS send message batch responses: {}".format(responses_as_str))
    return {
        "statusCode": 200,
        "body": responses_as_str
    }

def set_logger():
    if logging.getLogger().hasHandlers():
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

def sqs_send_message_batch(messages: t.List[str]):
    """
    Delivers up to ten messages to the specified queue.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.send_message_batch
    """
    max_batch_size = 10
    responses = []
    client = boto3.client("sqs")
    batches = [messages[x : x + max_batch_size] for x in range(0, len(messages), max_batch_size)]
    for batch in batches:
        responses.append(client.send_message_batch(
            QueueUrl=os.getenv("SQS_ENDPOINT_URL"),
            Entries=[
                {
                    "Id": str(hash(entry)),
                    "MessageBody": entry,
                } for entry in batch
            ],
        ))
    return responses


class LinksRetriever:
    PIE_MIK_URL= "https://mik.pie.net.pl/"

    def retrieve(self) -> t.List[str]:
        """
        Retrieves all links ending with .xlsx. E.g.:
        - https://pie.net.pl/wp-content/uploads/2023/05/MIK-w-czasie05.xlsx
        - https://pie.net.pl/wp-content/uploads/2023/05/Komponenty-MIK05.xlsx
        - https://pie.net.pl/wp-content/uploads/2023/05/MIK-wg-wielkosci-firm05.xlsx
        - https://pie.net.pl/wp-content/uploads/2023/05/MIK-wg-branz05.xlsx
        - https://pie.net.pl/wp-content/uploads/2023/05/Bariery-dla-firm05.xlsx
        - https://pie.net.pl/wp-content/uploads/2023/05/Wyniki-badan-ankietowych-firm05.xlsx
        Examples of links not included are:
        - https://pie.net.pl/
        - https://www.bgk.pl/
        - https://pie.net.pl/wp-content/uploads/2022/06/Kwartalnik_MIK_2_2022.pdf
        - https://pie.net.pl/wp-content/uploads/2022/06/MIK_6-2022.pdf
        """
        return self._get_links_to_xlsx(self._parse_response(self._send_request()))

    def _send_request(self) -> requests.models.Response:
        headers = {
            "Connection": "keep-alive",
            "User-Agent": "mojeanalizy.pl agent",
            "From": "office@tipi.software",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "pl-PL,pl;q=0.9",
        }
        return requests.get(self.PIE_MIK_URL, headers=headers)

    def _parse_response(self, r: requests.models.Response) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(r.content, "html.parser")

    def _get_links_to_xlsx(self, soup: bs4.BeautifulSoup) -> t.List[str]:
        return [
            link["href"]
            for link in soup.find_all("a", href=True)
            if link["href"].endswith(".xlsx")
        ]
