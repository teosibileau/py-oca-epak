"""Tests for label operations."""

from unittest.mock import MagicMock


class TestLabels:
    """Tests for label generation and retrieval methods."""

    def test_get_css_de_etiquetas_returns_string(self, oca_service):
        """Verify getCSSDeEtiquetasPorOrdenOrNumeroEnvio returns CSS string."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetCSSDeEtiquetasPorOrdenOrNumeroEnvioResult = (
            "body { font-family: Arial; }"
        )
        mock_client.GetCSSDeEtiquetasPorOrdenOrNumeroEnvio.return_value = mock_response

        result = oca_service.getCSSDeEtiquetasPorOrdenOrNumeroEnvio(
            para_etiquetadora=True
        )

        assert isinstance(result, str)
        assert "font-family" in result
        mock_client.GetCSSDeEtiquetasPorOrdenOrNumeroEnvio.assert_called_once_with(
            paraEtiquetadora=True
        )

    def test_get_datos_de_etiquetas_returns_list(self, oca_service):
        """Verify getDatosDeEtiquetasPorOrdenOrNumeroEnvio returns label data list."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <ArrayOfEtiqueta>
            <Etiqueta>
                <NroOrden>12345</NroOrden>
                <NroGuia>987654321</NroGuia>
                <Destinatario>Juan Perez</Destinatario>
            </Etiqueta>
        </ArrayOfEtiqueta>"""
        mock_response = MagicMock()
        mock_response.GetDatosDeEtiquetasPorOrdenOrNumeroEnvioResult = xml_response
        mock_client.GetDatosDeEtiquetasPorOrdenOrNumeroEnvio.return_value = (
            mock_response
        )

        result = oca_service.getDatosDeEtiquetasPorOrdenOrNumeroEnvio(
            id_orden_retiro=12345, nro_envio="987654321", is_locker=False
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["NroOrden"] == "12345"
        mock_client.GetDatosDeEtiquetasPorOrdenOrNumeroEnvio.assert_called_once_with(
            idOrdenRetiro=12345, nroEnvio="987654321", isLocker=False
        )

    def test_get_div_de_etiqueta_by_id_pieza_returns_html(self, oca_service):
        """Verify getDivDeEtiquetaByIdPieza returns HTML div."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetDivDeEtiquetaByIdPiezaResult = (
            "<div class='etiqueta'>Label</div>"
        )
        mock_client.GetDivDeEtiquetaByIdPieza.return_value = mock_response

        result = oca_service.getDivDeEtiquetaByIdPieza("PIEZA001")

        assert isinstance(result, str)
        assert "<div" in result
        mock_client.GetDivDeEtiquetaByIdPieza.assert_called_once_with(
            idPieza="PIEZA001"
        )

    def test_get_div_de_etiquetas_por_orden_returns_html(self, oca_service):
        """Verify getDivDeEtiquetasPorOrdenOrNumeroEnvio returns HTML divs."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetDivDeEtiquetasPorOrdenOrNumeroEnvioResult = (
            "<div>Label 1</div><div>Label 2</div>"
        )
        mock_client.GetDivDeEtiquetasPorOrdenOrNumeroEnvio.return_value = mock_response

        result = oca_service.getDivDeEtiquetasPorOrdenOrNumeroEnvio(
            id_orden_retiro=12345, nro_envio="987654321"
        )

        assert isinstance(result, str)
        assert "Label 1" in result
        mock_client.GetDivDeEtiquetasPorOrdenOrNumeroEnvio.assert_called_once_with(
            idOrdenRetiro=12345, nroEnvio="987654321"
        )

    def test_get_html_de_etiquetas_returns_html(self, oca_service):
        """Verify getHtmlDeEtiquetasPorOrdenOrNumeroEnvio returns full HTML."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvioResult = (
            "<html><body>Label</body></html>"
        )
        mock_client.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvio.return_value = mock_response

        result = oca_service.getHtmlDeEtiquetasPorOrdenOrNumeroEnvio(
            id_orden_retiro=12345, nro_envio="987654321"
        )

        assert isinstance(result, str)
        assert "<html>" in result
        assert "Label" in result
        mock_client.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvio.assert_called_once_with(
            idOrdenRetiro=12345, nroEnvio="987654321"
        )

    def test_get_html_de_etiquetas_para_etiquetadora_returns_html(self, oca_service):
        """Verify getHtmlDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora returns printer HTML."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadoraResult = (
            "<html><body>Printer Label</body></html>"
        )
        mock_client.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora.return_value = mock_response

        result = oca_service.getHtmlDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora(
            id_orden_retiro=12345, nro_envio="987654321"
        )

        assert isinstance(result, str)
        assert "Printer Label" in result

    def test_get_html_de_etiquetas_por_ordenes_returns_html(self, oca_service):
        """Verify getHtmlDeEtiquetasPorOrdenes returns HTML for multiple orders."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetHtmlDeEtiquetasPorOrdenesResult = (
            "<html><body>Multiple Labels</body></html>"
        )
        mock_client.GetHtmlDeEtiquetasPorOrdenes.return_value = mock_response

        result = oca_service.getHtmlDeEtiquetasPorOrdenes([12345, 12346, 12347])

        assert isinstance(result, str)
        assert "Multiple Labels" in result
        mock_client.GetHtmlDeEtiquetasPorOrdenes.assert_called_once_with(
            idOrdenes="12345,12346,12347"
        )

    def test_get_pdf_de_etiquetas_returns_base64(self, oca_service):
        """Verify getPdfDeEtiquetasPorOrdenOrNumeroEnvio returns base64 PDF."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioResult = (
            "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBlL1BhZ2UvUGFyZW50IDIgMCBS"
        )
        mock_client.GetPdfDeEtiquetasPorOrdenOrNumeroEnvio.return_value = mock_response

        result = oca_service.getPdfDeEtiquetasPorOrdenOrNumeroEnvio(
            id_orden_retiro=12345, nro_envio="987654321", logistica_inversa=True
        )

        assert isinstance(result, str)
        assert len(result) > 0
        mock_client.GetPdfDeEtiquetasPorOrdenOrNumeroEnvio.assert_called_once_with(
            idOrdenRetiro=12345, nroEnvio="987654321", logisticaInversa=True
        )

    def test_get_pdf_de_etiquetas_adidas_returns_base64(self, oca_service):
        """Verify getPdfDeEtiquetasPorOrdenOrNumeroEnvioAdidas returns Adidas PDF."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioAdidasResult = (
            "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBlL1BhZ2UvUGFyZW50IDIgMCBS"
        )
        mock_client.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioAdidas.return_value = (
            mock_response
        )

        result = oca_service.getPdfDeEtiquetasPorOrdenOrNumeroEnvioAdidas(
            id_orden_retiro=12345, nro_envio="987654321"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_pdf_para_etiquetadora_returns_base64(self, oca_service):
        """Verify getPdfDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora returns printer PDF."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadoraResult = (
            "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBlL1BhZ2UvUGFyZW50IDIgMCBS"
        )
        mock_client.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora.return_value = mock_response

        result = oca_service.getPdfDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora(
            id_orden_retiro=12345, nro_envio="987654321"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_obtener_etiquetas_zpl_returns_list(self, oca_service):
        """Verify obtenerEtiquetasZPL returns list of ZPL codes."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.ObtenerEtiquetasZPLResult = [
            "^XA^FO50,50^ADN,36,20^FDLabel 1^FS^XZ",
            "^XA^FO50,50^ADN,36,20^FDLabel 2^FS^XZ",
        ]
        mock_client.ObtenerEtiquetasZPL.return_value = mock_response

        result = oca_service.obtenerEtiquetasZPL(
            orden_retiro="12345", numero_envio="987654321", numero_bulto="1"
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert "^XA" in result[0]
        mock_client.ObtenerEtiquetasZPL.assert_called_once_with(
            ordenRetiro="12345", numeroEnvio="987654321", numeroBulto="1"
        )
