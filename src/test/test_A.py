# pylint: disable=missing-function-docstring
import responses

from A.lambda_function import LinksRetriever

PIE_MIK_RESP_MOCK_FILE = "src/test/pie_mik_mock_resp.txt"


def _open_txt(file_name: str) -> str:
    with open(file_name, encoding="utf-8") as file:
        return file.read()


@responses.activate
def test_link_extraction() -> None:
    retriever = LinksRetriever()
    responses.add(
        responses.GET,
        retriever.PIE_MIK_URL,
        _open_txt(PIE_MIK_RESP_MOCK_FILE),
        status=200,
    )
    links = retriever.retrieve()
    should_be = [
        "https://pie.net.pl/wp-content/uploads/2023/05/MIK-w-czasie05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/Komponenty-MIK05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/MIK-wg-wielkosci-firm05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/MIK-wg-branz05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/Bariery-dla-firm05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/Wyniki-badan-ankietowych-firm05.xlsx",
    ]
    assert len(links) == len(should_be)
    for link in links:
        assert link in should_be
