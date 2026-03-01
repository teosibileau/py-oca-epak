"""Tests for OcaService initialization."""

from ocaepak.client import OcaService


class TestInitialization:
    """Test class for OcaService initialization."""

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
