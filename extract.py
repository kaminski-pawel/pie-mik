import bs4
import requests
import typing as t
from config import CONSTANTS


class LinksRetriever:
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
        return requests.get(CONSTANTS["PIE_MIK_URL"], headers=headers)

    def _parse_response(self, r: requests.models.Response) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(r.content, "html.parser")

    def _get_links_to_xlsx(self, soup: bs4.BeautifulSoup) -> t.List[str]:
        return [
            link["href"]
            for link in soup.find_all("a", href=True)
            if link["href"].endswith(".xlsx")
        ]
