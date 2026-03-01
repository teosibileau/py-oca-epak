"""Tests for caching functionality."""

from unittest.mock import MagicMock


class TestCaching:
    """Tests for caching behavior."""

    def test_get_provincias_caches_result(self, oca_service):
        """Verify getProvincias caches result on first call."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetProvinciasResult = """<?xml version="1.0" encoding="utf-8"?>
        <Provincias>
            <Provincia>
                <IdProvincia>1</IdProvincia>
                <Descripcion>TEST PROVINCE</Descripcion>
            </Provincia>
        </Provincias>"""
        mock_client.GetProvincias.return_value = mock_response

        result1 = oca_service.getProvincias()
        assert mock_client.GetProvincias.call_count == 1

        result2 = oca_service.getProvincias()
        assert mock_client.GetProvincias.call_count == 1
        assert result1 is result2

    def test_get_localidades_by_provincia_caches_by_id(self, oca_service):
        """Verify getLocalidadesByProvincia caches per province ID."""
        mock_client = oca_service._mock_client

        mock_response1 = MagicMock()
        mock_response1.GetLocalidadesByProvinciaResult = """<?xml version="1.0" encoding="utf-8"?>
        <Localidades>
            <Provincia>
                <Nombre>LOCALITY 1</Nombre>
            </Provincia>
        </Localidades>"""

        mock_response2 = MagicMock()
        mock_response2.GetLocalidadesByProvinciaResult = """<?xml version="1.0" encoding="utf-8"?>
        <Localidades>
            <Provincia>
                <Nombre>LOCALITY 2</Nombre>
            </Provincia>
        </Localidades>"""

        def mock_get_localidades(idProvincia):
            if idProvincia == 1:
                return mock_response1
            return mock_response2

        mock_client.GetLocalidadesByProvincia.side_effect = mock_get_localidades

        result1 = oca_service.getLocalidadesByProvincia(1)
        assert mock_client.GetLocalidadesByProvincia.call_count == 1

        result2 = oca_service.getLocalidadesByProvincia(1)
        assert mock_client.GetLocalidadesByProvincia.call_count == 1
        assert result1 is result2

        result3 = oca_service.getLocalidadesByProvincia(2)
        assert mock_client.GetLocalidadesByProvincia.call_count == 2
        assert result3[0]["Nombre"] == "LOCALITY 2"

    def test_clear_cache_removes_cached_data(self, oca_service):
        """Verify clear_cache removes all cached data."""
        mock_client = oca_service._mock_client

        mock_response_prov = MagicMock()
        mock_response_prov.GetProvinciasResult = "<Provincias></Provincias>"
        mock_client.GetProvincias.return_value = mock_response_prov

        mock_response_loc = MagicMock()
        mock_response_loc.GetLocalidadesByProvinciaResult = (
            "<Localidades></Localidades>"
        )
        mock_client.GetLocalidadesByProvincia.return_value = mock_response_loc

        oca_service.getProvincias()
        oca_service.getLocalidadesByProvincia(1)

        assert hasattr(oca_service, "_provincias_cache")
        assert hasattr(oca_service, "_localidades_cache")

        oca_service.clear_cache()

        assert not hasattr(oca_service, "_provincias_cache")
        assert not hasattr(oca_service, "_localidades_cache")

        oca_service.getProvincias()
        assert mock_client.GetProvincias.call_count == 2
