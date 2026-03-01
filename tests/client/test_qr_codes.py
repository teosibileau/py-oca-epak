"""Tests for QR code generation and order consolidation."""

from unittest.mock import MagicMock


class TestQRCodes:
    """Tests for QR code generation and consolidation features."""

    def test_generate_qr_by_orden_de_retiro_returns_base64(self, oca_service):
        """Verify generateQrByOrdenDeRetiro returns base64 QR string."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GenerateQrByOrdenDeRetiroResult = "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAElJREFUOI1j/P///38GMgAxWZgYGRgYnEY1DGJgYGBg+//z/39Uw1AMBwMYGBgYGP7//8+AFQxDMBwMYGBgYGD4//8/AxYwDMBwMYGBgYEBAF/3Jv4i2bNHAAAAAElFTkSuQmCC"
        mock_client.GenerateQrByOrdenDeRetiro.return_value = mock_response

        result = oca_service.generateQrByOrdenDeRetiro("12345")

        assert isinstance(result, str)
        assert len(result) > 0
        mock_client.GenerateQrByOrdenDeRetiro.assert_called_once_with(
            usr="test_user", psw="test_pass", idOrdenDeRetiro="12345"
        )

    def test_generate_qr_para_paquetes_returns_base64(self, oca_service):
        """Verify generateQrParaPaquetes returns base64 QR string."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GenerateQRParaPaquetesResult = "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAElJREFUOI1j/P///38GMgAxWZgYGRgYnEY1DGJgYGBg+//z/39Uw1AMBwMYGBgYGP7//8+AFQxDMBwMYGBgYGD4//8/AxYwDMBwMYGBgYEBAF/3Jv4i2bNHAAAAAElFTkSuQmCC"
        mock_client.GenerateQRParaPaquetes.return_value = mock_response

        result = oca_service.generateQrParaPaquetes("987654321", "PKG001")

        assert isinstance(result, str)
        assert len(result) > 0
        mock_client.GenerateQRParaPaquetes.assert_called_once_with(
            usr="test_user",
            psw="test_pass",
            numeroDeEnvio="987654321",
            idpaquete="PKG001",
        )

    def test_generate_list_qr_por_envio_returns_list(self, oca_service):
        """Verify generateListQrPorEnvio returns list of base64 QR strings."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GenerateListQrPorEnvioResult = [
            "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAElJREFUOI1j/P///38GMgAxWZgYGRgYnEY1DGJgYGBg+//z/39Uw1AMBwMYGBgYGP7//8+AFQxDMBwMYGBgYGD4//8/AxYwDMBwMYGBgYEBAF/3Jv4i2bNHAAAAAElFTkSuQmCC",
            "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAElJREFUOI1j/P///38GMgAxWZgYGRgYnEY1DGJgYGBg+//z/39Uw1AMBwMYGBgYGP7//8+AFQxDMBwMYGBgYGD4//8/AxYwDMBwMYGBgYEBAF/3Jv4i2bNHAAAAAElFTkSuQmCC",
        ]
        mock_client.GenerateListQrPorEnvio.return_value = mock_response

        result = oca_service.generateListQrPorEnvio("555666777")

        assert isinstance(result, list)
        assert len(result) == 2
        mock_client.GenerateListQrPorEnvio.assert_called_once_with(
            usr="test_user", psw="test_pass", numeroDeEnvio="555666777"
        )

    def test_generar_consolidacion_de_ordenes_returns_dict(self, oca_service):
        """Verify generarConsolidacionDeOrdenesDeRetiro returns parsed result."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GenerarConsolidacionDeOrdenesDeRetiroResult = "CONS123|3"
        mock_client.GenerarConsolidacionDeOrdenesDeRetiro.return_value = mock_response

        result = oca_service.generarConsolidacionDeOrdenesDeRetiro(
            ["123", "456", "789"]
        )

        assert isinstance(result, dict)
        assert result["IdDeConsolidacion"] == "CONS123"
        assert result["CantidadDeOrdenes"] == 3
        mock_client.GenerarConsolidacionDeOrdenesDeRetiro.assert_called_once_with(
            usr="test_user", psw="test_pass", ordenesDeRetiro="123,456,789"
        )

    def test_generar_consolidacion_single_order(self, oca_service):
        """Verify consolidation works with single order."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GenerarConsolidacionDeOrdenesDeRetiroResult = "CONS456|1"
        mock_client.GenerarConsolidacionDeOrdenesDeRetiro.return_value = mock_response

        result = oca_service.generarConsolidacionDeOrdenesDeRetiro(["999"])

        assert result["IdDeConsolidacion"] == "CONS456"
        assert result["CantidadDeOrdenes"] == 1

    def test_generar_consolidacion_empty_response(self, oca_service):
        """Verify consolidation handles empty/invalid response."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GenerarConsolidacionDeOrdenesDeRetiroResult = ""
        mock_client.GenerarConsolidacionDeOrdenesDeRetiro.return_value = mock_response

        result = oca_service.generarConsolidacionDeOrdenesDeRetiro(["111"])

        assert result["IdDeConsolidacion"] == ""
        assert result["CantidadDeOrdenes"] == 0
