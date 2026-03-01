"""Tests for tracking functionality."""

import pytest
from unittest.mock import MagicMock


class TestTracking:
    """Tests for tracking shipment status."""

    def test_tracking_envio_estado_actual_returns_tracking_data(self, oca_service):
        """Verify trackingEnvioEstadoActual returns current tracking status."""
        mock_client = oca_service._mock_client
        mock_result = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <NumeroEnvio>123456789</NumeroEnvio>
                <Estado>En transito</Estado>
                <Sucursal>BUENOS AIRES</Sucursal>
                <Fecha>2024-01-15T10:30:00-03:00</Fecha>
            </Table>
        </DataSet>"""
        mock_result.__getitem__.return_value = inner_mock
        mock_client.TrackingEnvio_EstadoActual.return_value = mock_result

        result = oca_service.trackingEnvioEstadoActual("123456789")

        assert len(result) == 1
        assert result[0]["NumeroEnvio"] == 123456789
        assert result[0]["Estado"] == b"En transito"
        assert result[0]["Sucursal"] == b"BUENOS AIRES"

    def test_tracking_envio_estado_actual_calls_with_envio_number(self, oca_service):
        """Verify trackingEnvioEstadoActual passes correct shipment number."""
        mock_client = oca_service._mock_client
        mock_result = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = "<DataSet></DataSet>"
        mock_result.__getitem__.return_value = inner_mock
        mock_client.TrackingEnvio_EstadoActual.return_value = mock_result

        oca_service.trackingEnvioEstadoActual("987654321")

        mock_client.TrackingEnvio_EstadoActual.assert_called_once_with(
            numeroEnvio="987654321"
        )

    def test_tracking_envio_estado_actual_empty_response(self, oca_service):
        """Verify trackingEnvioEstadoActual handles empty response."""
        mock_client = oca_service._mock_client
        mock_result = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = "<DataSet></DataSet>"
        mock_result.__getitem__.return_value = inner_mock
        mock_client.TrackingEnvio_EstadoActual.return_value = mock_result

        result = oca_service.trackingEnvioEstadoActual("000000000")

        assert result == []

    def test_tracking_envio_estado_actual_soap_error(self, oca_service):
        """Verify trackingEnvioEstadoActual handles SOAP errors."""
        mock_client = oca_service._mock_client
        mock_client.TrackingEnvio_EstadoActual.side_effect = Exception(
            "Invalid tracking number"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.trackingEnvioEstadoActual("INVALID")

        assert "Invalid tracking number" in str(exc_info.value)
