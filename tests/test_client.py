"""Test suite for OcaService class."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock
from ocaepak.client import OcaService


class TestOcaService:
    """Test suite for OcaService class using pytest fixtures as instance methods."""

    # ============================================================
    # FIXTURES (Instance Methods)
    # ============================================================

    @pytest.fixture
    def mock_soap_client(self, mocker):
        """Mock the SoapClient class."""
        return mocker.patch("ocaepak.client.SoapClient")

    @pytest.fixture
    def mock_logger(self, mocker):
        """Mock the logger for ingresarOR tests."""
        return mocker.patch("ocaepak.client.logger")

    @pytest.fixture
    def oca_service(self, mock_soap_client):
        """Create OcaService instance with mocked SOAP client."""
        mock_instance = mock_soap_client.return_value
        service = OcaService("test_user", "test_pass", "20-12345678-9")
        service._mock_client = mock_instance
        return service

    @pytest.fixture
    def sample_xml_single_table(self):
        """Sample XML response with single Table element."""
        return """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <Numero>12345</Numero>
                <Piso>5</Piso>
                <idCentroImposicion>42</idCentroImposicion>
                <Precio>100.50</Precio>
                <Adicional>10.25</Adicional>
                <Total>110.75</Total>
                <fecha>2024-01-15T10:30:00-03:00</fecha>
                <Nombre>Centro Principal</Nombre>
                <Localidad>Buenos Aires</Localidad>
            </Table>
        </DataSet>"""

    @pytest.fixture
    def sample_xml_multiple_tables(self):
        """Sample XML response with multiple Table elements."""
        return """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <Numero>1001</Numero>
                <Precio>50.00</Precio>
                <Nombre>Sucursal A</Nombre>
            </Table>
            <Table>
                <Numero>1002</Numero>
                <Precio>75.00</Precio>
                <Nombre>Sucursal B</Nombre>
            </Table>
        </DataSet>"""

    @pytest.fixture
    def sample_xml_empty_values(self):
        """Sample XML with empty/whitespace values."""
        return """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <Numero>999</Numero>
                <Precio></Precio>
                <Nombre>   </Nombre>
                <Localidad>Cordoba</Localidad>
            </Table>
        </DataSet>"""

    @pytest.fixture
    def sample_compra_data(self):
        """Sample purchase data for ingresarOR method."""
        return {
            "numero_cuenta": "12345/001",
            "retiro": {
                "calle": "Av. Corrientes",
                "numero": 1234,
                "piso": "3",
                "departamento": "B",
                "cp": 1043,
                "localidad": "Buenos Aires",
                "provincia": "CABA",
                "solicitante": "Juan Perez",
                "email": "juan@example.com",
                "observaciones": "Fragile items",
                "centro_de_costo": 1,
            },
            "envios": [
                {
                    "id_operativa": 72771,
                    "numero_remito": "REM-001",
                    "destinatario": {
                        "apellido": "Gomez",
                        "nombre": "Maria",
                        "calle": "Av. Santa Fe",
                        "numero": 5678,
                        "piso": "2",
                        "departamento": "A",
                        "cp": 5000,
                        "localidad": "Cordoba",
                        "provincia": "Cordoba",
                        "telefono": "3511234567",
                        "email": "maria@example.com",
                        "celular": "3519876543",
                    },
                    "paquetes": [
                        {
                            "alto": 10,
                            "ancho": 20,
                            "largo": 30,
                            "peso": 2.5,
                            "valor_declarado": 1500,
                            "cantidad": 2,
                        }
                    ],
                }
            ],
        }

    def _create_xml_mock(self, xml_string):
        """Helper to create a properly configured XML mock."""
        mock_result = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = xml_string
        mock_result.__getitem__.return_value = inner_mock
        return mock_result

    # ============================================================
    # CLASS ATTRIBUTES TESTS
    # ============================================================

    def test_wsdl_base_uri_constant(self):
        """Verify WSDL base URI is correct."""
        expected = "http://webservice.oca.com.ar/oep_tracking/Oep_Track.asmx"
        assert OcaService.WSDL_BASE_URI == expected

    def test_oca_wsdl_constant(self):
        """Verify full WSDL URL is constructed correctly."""
        expected = "http://webservice.oca.com.ar/oep_tracking/Oep_Track.asmx?WSDL"
        assert OcaService.OCA_WDSL == expected

    def test_operativas_dictionary(self):
        """Verify OPERATIVAS contains expected service types."""
        assert 72771 in OcaService.OPERATIVAS
        assert 72772 in OcaService.OPERATIVAS
        assert "Punto a Punto" in OcaService.OPERATIVAS[72771]

    def test_franjas_horarias_dictionary(self):
        """Verify FRANJAS_HORARIAS contains expected time windows."""
        assert 1 in OcaService.FRANJAS_HORARIAS
        assert 2 in OcaService.FRANJAS_HORARIAS
        assert 3 in OcaService.FRANJAS_HORARIAS
        assert "8 a 17hs" == OcaService.FRANJAS_HORARIAS[1]

    def test_labels_for_integers(self):
        """Verify LABELS_FOR_INTEGERS contains correct field names."""
        expected = [
            "Numero",
            "Piso",
            "idCentroImposicion",
            "idTipoSercicio",
            "PlazoEntrega",
            "Tarifador",
            "IDLocker",
            "NumeroEnvio",
        ]
        assert OcaService.LABELS_FOR_INTEGERS == expected

    def test_labels_for_floats(self):
        """Verify LABELS_FOR_FLOATS contains correct field names."""
        expected = ["Precio", "Adicional", "Total"]
        assert OcaService.LABELS_FOR_FLOATS == expected

    def test_labels_for_datetimes(self):
        """Verify LABELS_FOR_DATETIMES contains correct field names."""
        expected = ["fecha"]
        assert OcaService.LABELS_FOR_DATETIMES == expected

    # ============================================================
    # INITIALIZATION TESTS
    # ============================================================

    def test_init_sets_user_password_cuit(self, mock_soap_client):
        """Verify __init__ correctly stores credentials."""
        service = OcaService("myuser", "mypass", "20-12345678-9")
        assert service.user == "myuser"
        assert service.password == "mypass"
        assert service.CUIT == "20-12345678-9"

    def test_init_creates_soap_client_with_correct_params(self, mock_soap_client):
        """Verify SoapClient is initialized with correct WSDL and settings."""
        OcaService("test_user", "test_pass", "20-12345678-9")
        mock_soap_client.assert_called_once_with(
            wsdl=OcaService.OCA_WDSL,
            location=OcaService.WSDL_BASE_URI,
            exceptions=True,
            trace=False,
        )

    def test_init_with_trace_enabled(self, mock_soap_client):
        """Verify trace parameter is passed to SoapClient."""
        OcaService("test_user", "test_pass", "20-12345678-9", trace=True)
        mock_soap_client.assert_called_once_with(
            wsdl=OcaService.OCA_WDSL,
            location=OcaService.WSDL_BASE_URI,
            exceptions=True,
            trace=True,
        )

    # ============================================================
    # ITERATERESULT CLASSMETHOD TESTS
    # ============================================================

    def test_iterateresult_converts_integers(self, sample_xml_single_table):
        """Verify integer fields are converted to int type."""
        mock_xml_result = self._create_xml_mock(sample_xml_single_table)
        result = OcaService.iterateresult("AnularOrdenGeneradaResult", mock_xml_result)

        assert len(result) == 1
        assert isinstance(result[0]["Numero"], int)
        assert result[0]["Numero"] == 12345
        assert isinstance(result[0]["Piso"], int)
        assert result[0]["Piso"] == 5
        assert isinstance(result[0]["idCentroImposicion"], int)
        assert result[0]["idCentroImposicion"] == 42

    def test_iterateresult_converts_floats(self, sample_xml_single_table):
        """Verify float fields are converted to float type."""
        mock_xml_result = self._create_xml_mock(sample_xml_single_table)
        result = OcaService.iterateresult("TarifarResult", mock_xml_result)

        assert len(result) == 1
        assert isinstance(result[0]["Precio"], float)
        assert result[0]["Precio"] == 100.50
        assert isinstance(result[0]["Adicional"], float)
        assert result[0]["Adicional"] == 10.25
        assert isinstance(result[0]["Total"], float)
        assert result[0]["Total"] == 110.75

    def test_iterateresult_converts_datetimes(self, sample_xml_single_table):
        """Verify datetime fields are parsed correctly."""
        mock_xml_result = self._create_xml_mock(sample_xml_single_table)
        result = OcaService.iterateresult("StatusResult", mock_xml_result)

        assert len(result) == 1
        assert isinstance(result[0]["fecha"], datetime)
        assert result[0]["fecha"].year == 2024
        assert result[0]["fecha"].month == 1
        assert result[0]["fecha"].day == 15

    def test_iterateresult_encodes_strings_to_utf8(self, sample_xml_single_table):
        """Verify string fields are encoded to UTF-8."""
        mock_xml_result = self._create_xml_mock(sample_xml_single_table)
        result = OcaService.iterateresult("CentroResult", mock_xml_result)

        assert len(result) == 1
        assert isinstance(result[0]["Nombre"], bytes)
        assert result[0]["Nombre"].decode("utf-8") == "Centro Principal"
        assert isinstance(result[0]["Localidad"], bytes)
        assert result[0]["Localidad"].decode("utf-8") == "Buenos Aires"

    def test_iterateresult_handles_multiple_tables(self, sample_xml_multiple_tables):
        """Verify multiple Table elements return list of dicts."""
        mock_xml_result = self._create_xml_mock(sample_xml_multiple_tables)
        result = OcaService.iterateresult("CentrosResult", mock_xml_result)

        assert len(result) == 2
        assert result[0]["Numero"] == 1001
        assert result[1]["Numero"] == 1002

    def test_iterateresult_skips_empty_values(self, sample_xml_empty_values):
        """Verify empty/whitespace values are skipped."""
        mock_xml_result = self._create_xml_mock(sample_xml_empty_values)
        result = OcaService.iterateresult("TestResult", mock_xml_result)

        assert len(result) == 1
        assert "Numero" in result[0]
        assert "Precio" not in result[0]  # Empty value skipped
        assert "Nombre" not in result[0]  # Whitespace value skipped
        assert "Localidad" in result[0]

    def test_iterateresult_handles_malformed_datetime(self):
        """Verify error handling for invalid datetime format."""
        xml_with_bad_date = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <fecha>invalid-date</fecha>
            </Table>
        </DataSet>"""
        mock_xml_result = self._create_xml_mock(xml_with_bad_date)

        with pytest.raises(ValueError):
            OcaService.iterateresult("BadDateResult", mock_xml_result)

    # ============================================================
    # SOAP METHOD TESTS - SUCCESS SCENARIOS
    # ============================================================

    def test_anular_orden_generada_calls_correct_soap_method(self, oca_service):
        """Verify anularOrdenGenerada calls AnularOrdenGenerada with correct params."""
        mock_client = oca_service._mock_client
        mock_client.AnularOrdenGenerada.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.anularOrdenGenerada(12345)

        mock_client.AnularOrdenGenerada.assert_called_once_with(
            usuario="test_user",
            password="test_pass",
            nroOrden=12345,
        )

    def _create_soap_mock(self, xml_string):
        """Helper to create a mock SOAP response."""
        mock_response = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = xml_string
        mock_response.__getitem__.return_value = inner_mock
        return mock_response

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
        mock_client.AnularOrdenGenerada.return_value = self._create_soap_mock(
            xml_response
        )

        result = oca_service.anularOrdenGenerada(12345)

        assert len(result) == 1
        assert result[0]["Numero"] == 12345

    def test_centro_costo_por_operativa_calls_correct_soap_method(self, oca_service):
        """Verify centroCostoPorOperativa calls GetCentroCostorPorOperativa."""
        mock_client = oca_service._mock_client
        mock_client.GetCentroCostorPorOperativa.return_value = self._create_soap_mock(
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
        mock_client.GetCentrosImposicion.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.centrosDeImposicion()

        mock_client.GetCentrosImposicion.assert_called_once()

    def test_centros_de_imposicion_por_cp_calls_with_postal_code(self, oca_service):
        """Verify centrosDeImposicionPorCP passes CodigoPostal param."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionPorCP.return_value = self._create_soap_mock(
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

        # Verify the SOAP method was called
        assert mock_client.IngresoOR.called
        call_args = mock_client.IngresoOR.call_args

        # Check that XML_Retiro was passed and contains expected data
        assert "XML_Retiro" in call_args.kwargs or call_args[1].get("XML_Retiro")
        xml_arg = call_args.kwargs.get("XML_Retiro") or call_args[1].get("XML_Retiro")
        assert "12345/001" in xml_arg  # numero_cuenta
        assert "Av. Corrientes" in xml_arg  # calle
        assert "Juan Perez" in xml_arg  # solicitante

    def test_ingresar_or_calls_soap_with_correct_params(
        self, oca_service, sample_compra_data, mock_logger
    ):
        """Verify ingresarOR calls IngresoOR with all required parameters."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, 1, confirmar_retiro=True)

        mock_client.IngresoOR.assert_called_once()
        call_args = mock_client.IngresoOR.call_args

        # Check positional or keyword arguments
        args_dict = call_args.kwargs if call_args.kwargs else call_args[1]
        assert args_dict["usr"] == "test_user"
        assert args_dict["psw"] == "test_pass"
        assert args_dict["ConfirmarRetiro"] == "true"
        assert args_dict["DiasRetiro"] == 3
        assert args_dict["FranjaHoraria"] == 1
        assert "XML_Retiro" in args_dict

    def test_ingresar_or_logs_rendered_xml(
        self, oca_service, sample_compra_data, mock_logger
    ):
        """Verify ingresarOR logs the rendered XML."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, 1)

        mock_logger.info.assert_called_once()
        logged_message = mock_logger.info.call_args[0][0]
        assert "ROWS" in logged_message or "12345/001" in logged_message

    def test_ingresar_or_boolean_conversion_true(self, oca_service, sample_compra_data):
        """Verify confirmar_retiro=True converts to 'true' string."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, 1, confirmar_retiro=True)

        call_args = mock_client.IngresoOR.call_args
        args_dict = call_args.kwargs if call_args.kwargs else call_args[1]
        assert args_dict["ConfirmarRetiro"] == "true"

    def test_ingresar_or_boolean_conversion_false(
        self, oca_service, sample_compra_data
    ):
        """Verify confirmar_retiro=False converts to 'false' string."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_client.IngresoOR.return_value = mock_response

        oca_service.ingresarOR(sample_compra_data, 3, 1, confirmar_retiro=False)

        call_args = mock_client.IngresoOR.call_args
        args_dict = call_args.kwargs if call_args.kwargs else call_args[1]
        assert args_dict["ConfirmarRetiro"] == "false"

    def test_estado_ultimos_envios_formats_dates_correctly(self, oca_service):
        """Verify estadoUltimosEnvios formats dates as DD/MM/YYYY."""
        mock_client = oca_service._mock_client
        mock_client.GetEnviosUltimoEstado.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        from_date = datetime(2024, 1, 15)
        to_date = datetime(2024, 1, 20)

        oca_service.estadoUltimosEnvios(["72771"], from_date, to_date)

        mock_client.GetEnviosUltimoEstado.assert_called_once_with(
            cuit="20-12345678-9",
            operativas=["72771"],
            fechaDesta="15/01/2024",
            fechaHasta="20/01/2024",
        )

    def test_list_envios_formats_dates_correctly(self, oca_service):
        """Verify listEnvios formats dates correctly."""
        mock_client = oca_service._mock_client
        mock_client.List_Envios.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        from_date = datetime(2024, 1, 15)
        to_date = datetime(2024, 1, 20)

        oca_service.listEnvios(from_date, to_date)

        mock_client.List_Envios.assert_called_once_with(
            CUIT="20-12345678-9",
            FechaDesde="15/01/2024",
            FechaHasta="20/01/2024",
        )

    def test_tarifar_envio_corporativo_passes_all_params(self, oca_service):
        """Verify tarifarEnvioCorporativo passes all required parameters."""
        mock_client = oca_service._mock_client
        mock_client.Tarifar_Envio_Corporativo.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.tarifarEnvioCorporativo(5.0, 100, 1000, 5000, 2, 72771)

        mock_client.Tarifar_Envio_Corporativo.assert_called_once_with(
            PesoTotal=5.0,
            VolumenTotal=100,
            CodigoPostalOrigen=1000,
            CodigoPostalDestino=5000,
            CantidadPaquetes=2,
            Cuit="20-12345678-9",
            Operativa=72771,
        )

    def test_tracking_or_calls_with_orden_retiro(self, oca_service):
        """Verify trackingOR calls Tracking_OrdenRetiro."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_OrdenRetiro.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.trackingOR(12345)

        mock_client.Tracking_OrdenRetiro.assert_called_once_with(
            CUIT="20-12345678-9",
            OrdenRetiro=12345,
        )

    def test_tracking_pieza_con_id_calls_with_pieza(self, oca_service):
        """Verify trackingPiezaConID calls Tracking_Pieza with Pieza param."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_Pieza.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.trackingPiezaConID("123456789")

        mock_client.Tracking_Pieza.assert_called_once_with(
            Pieza="123456789",
        )

    def test_tracking_pieza_con_dni_cuit_calls_with_both_params(self, oca_service):
        """Verify trackingPiezaConDNICUIT calls with NroDocumentoCliente and CUIT."""
        mock_client = oca_service._mock_client
        mock_client.Tracking_Pieza.return_value = self._create_soap_mock(
            "<DataSet><Table><Numero>1</Numero></Table></DataSet>"
        )

        oca_service.trackingPiezaConDNICUIT("30123456", "20-12345678-9")

        mock_client.Tracking_Pieza.assert_called_once_with(
            NroDocumentoCliente="30123456",
            CUIT="20-12345678-9",
        )

    # ============================================================
    # ERROR SCENARIO TESTS
    # ============================================================

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
        mock_client.GetCentrosImposicion.return_value = self._create_soap_mock(
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
        # Pass invalid data that will cause template rendering issues
        invalid_compra = {"invalid": "data"}

        # Template will raise UndefinedError when required fields are missing
        with pytest.raises(Exception) as exc_info:
            oca_service.ingresarOR(invalid_compra, 3, 1)

        # Verify it's a template-related error
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
        incomplete_compra = {}  # Empty dict

        # Template will raise UndefinedError when required fields are missing
        with pytest.raises(Exception) as exc_info:
            oca_service.ingresarOR(incomplete_compra, 3, 1)

        # Verify it's a template-related error
        assert (
            "retiro" in str(exc_info.value).lower()
            or "undefined" in str(exc_info.value).lower()
        )

    def test_estado_ultimos_envios_invalid_date_range(self, oca_service):
        """Verify estadoUltimosEnvios handles invalid date range."""
        mock_client = oca_service._mock_client
        mock_client.GetEnviosUltimoEstado.side_effect = Exception("Invalid date range")

        from_date = datetime(2024, 1, 20)
        to_date = datetime(2024, 1, 15)  # End before start

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
        mock_client.Tracking_Pieza.return_value = self._create_soap_mock(
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
        # XML without required fields - should still work, just return what's there
        mock_xml_result = self._create_xml_mock(
            "<DataSet><Table><Nombre>Test</Nombre></Table></DataSet>"
        )

        result = OcaService.iterateresult("Result", mock_xml_result)

        assert len(result) == 1
        assert result[0]["Nombre"] == b"Test"  # Should be bytes (UTF-8 encoded)

    def test_iterateresult_handles_invalid_numeric_value(self):
        """Verify iterateresult handles non-numeric value in numeric field."""
        xml_with_bad_number = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <Numero>not-a-number</Numero>
            </Table>
        </DataSet>"""
        mock_xml_result = self._create_xml_mock(xml_with_bad_number)

        with pytest.raises(ValueError):
            OcaService.iterateresult("BadNum", mock_xml_result)

    # ============================================================
    # GETPROVINCIAS TESTS
    # ============================================================

    def test_get_provincias_returns_list(self, oca_service):
        """Verify getProvincias returns list of provinces."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <Provincias>
            <Provincia>
                <IdProvincia>2</IdProvincia>
                <Descripcion>BUENOS AIRES</Descripcion>
            </Provincia>
            <Provincia>
                <IdProvincia>1</IdProvincia>
                <Descripcion>CAPITAL FEDERAL</Descripcion>
            </Provincia>
        </Provincias>"""
        mock_response = MagicMock()
        mock_response.GetProvinciasResult = xml_response
        mock_client.GetProvincias.return_value = mock_response

        result = oca_service.getProvincias()

        assert len(result) == 2
        assert result[0]["IdProvincia"] == "2"
        assert result[0]["Descripcion"] == "BUENOS AIRES"
        assert result[1]["IdProvincia"] == "1"
        assert result[1]["Descripcion"] == "CAPITAL FEDERAL"

    def test_get_provincias_calls_correct_soap_method(self, oca_service):
        """Verify getProvincias calls GetProvincias with no params."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetProvinciasResult = "<Provincias><Provincia><IdProvincia>1</IdProvincia></Provincia></Provincias>"
        mock_client.GetProvincias.return_value = mock_response

        oca_service.getProvincias()

        mock_client.GetProvincias.assert_called_once_with()

    def test_get_provincias_empty_response(self, oca_service):
        """Verify getProvincias handles empty response."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetProvinciasResult = "<Provincias></Provincias>"
        mock_client.GetProvincias.return_value = mock_response

        result = oca_service.getProvincias()

        assert result == []

    def test_get_provincias_soap_error(self, oca_service):
        """Verify getProvincias handles SOAP errors."""
        mock_client = oca_service._mock_client
        mock_client.GetProvincias.side_effect = Exception("SOAP Fault")

        with pytest.raises(Exception) as exc_info:
            oca_service.getProvincias()

        assert "SOAP Fault" in str(exc_info.value)

    # ============================================================
    # ADMISSION CENTERS TESTS
    # ============================================================

    def test_centros_de_imposicion_admision_returns_list(self, oca_service):
        """Verify centrosDeImposicionAdmision returns list of centers."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <idCentroImposicion>101</idCentroImposicion>
                <Nombre>Centro Admision A</Nombre>
                <Localidad>Buenos Aires</Localidad>
            </Table>
            <Table>
                <idCentroImposicion>102</idCentroImposicion>
                <Nombre>Centro Admision B</Nombre>
                <Localidad>Cordoba</Localidad>
            </Table>
        </DataSet>"""
        mock_client.GetCentrosImposicionAdmision.return_value = self._create_soap_mock(
            xml_response
        )

        result = oca_service.centrosDeImposicionAdmision()

        assert len(result) == 2
        assert result[0]["idCentroImposicion"] == 101
        assert result[0]["Nombre"] == b"Centro Admision A"
        assert result[1]["idCentroImposicion"] == 102
        assert result[1]["Nombre"] == b"Centro Admision B"

    def test_centros_de_imposicion_admision_calls_correct_soap_method(
        self, oca_service
    ):
        """Verify centrosDeImposicionAdmision calls GetCentrosImposicionAdmision."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmision.return_value = self._create_soap_mock(
            "<DataSet><Table><idCentroImposicion>1</idCentroImposicion></Table></DataSet>"
        )

        oca_service.centrosDeImposicionAdmision()

        mock_client.GetCentrosImposicionAdmision.assert_called_once_with()

    def test_centros_de_imposicion_admision_empty_response(self, oca_service):
        """Verify centrosDeImposicionAdmision handles empty response."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmision.return_value = self._create_soap_mock(
            "<DataSet></DataSet>"
        )

        result = oca_service.centrosDeImposicionAdmision()

        assert result == []

    def test_centros_de_imposicion_admision_soap_error(self, oca_service):
        """Verify centrosDeImposicionAdmision handles SOAP errors."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmision.side_effect = Exception("SOAP Error")

        with pytest.raises(Exception) as exc_info:
            oca_service.centrosDeImposicionAdmision()

        assert "SOAP Error" in str(exc_info.value)

    def test_centros_de_imposicion_admision_por_cp_returns_list(self, oca_service):
        """Verify centrosDeImposicionAdmisionPorCP returns centers near postal code."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <idCentroImposicion>201</idCentroImposicion>
                <Nombre>Centro CP 1000</Nombre>
                <Localidad>Buenos Aires</Localidad>
            </Table>
        </DataSet>"""
        mock_client.GetCentrosImposicionAdmisionPorCP.return_value = (
            self._create_soap_mock(xml_response)
        )

        result = oca_service.centrosDeImposicionAdmisionPorCP(1000)

        assert len(result) == 1
        assert result[0]["idCentroImposicion"] == 201
        assert result[0]["Nombre"] == b"Centro CP 1000"

    def test_centros_de_imposicion_admision_por_cp_calls_with_postal_code(
        self, oca_service
    ):
        """Verify centrosDeImposicionAdmisionPorCP passes CodigoPostal param."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmisionPorCP.return_value = self._create_soap_mock(
            "<DataSet><Table><idCentroImposicion>1</idCentroImposicion></Table></DataSet>"
        )

        oca_service.centrosDeImposicionAdmisionPorCP(5000)

        mock_client.GetCentrosImposicionAdmisionPorCP.assert_called_once_with(
            CodigoPostal=5000
        )

    def test_centros_de_imposicion_admision_por_cp_empty_response(self, oca_service):
        """Verify centrosDeImposicionAdmisionPorCP handles empty response."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmisionPorCP.return_value = (
            self._create_soap_mock("<DataSet></DataSet>")
        )

        result = oca_service.centrosDeImposicionAdmisionPorCP(9999)

        assert result == []

    def test_centros_de_imposicion_admision_por_cp_soap_error(self, oca_service):
        """Verify centrosDeImposicionAdmisionPorCP handles SOAP errors."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmisionPorCP.side_effect = Exception(
            "Invalid CP"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.centrosDeImposicionAdmisionPorCP(0)

        assert "Invalid CP" in str(exc_info.value)

    # ============================================================
    # LOCALIDADES TESTS
    # ============================================================

    def test_get_localidades_by_provincia_returns_list(self, oca_service):
        """Verify getLocalidadesByProvincia returns list of localities."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <Localidades>
            <Provincia>
                <Nombre>CAPITAL FEDERAL</Nombre>
            </Provincia>
            <Provincia>
                <Nombre>12 DE OCTUBRE</Nombre>
            </Provincia>
        </Localidades>"""
        mock_response = MagicMock()
        mock_response.GetLocalidadesByProvinciaResult = xml_response
        mock_client.GetLocalidadesByProvincia.return_value = mock_response

        result = oca_service.getLocalidadesByProvincia(1)

        assert len(result) == 2
        assert result[0]["Nombre"] == "CAPITAL FEDERAL"
        assert result[1]["Nombre"] == "12 DE OCTUBRE"

    def test_get_localidades_by_provincia_calls_with_province_id(self, oca_service):
        """Verify getLocalidadesByProvincia passes idProvincia parameter."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetLocalidadesByProvinciaResult = (
            "<Localidades><Provincia><Nombre>Test</Nombre></Provincia></Localidades>"
        )
        mock_client.GetLocalidadesByProvincia.return_value = mock_response

        oca_service.getLocalidadesByProvincia(5)

        mock_client.GetLocalidadesByProvincia.assert_called_once_with(idProvincia=5)

    def test_get_localidades_by_provincia_empty_response(self, oca_service):
        """Verify getLocalidadesByProvincia handles empty response."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetLocalidadesByProvinciaResult = "<Localidades></Localidades>"
        mock_client.GetLocalidadesByProvincia.return_value = mock_response

        result = oca_service.getLocalidadesByProvincia(99)

        assert result == []

    def test_get_localidades_by_provincia_soap_error(self, oca_service):
        """Verify getLocalidadesByProvincia handles SOAP errors."""
        mock_client = oca_service._mock_client
        mock_client.GetLocalidadesByProvincia.side_effect = Exception(
            "Invalid province"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.getLocalidadesByProvincia(999)

        assert "Invalid province" in str(exc_info.value)

    # ============================================================
    # CACHE TESTS
    # ============================================================

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

        # First call - should fetch from API
        result1 = oca_service.getProvincias()
        assert mock_client.GetProvincias.call_count == 1

        # Second call - should use cache, not call API again
        result2 = oca_service.getProvincias()
        assert mock_client.GetProvincias.call_count == 1  # Still 1, not 2
        assert result1 is result2  # Same object reference

    def test_get_localidades_by_provincia_caches_by_id(self, oca_service):
        """Verify getLocalidadesByProvincia caches per province ID."""
        mock_client = oca_service._mock_client

        # Mock for province 1
        mock_response1 = MagicMock()
        mock_response1.GetLocalidadesByProvinciaResult = """<?xml version="1.0" encoding="utf-8"?>
        <Localidades>
            <Provincia>
                <Nombre>LOCALITY 1</Nombre>
            </Provincia>
        </Localidades>"""

        # Mock for province 2
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

        # First call for province 1
        result1 = oca_service.getLocalidadesByProvincia(1)
        assert mock_client.GetLocalidadesByProvincia.call_count == 1

        # Second call for province 1 - should use cache
        result2 = oca_service.getLocalidadesByProvincia(1)
        assert mock_client.GetLocalidadesByProvincia.call_count == 1
        assert result1 is result2

        # Call for province 2 - should fetch from API
        result3 = oca_service.getLocalidadesByProvincia(2)
        assert mock_client.GetLocalidadesByProvincia.call_count == 2
        assert result3[0]["Nombre"] == "LOCALITY 2"

    def test_clear_cache_removes_cached_data(self, oca_service):
        """Verify clear_cache removes all cached data."""
        mock_client = oca_service._mock_client

        # Setup mocks
        mock_response_prov = MagicMock()
        mock_response_prov.GetProvinciasResult = "<Provincias></Provincias>"
        mock_client.GetProvincias.return_value = mock_response_prov

        mock_response_loc = MagicMock()
        mock_response_loc.GetLocalidadesByProvinciaResult = (
            "<Localidades></Localidades>"
        )
        mock_client.GetLocalidadesByProvincia.return_value = mock_response_loc

        # Cache some data
        oca_service.getProvincias()
        oca_service.getLocalidadesByProvincia(1)

        assert hasattr(oca_service, "_provincias_cache")
        assert hasattr(oca_service, "_localidades_cache")

        # Clear cache
        oca_service.clear_cache()

        assert not hasattr(oca_service, "_provincias_cache")
        assert not hasattr(oca_service, "_localidades_cache")

        # Next call should fetch from API again
        oca_service.getProvincias()
        assert mock_client.GetProvincias.call_count == 2

    # ============================================================
    # SERVICES BY CENTER TESTS
    # ============================================================

    def test_get_servicios_de_centros_imposicion_returns_list_with_services(
        self, oca_service
    ):
        """Verify getServiciosDeCentrosImposicion returns centers with services."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <CentrosDeImposicion>
            <Centro>
                <IdCentroImposicion>2</IdCentroImposicion>
                <Calle>BLVD. BUENOS AIRES</Calle>
                <Numero>1459</Numero>
                <Localidad>LUIS GUILLON</Localidad>
                <Provincia>BUENOS AIRES</Provincia>
                <Telefono>4367-5729</Telefono>
                <Latitud>-34.8098435</Latitud>
                <Longitud>-58.4477191</Longitud>
                <TipoAgencia>Sucursal OCA</TipoAgencia>
                <Sigla>ADG</Sigla>
                <Sucursal>SUCURSAL OCA: LUIS GUILLÓN</Sucursal>
                <Servicios>
                    <Servicio>
                        <IdTipoServicio>1</IdTipoServicio>
                        <ServicioDesc>Admisión de paquetes</ServicioDesc>
                    </Servicio>
                    <Servicio>
                        <IdTipoServicio>2</IdTipoServicio>
                        <ServicioDesc>Entrega de paquetes</ServicioDesc>
                    </Servicio>
                </Servicios>
            </Centro>
        </CentrosDeImposicion>"""
        mock_response = MagicMock()
        mock_response.GetServiciosDeCentrosImposicionResult = xml_response
        mock_client.GetServiciosDeCentrosImposicion.return_value = mock_response

        result = oca_service.getServiciosDeCentrosImposicion()

        assert len(result) == 1
        assert result[0]["IdCentroImposicion"] == "2"
        assert result[0]["Calle"] == "BLVD. BUENOS AIRES"
        assert result[0]["Localidad"] == "LUIS GUILLON"
        assert result[0]["Sigla"] == "ADG"
        assert "Servicios" in result[0]
        assert len(result[0]["Servicios"]) == 2
        assert result[0]["Servicios"][0]["IdTipoServicio"] == "1"
        assert result[0]["Servicios"][0]["ServicioDesc"] == "Admisión de paquetes"

    def test_get_servicios_de_centros_imposicion_calls_correct_soap_method(
        self, oca_service
    ):
        """Verify getServiciosDeCentrosImposicion calls correct SOAP method."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetServiciosDeCentrosImposicionResult = (
            "<CentrosDeImposicion></CentrosDeImposicion>"
        )
        mock_client.GetServiciosDeCentrosImposicion.return_value = mock_response

        oca_service.getServiciosDeCentrosImposicion()

        mock_client.GetServiciosDeCentrosImposicion.assert_called_once_with()

    def test_get_servicios_de_centros_imposicion_empty_response(self, oca_service):
        """Verify getServiciosDeCentrosImposicion handles empty response."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetServiciosDeCentrosImposicionResult = (
            "<CentrosDeImposicion></CentrosDeImposicion>"
        )
        mock_client.GetServiciosDeCentrosImposicion.return_value = mock_response

        result = oca_service.getServiciosDeCentrosImposicion()

        assert result == []

    def test_get_servicios_de_centros_imposicion_soap_error(self, oca_service):
        """Verify getServiciosDeCentrosImposicion handles SOAP errors."""
        mock_client = oca_service._mock_client
        mock_client.GetServiciosDeCentrosImposicion.side_effect = Exception(
            "SOAP Error"
        )

        with pytest.raises(Exception) as exc_info:
            oca_service.getServiciosDeCentrosImposicion()

        assert "SOAP Error" in str(exc_info.value)

    def test_parse_nested_list_result_with_nested_elements(self):
        """Verify parse_nested_list_result handles nested elements."""
        xml_string = """<?xml version="1.0" encoding="utf-8"?>
        <Root>
            <Item>
                <Id>1</Id>
                <Name>Test</Name>
                <Children>
                    <Child>
                        <ChildId>1a</ChildId>
                        <ChildName>Child 1</ChildName>
                    </Child>
                    <Child>
                        <ChildId>1b</ChildId>
                        <ChildName>Child 2</ChildName>
                    </Child>
                </Children>
            </Item>
        </Root>"""

        result = OcaService.parse_nested_list_result(xml_string, "Item", "Child")

        assert len(result) == 1
        assert result[0]["Id"] == "1"
        assert result[0]["Name"] == "Test"
        assert "Children" in result[0]
        assert len(result[0]["Children"]) == 2
        assert result[0]["Children"][0]["ChildId"] == "1a"
        assert result[0]["Children"][1]["ChildName"] == "Child 2"

    def test_parse_nested_list_result_without_nested(self):
        """Verify parse_nested_list_result works without nested elements."""
        xml_string = """<?xml version="1.0" encoding="utf-8"?>
        <Root>
            <Item>
                <Id>1</Id>
                <Name>Test</Name>
            </Item>
            <Item>
                <Id>2</Id>
                <Name>Test 2</Name>
            </Item>
        </Root>"""

        result = OcaService.parse_nested_list_result(xml_string, "Item")

        assert len(result) == 2
        assert result[0]["Id"] == "1"
        assert result[1]["Name"] == "Test 2"

    # ============================================================
    # ELOCKER TESTS
    # ============================================================

    def test_get_elocker_oca_returns_list(self, oca_service):
        """Verify getELockerOCA returns list of eLockers."""
        mock_client = oca_service._mock_client

        # Setup mock for iterateresult (DataSet with Table elements)
        mock_result = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = """<?xml version="1.0" encoding="utf-8"?>
        <DataSet>
            <Table>
                <IDLocker>5199</IDLocker>
                <Sigla>62A</Sigla>
                <Descripcion>SmartLocker OCA - ParkingCity</Descripcion>
                <Calle>Maipu</Calle>
                <Numero>119</Numero>
                <Localidad>ALBERDI</Localidad>
                <Provincia>CORDOBA</Provincia>
                <CodigoPostal>5000</CodigoPostal>
            </Table>
        </DataSet>"""
        mock_result.__getitem__.return_value = inner_mock
        mock_client.GetELockerOCA.return_value = mock_result

        result = oca_service.getELockerOCA()

        assert len(result) == 1
        assert result[0]["IDLocker"] == 5199
        assert result[0]["Sigla"] == b"62A"
        assert result[0]["Descripcion"] == b"SmartLocker OCA - ParkingCity"

    def test_get_elocker_oca_calls_correct_soap_method(self, oca_service):
        """Verify getELockerOCA calls correct SOAP method."""
        mock_client = oca_service._mock_client
        mock_result = MagicMock()
        inner_mock = MagicMock()
        inner_mock.as_xml.return_value = "<DataSet></DataSet>"
        mock_result.__getitem__.return_value = inner_mock
        mock_client.GetELockerOCA.return_value = mock_result

        oca_service.getELockerOCA()

        mock_client.GetELockerOCA.assert_called_once_with()

    # ============================================================
    # SERVICES BY PROVINCE TESTS
    # ============================================================

    def test_get_servicios_por_provincia_returns_filtered_list(self, oca_service):
        """Verify getServiciosDeCentrosImposicionPorProvincia returns filtered centers."""
        mock_client = oca_service._mock_client
        xml_response = """<?xml version="1.0" encoding="utf-8"?>
        <CentrosDeImposicion>
            <Centro>
                <IdCentroImposicion>9</IdCentroImposicion>
                <Calle>VIAMONTE</Calle>
                <Localidad>CAPITAL FEDERAL</Localidad>
                <Provincia>CAPITAL FEDERAL</Provincia>
                <Servicios>
                    <Servicio>
                        <IdTipoServicio>1</IdTipoServicio>
                        <ServicioDesc>Admisión de paquetes</ServicioDesc>
                    </Servicio>
                </Servicios>
            </Centro>
        </CentrosDeImposicion>"""
        mock_response = MagicMock()
        mock_response.GetServiciosDeCentrosImposicion_xProvinciaResult = xml_response
        mock_client.GetServiciosDeCentrosImposicion_xProvincia.return_value = (
            mock_response
        )

        result = oca_service.getServiciosDeCentrosImposicionPorProvincia(
            1, "CAPITAL FEDERAL"
        )

        assert len(result) == 1
        assert result[0]["IdCentroImposicion"] == "9"
        assert "Servicios" in result[0]

    def test_get_servicios_por_provincia_calls_with_params(self, oca_service):
        """Verify getServiciosDeCentrosImposicionPorProvincia passes correct parameters."""
        mock_client = oca_service._mock_client
        mock_response = MagicMock()
        mock_response.GetServiciosDeCentrosImposicion_xProvinciaResult = (
            "<CentrosDeImposicion></CentrosDeImposicion>"
        )
        mock_client.GetServiciosDeCentrosImposicion_xProvincia.return_value = (
            mock_response
        )

        oca_service.getServiciosDeCentrosImposicionPorProvincia(2, "CORDOBA")

        mock_client.GetServiciosDeCentrosImposicion_xProvincia.assert_called_once_with(
            provinciaID=2, localidad="CORDOBA"
        )

    # ============================================================
    # TRACKING ENVIO ESTADO ACTUAL TESTS
    # ============================================================

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

    # ============================================================
    # QR CODE GENERATION TESTS
    # ============================================================

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

    # ============================================================
    # CONSOLIDACION DE ORDENES TESTS
    # ============================================================

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

    # ============================================================
    # LABEL METHODS TESTS
    # ============================================================

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
        mock_client.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvio.assert_called_once_with(
            idOrdenRetiro=12345, nroEnvio="987654321"
        )

    def test_get_html_para_etiquetadora_returns_html(self, oca_service):
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
