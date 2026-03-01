"""Tests for OcaService class constants and attributes."""

from ocaepak.client import OcaService


class TestConstants:
    """Test class constants and attributes."""

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
