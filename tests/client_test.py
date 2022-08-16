import pytest
from conftest import fixture_content
from goifer.client import Client
import responses


class TestClient:
    @pytest.fixture
    def wahlkreise(self):
        return fixture_content("wahlkreise.xml")

    @responses.activate
    def test_indexes(self):
        client = Client("canton_zurich")
        indexes = client.indexes()
        assert isinstance(indexes, list), "indexes is not a list"
        assert len(indexes) == 11

    @responses.activate
    def test_search_wahlkreis(self, wahlkreise):
        responses.add(
            responses.GET,
            "https://parlzhcdws.cmicloud.ch/parlzh2/cdws/Index/WAHLKREISE/searchdetails",
            content_type="text/xml",
            body=wahlkreise,
            status=200,
        )
        client = Client("canton_zurich")
        results = client.search("Wahlkreise", "seq > 0")
        wahlkreis = results[0]

        assert wahlkreis["name"] == "I      Zürich 1+2"
