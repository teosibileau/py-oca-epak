"""Tests for core SOAP operations."""

from datetime import datetime
from unittest.mock import MagicMock
from tests.client.conftest import create_soap_mock


class TestCoreOperations:
    """Tests for core SOAP operations."""

    def test_anular_orden_generada_calls_correct_soap_method(self, oca_service):
        """Verify anularOrdenGenerada calls AnularOrdenGenerada with correct params."""
        mock_client = oca_service._mock_client
        mock_client.AnularOrdenGenerada.return_value = create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.anularOrdenGenerada(12345)

        mock_client.AnularOrdenGenerada.assert_called_once_with(
            usuario="test_user",
            password="test_pass",
            nroOrden=12345,
        )

    def test_anular_orden_generada_returns_processed_result(self, oca_service):
        """Verify anularOrdenGenerada returns processed data."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <Numero>12345</Numero>
                <Resultado>OK</Resultado>
            </Table>
        </DataSet>"""
        mock_client.AnularOrdenGenerada.return_value = create_soap_mock(xml_response)

        result = oca_service.anularOrdenGenerada(12345)

        assert len(result) == 1
        assert result[0]["Numero"] == 12345

    def test_centro_costo_por_operativa_calls_correct_soap_method(self, oca_service):
        """Verify centroCostoPorOperativa calls GetCentroCostorPorOperativa."""
        mock_client = oca_service._mock_client
        mock_client.GetCentroCostorPorOperativa.return_value = create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.centroCostoPorOperativa(72771)

        mock_client.GetCentroCostorPorOperativa.assert_called_once_with(
            CUIT="20-12345678-9",
            Operativa=72771,
        )

    def test_centros_de_imposicion_calls_correct_soap_method(self, oca_service):
        """Verify centrosDeImposicion calls GetCentrosImposicion."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicion.return_value = create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.centrosDeImposicion()

        mock_client.GetCentrosImposicion.assert_called_once()

    def test_centros_de_imposicion_por_cp_calls_with_postal_code(self, oca_service):
        """Verify centrosDeImposicionPorCP passes CodigoPostal param."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionPorCP.return_value = create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.centrosDeImposicionPorCP(1000)

        mock_client.GetCentrosImposicionPorCP.assert_called_once_with(
            CodigoPostal=1000,
        )

    def test_ingresar_or_renders_template_correctly(
        self, oca_service, sample_compra_data, mock_logger
    ):
        """Verify ingresarOR renders Jinja2 template with compra data."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, 1)

        mock_client.IngresoOR.assert_called_once()
        call_args = mock_client.IngresoOR.call_args
        assert "usr" in call_args.kwargs
        assert "psw" in call_args.kwargs
        assert "xmlOr" in call_args.kwargs
        assert "<NumeroCuenta>12345/001</NumeroCuenta>" in call_args.kwargs["xmlOr"]

    def test_ingresar_or_calls_soap_with_correct_params(
        self, oca_service, sample_compra_data, mock_logger
    ):
        """Verify ingresarOR calls SOAP method with correct parameters."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, 1)

        mock_client.IngresoOR.assert_called_once()
        call_args = mock_client.IngresoOR.call_args
        assert call_args.kwargs["usr"] == "test_user"
        assert call_args.kwargs["psw"] == "test_pass"
        assert "<NumeroCuenta>12345/001</NumeroCuenta>" in call_args.kwargs["xmlOr"]
        assert "<IdFranjaHoraria>3</IdFranjaHoraria>" in call_args.kwargs["xmlOr"]
        assert "<ConfirmarRetiro>1</ConfirmarRetiro>" in call_args.kwargs["xmlOr"]

    def test_ingresar_or_logs_rendered_xml(
        self, oca_service, sample_compra_data, mock_logger
    ):
        """Verify ingresarOR logs the rendered XML."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, 1)

        mock_logger.info.assert_called()
        log_call = mock_logger.info.call_args[0][0]
        assert "NumeroCuenta" in log_call

    def test_ingresar_or_boolean_conversion_true(
        self, oca_service, sample_compra_data, mock_logger
    ):
        """Verify ingresarOR converts True to 1."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, True)

        call_args = mock_client.IngresoOR.call_args
        assert "<ConfirmarRetiro>1</ConfirmarRetiro>" in call_args.kwargs["xmlOr"]

    def test_ingresar_or_boolean_conversion_false(
        self, oca_service, sample_compra_data, mock_logger
    ):
        """Verify ingresarOR converts False to 0."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, False)

        call_args = mock_client.IngresoOR.call_args
        assert "<ConfirmarRetiro>0</ConfirmarRetiro>" in call_args.kwargs["xmlOr"]

    def test_estado_ultimos_envios_formats_dates_correctly(self, oca_service):
        """Verify estadoUltimosEnvios formats dates as ISO strings."""
        mock_client = oca_service._mock_client
        mock_client.GetEnviosUltimoEstado.return_value = create_soap_mock(
            "<DataSet></DataSet>"
        )

        from_date = datetime(2024, 1, 15, 10, 30)
        to_date = datetime(2024, 1, 20, 18, 0)

        oca_service.estadoUltimosEnvios(["72771"], from_date, to_date)

        mock_client.GetEnviosUltimoEstado.assert_called_once_with(
            CUIT="20-12345678-9",
            Operativas="72771",
            FechaDesde="2024-01-15T10:30:00",
            FechaHasta="2024-01-20T18:00:00",
        )

    def test_list_envios_formats_dates_correctly(self, oca_service):
        """Verify listEnvios formats dates as ISO strings."""
        mock_client = oca_service._mock_client
        mock_client.List_Envios.return_value = create_soap_mock("<DataSet></DataSet>")

        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        oca_service.listEnvios(12345, from_date, to_date)

        mock_client.List_Envios.assert_called_once_with(
            CUIT="20-12345678-9",
            IdCentroImposicion=12345,
            Desde="2024-01-01T00:00:00",
            Hasta="2024-01-31T00:00:00",
        )

    def test_tarifar_envio_corporativo_passes_all_params(self, oca_service):
        """Verify tarifarEnvioCorporativo passes all parameters."""
        mock_client = oca_service._mock_client
        mock_client.Tarifar_Envio_Corporativo.return_value = create_soap_mock(
            "<DataSet></DataSet>"
        )

        oca_service.tarifarEnvioCorporativo(5.0, 100, 1000, 5000, 1, 72771)

        mock_client.Tarifar_Envio_Corporativo.assert_called_once_with(
            PesoTotal=5.0,
            VolumenTotal=100,
            CodigoPostalOrigen=1000,
            CodigoPostalDestino=5000,
            CantidadPaquetes=1,
            Operativa=72771,
        )

    def test_tracking_or_calls_with_orden_retiro(self, oca_service):
        """Verify trackingOR passes orden retiro number."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_OrdenRetiro.return_value = create_soap_mock(
            "<DataSet></DataSet>"
        )

        oca_service.trackingOR(12345)

        mock_client.Tracking_OrdenRetiro.assert_called_once_with(OrdenRetiro=12345)

    def test_tracking_pieza_con_id_calls_with_pieza(self, oca_service):
        """Verify trackingPiezaConID passes pieza ID."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_Pieza.return_value = create_soap_mock(
            "<DataSet></DataSet>"
        )

        oca_service.trackingPiezaConID("ABC123")

        mock_client.Tracking_Pieza.assert_called_once_with(Pieza="ABC123")

    def test_tracking_pieza_con_dni_cuit_calls_with_both_params(self, oca_service):
        """Verify trackingPiezaConDNICuit passes DNI and CUIT."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_Pieza.return_value = create_soap_mock(
            "<DataSet></DataSet>"
        )

        oca_service.trackingPiezaConDNICuit("12345678", "20-12345678-9")

        mock_client.Tracking_Pieza.assert_called_once_with(
            NroDocumento="12345678", CUIT="20-12345678-9"
        )
