"""Tests for XML parsing methods."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock
from ocaepak.client import OcaService
from tests.client.conftest import create_xml_mock


class TestParsing:
    """Test class for XML parsing methods."""

    def test_iterateresult_converts_integers(self, sample_xml_single_table):
        """Verify integer fields are converted to int type."""
        mock_xml_result = create_xml_mock(sample_xml_single_table)
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
        mock_xml_result = create_xml_mock(sample_xml_single_table)
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
        mock_xml_result = create_xml_mock(sample_xml_single_table)
        result = OcaService.iterateresult("StatusResult", mock_xml_result)

        assert len(result) == 1
        assert isinstance(result[0]["fecha"], datetime)
        assert result[0]["fecha"].year == 2024
        assert result[0]["fecha"].month == 1
        assert result[0]["fecha"].day == 15

    def test_iterateresult_encodes_strings_to_utf8(self, sample_xml_single_table):
        """Verify string fields are encoded to UTF-8."""
        mock_xml_result = create_xml_mock(sample_xml_single_table)
        result = OcaService.iterateresult("CentroResult", mock_xml_result)

        assert len(result) == 1
        assert isinstance(result[0]["Nombre"], bytes)
        assert result[0]["Nombre"].decode("utf-8") == "Centro Principal"
        assert isinstance(result[0]["Localidad"], bytes)
        assert result[0]["Localidad"].decode("utf-8") == "Buenos Aires"

    def test_iterateresult_handles_multiple_tables(self, sample_xml_multiple_tables):
        """Verify multiple Table elements return list of dicts."""
        mock_xml_result = create_xml_mock(sample_xml_multiple_tables)
        result = OcaService.iterateresult("CentrosResult", mock_xml_result)

        assert len(result) == 2
        assert result[0]["Numero"] == 1001
        assert result[1]["Numero"] == 1002

    def test_iterateresult_skips_empty_values(self, sample_xml_empty_values):
        """Verify empty/whitespace values are skipped."""
        mock_xml_result = create_xml_mock(sample_xml_empty_values)
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
        mock_xml_result = create_xml_mock(xml_with_bad_date)

        with pytest.raises(ValueError):
            OcaService.iterateresult("BadDateResult", mock_xml_result)

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
        mock_xml_result = create_xml_mock(
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
        mock_xml_result = create_xml_mock(xml_with_bad_number)

        with pytest.raises(ValueError):
            OcaService.iterateresult("BadNum", mock_xml_result)
