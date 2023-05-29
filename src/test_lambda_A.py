import responses
from src.config import CONSTANTS
from src.extract import LinksRetriever


def _open_txt(fn: str) -> str:
    with open(fn) as f:
        return f.read()


@responses.activate
def test_link_extraction():
    responses.add(
        responses.GET,
        CONSTANTS["PIE_MIK_URL"],
        _open_txt(CONSTANTS["PIE_MIK_RESP_MOCK_FILE"]),
        status=200,
    )
    links = LinksRetriever().retrieve()
    should_be = [
        "https://pie.net.pl/wp-content/uploads/2023/05/MIK-w-czasie05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/Komponenty-MIK05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/MIK-wg-wielkosci-firm05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/MIK-wg-branz05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/Bariery-dla-firm05.xlsx",
        "https://pie.net.pl/wp-content/uploads/2023/05/Wyniki-badan-ankietowych-firm05.xlsx",
    ]
    assert len(links) == len(should_be)
    for l in links:
        assert l in should_be
