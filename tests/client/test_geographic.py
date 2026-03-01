"""Tests for geographic and location services."""

import pytest
from unittest.mock import MagicMock
from ocaepak.client import OcaService
from tests.client.conftest import create_soap_mock


class TestGeographic:
    """Tests for location services including provinces, localities, and centers."""

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
        mock_client.GetCentrosImposicionAdmision.return_value = create_soap_mock(
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
        mock_client.GetCentrosImposicionAdmision.return_value = create_soap_mock(
            "<DataSet><Table><idCentroImposicion>1</idCentroImposicion></Table></DataSet>"
        )

        oca_service.centrosDeImposicionAdmision()

        mock_client.GetCentrosImposicionAdmision.assert_called_once_with()

    def test_centros_de_imposicion_admision_empty_response(self, oca_service):
        """Verify centrosDeImposicionAdmision handles empty response."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmision.return_value = create_soap_mock(
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
        mock_client.GetCentrosImposicionAdmisionPorCP.return_value = create_soap_mock(
            xml_response
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
        mock_client.GetCentrosImposicionAdmisionPorCP.return_value = create_soap_mock(
            "<DataSet><Table><idCentroImposicion>1</idCentroImposicion></Table></DataSet>"
        )

        oca_service.centrosDeImposicionAdmisionPorCP(5000)

        mock_client.GetCentrosImposicionAdmisionPorCP.assert_called_once_with(
            CodigoPostal=5000
        )

    def test_centros_de_imposicion_admision_por_cp_empty_response(self, oca_service):
        """Verify centrosDeImposicionAdmisionPorCP handles empty response."""
        mock_client = oca_service._mock_client
        mock_client.GetCentrosImposicionAdmisionPorCP.return_value = create_soap_mock(
            "<DataSet></DataSet>"
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

    def test_get_elocker_oca_returns_list(self, oca_service):
        """Verify getELockerOCA returns list of eLockers."""
        mock_client = oca_service._mock_client

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
