from goifer_test import GoiferTestCase
from goifer.client import GoiferClient
import responses

SERVICE_URL = 'https://ws.parlament.ch/odata.svc'


class TestClient(SwissParlTestCase):
    @responses.activate
    def test_get_overview(self, metadata):
        responses.add(
            responses.GET,
            f"{SERVICE_URL}/$metadata",
            content_type='text/xml',
            body=metadata,
            status=200
        )
        client = GoiferClient()
        indexes = client.get_indexes()
        assert isinstance(indexes, dict), "indexes is not a dict"
        assert len(indexes) == 44
