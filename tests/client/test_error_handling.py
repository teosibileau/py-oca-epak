"""Tests for error handling scenarios."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock
from ocaepak.client import OcaService
from tests.client.conftest import create_xml_mock, create_soap_mock


class TestErrorHandling:
    """Tests for error scenarios and exception handling."""

    def test_anular_orden_generada_soap_fault(self, oca_service):
        """Verify anularOrdenGenerada handles SOAP fault gracefully."""
        mock_client = oca_service._mock_client
        mock_client.AnularOrdenGenerada.side_effect = Exception(
            "SOAP Fault: Invalid order"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.anularOrdenGenerada(12345)

        assert "SOAP Fault" in str(exc_info.value)

    def test_anular_orden_generada_network_error(self, oca_service):
        """Verify anularOrdenGenerada handles network errors."""
        mock_client = oca_service._mock_client
        mock_client.AnularOrdenGenerada.side_effect = ConnectionError("Network timeout")

        with pytest.raises(ConnectionError) as exc_info:
            oca_service.anularOrdenGenerada(12345)

        assert "Network timeout" in str(exc_info.value)

    def test_anular_orden_generada_authentication_error(self, oca_service):
        """Verify anularOrdenGenerada handles authentication failure."""
        mock_client = oca_service._mock_client
        mock_client.AnularOrdenGenerada.side_effect = Exception("Authentication failed")

        with pytest.raises(Exception) as exc_info:
            oca_service.anularOrdenGenerada(12345)

        assert "Authentication failed" in str(exc_info.value)

    def test_centro_costo_invalid_operativa(self, oca_service):
        """Verify centroCostoPorOperativa handles invalid operativa error."""
        mock_client = oca_service._mock_client
        mock_client.GetCentroCostorPorOperativa.side_effect = Exception(
            "Invalid operativa"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.centroCostoPorOperativa(99999)

        assert "Invalid operativa" in str(exc_info.value)

    def test_centros_de_imposicion_empty_response(self, oca_service):
        """Verify centrosDeImposicion handles empty response."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicion.return_value = create_soap_mock(
            "<DataSet></DataSet>"
        )

        result = oca_service.centrosDeImposicion()

        assert result == []

    def test_centros_de_imposicion_por_cp_invalid_cp(self, oca_service):
        """Verify centrosDeImposicionPorCP handles invalid postal code."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionPorCP.side_effect = Exception(
            "Invalid postal code"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.centrosDeImposicionPorCP(999999)

        assert "Invalid postal code" in str(exc_info.value)

    def test_ingresar_or_template_render_error(self, oca_service, mock_logger):
        """Verify ingresarOR handles Jinja2 template rendering errors."""
        invalid_compra = {"invalid": "data"}

        with pytest.raises(Exception) as exc_info:
            oca_service.ingresarOR(invalid_compra, 3, 1)

        assert (
            "retiro" in str(exc_info.value).lower()
            or "undefined" in str(exc_info.value).lower()
        )

    def test_ingresar_or_soap_fault(self, oca_service, sample_compra_data, mock_logger):
        """Verify ingresarOR handles SOAP fault during submission."""
        mock_client = oca_service._mock_client
        mock_client.IngresoOR.side_effect = Exception("SOAP Fault: Invalid XML")

        with pytest.raises(Exception) as exc_info:
            oca_service.ingresarOR(sample_compra_data, 3, 1)

        assert "SOAP Fault" in str(exc_info.value)

    def test_ingresar_or_missing_required_fields(self, oca_service, mock_logger):
        """Verify ingresarOR handles missing required fields in compra."""
        incomplete_compra = {}

        with pytest.raises(Exception) as exc_info:
            oca_service.ingresarOR(incomplete_compra, 3, 1)

        assert (
            "retiro" in str(exc_info.value).lower()
            or "undefined" in str(exc_info.value).lower()
        )

    def test_estado_ultimos_envios_invalid_date_range(self, oca_service):
        """Verify estadoUltimosEnvios handles invalid date range."""
        mock_client = oca_service._mock_client
        mock_client.GetEnviosUltimoEstado.side_effect = Exception("Invalid date range")

        from_date = datetime(2024, 1, 20)
        to_date = datetime(2024, 1, 15)

        with pytest.raises(Exception) as exc_info:
            oca_service.estadoUltimosEnvios(["72771"], from_date, to_date)

        assert "Invalid date range" in str(exc_info.value)

    def test_tarifar_envio_corporativo_invalid_weight(self, oca_service):
        """Verify tarifarEnvioCorporativo handles invalid weight."""
        mock_client = oca_service._mock_client
        mock_client.Tarifar_Envio_Corporativo.side_effect = Exception("Invalid weight")

        with pytest.raises(Exception) as exc_info:
            oca_service.tarifarEnvioCorporativo(-1, 100, 1000, 5000, 1, 72771)

        assert "Invalid weight" in str(exc_info.value)

    def test_tarifar_envio_corporativo_invalid_cp(self, oca_service):
        """Verify tarifarEnvioCorporativo handles invalid postal codes."""
        mock_client = oca_service._mock_client
        mock_client.Tarifar_Envio_Corporativo.side_effect = Exception(
            "Invalid postal code"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.tarifarEnvioCorporativo(5.0, 100, 0, 0, 1, 72771)

        assert "Invalid postal code" in str(exc_info.value)

    def test_tracking_or_invalid_orden_retiro(self, oca_service):
        """Verify trackingOR handles invalid orden retiro number."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_OrdenRetiro.side_effect = Exception("Order not found")

        with pytest.raises(Exception) as exc_info:
            oca_service.trackingOR(0)

        assert "Order not found" in str(exc_info.value)

    def test_tracking_pieza_not_found(self, oca_service):
        """Verify tracking methods handle piece not found error."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_Pieza.side_effect = Exception("Piece not found")

        with pytest.raises(Exception) as exc_info:
            oca_service.trackingPiezaConID("INVALID")

        assert "Piece not found" in str(exc_info.value)

    def test_tracking_pieza_empty_response(self, oca_service):
        """Verify tracking methods handle empty tracking response."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_Pieza.return_value = create_soap_mock(
            "<DataSet></DataSet>"
        )

        result = oca_service.trackingPiezaConID("123456789")

        assert result == []

    def test_iterateresult_handles_xml_parsing_error(self):
        """Verify iterateresult handles malformed XML."""
        mock_xml_result = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = "<invalid>xml</DataSet>"
        mock_xml_result.__getitem__.return_value = inner_mock

        with pytest.raises(Exception):
            OcaService.iterateresult("BadResult", mock_xml_result)

    def test_iterateresult_handles_missing_required_field(self):
        """Verify iterateresult handles missing expected fields."""
        mock_xml_result = create_xml_mock(
            "<DataSet><Table><Nombre>Test</Nombre></Table></DataSet>"
        )

        result = OcaService.iterateresult("Result", mock_xml_result)

        assert len(result) == 1
        assert result[0]["Nombre"] == b"Test"

    def test_iterateresult_handles_invalid_numeric_value(self):
        """Verify iterateresult handles non-numeric value in numeric field."""
        xml_with_bad_number = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <Numero>not-a-number</Numero>
            </Table>
        </DataSet>"""
        mock_xml_result = create_xml_mock(xml_with_bad_number)

        with pytest.raises(ValueError):
            OcaService.iterateresult("BadNum", mock_xml_result)

    def test_iterateresult_handles_malformed_datetime(self):
        """Verify error handling for invalid datetime format."""
        xml_with_bad_date = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <fecha>invalid-date</fecha>
            </Table>
        </DataSet>"""
        mock_xml_result = create_xml_mock(xml_with_bad_date)

        with pytest.raises(ValueError):
            OcaService.iterateresult("BadDateResult", mock_xml_result)
