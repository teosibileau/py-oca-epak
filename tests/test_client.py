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
            "idProvincia",
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
        <DataSet>
            <Table>
                <idProvincia>1</idProvincia>
                <Nombre>Buenos Aires</Nombre>
            </Table>
            <Table>
                <idProvincia>2</idProvincia>
                <Nombre>Cordoba</Nombre>
            </Table>
        </DataSet>"""
        mock_client.GetProvincias.return_value = self._create_soap_mock(xml_response)

        result = oca_service.getProvincias()

        assert len(result) == 2
        assert result[0]["idProvincia"] == 1
        assert result[0]["Nombre"] == b"Buenos Aires"
        assert result[1]["idProvincia"] == 2
        assert result[1]["Nombre"] == b"Cordoba"

    def test_get_provincias_calls_correct_soap_method(self, oca_service):
        """Verify getProvincias calls GetProvincias with no params."""
        mock_client = oca_service._mock_client
        mock_client.GetProvincias.return_value = self._create_soap_mock(
            "<DataSet><Table><idProvincia>1</idProvincia></Table></DataSet>"
        )

        oca_service.getProvincias()

        mock_client.GetProvincias.assert_called_once_with()

    def test_get_provincias_empty_response(self, oca_service):
        """Verify getProvincias handles empty response."""
        mock_client = oca_service._mock_client
        mock_client.GetProvincias.return_value = self._create_soap_mock(
            "<DataSet></DataSet>"
        )

        result = oca_service.getProvincias()

        assert result == []

    def test_get_provincias_soap_error(self, oca_service):
        """Verify getProvincias handles SOAP errors."""
        mock_client = oca_service._mock_client
        mock_client.GetProvincias.side_effect = Exception("SOAP Fault")

        with pytest.raises(Exception) as exc_info:
            oca_service.getProvincias()

        assert "SOAP Fault" in str(exc_info.value)
