"""Shared fixtures for client tests."""

import pytest
from unittest.mock import MagicMock
from ocaepak.client import OcaService


@pytest.fixture
def mock_soap_client(mocker):
    """Mock the SoapClient class."""
    return mocker.patch("ocaepak.client.SoapClient")


@pytest.fixture
def mock_logger(mocker):
    """Mock the logger for ingresarOR tests."""
    return mocker.patch("ocaepak.client.logger")


@pytest.fixture
def oca_service(mock_soap_client):
    """Create OcaService instance with mocked SOAP client."""
    mock_instance = mock_soap_client.return_value
    service = OcaService("test_user", "test_pass", "20-12345678-9")
    service._mock_client = mock_instance
    return service


@pytest.fixture
def sample_xml_single_table():
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
def sample_xml_multiple_tables():
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
def sample_xml_empty_values():
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
def sample_compra_data():
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


def create_xml_mock(xml_string):
    """Helper to create a properly configured XML mock."""
    mock_result = MagicMock()
    inner_mock = MagicMock()
    inner_mock.as_xml.return_value = xml_string
    mock_result.__getitem__.return_value = inner_mock
    return mock_result


def create_soap_mock(xml_string):
    """Helper to create a mock SOAP response."""
    mock_response = MagicMock()
    inner_mock = MagicMock()
    inner_mock.as_xml.return_value = xml_string
    mock_response.__getitem__.return_value = inner_mock
    return mock_response
