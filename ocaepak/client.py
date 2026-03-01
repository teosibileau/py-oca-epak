from pysimplesoap.client import SoapClient
from xml.etree import ElementTree as ET

from datetime import datetime


import os
import logging
from jinja2 import Template

ROOT = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


class OcaService:
    WSDL_BASE_URI = "http://webservice.oca.com.ar/oep_tracking/Oep_Track.asmx"
    OCA_WDSL = "%s?WSDL" % WSDL_BASE_URI
    LABELS_FOR_INTEGERS = [
        "Numero",
        "Piso",
        "idCentroImposicion",
        "idTipoSercicio",
        "PlazoEntrega",
        "Tarifador",
        "IDLocker",
    ]
    LABELS_FOR_FLOATS = ["Precio", "Adicional", "Total"]
    LABELS_FOR_DATETIMES = ["fecha"]

    OPERATIVAS = {
        72767: "Punto a Punto Estandar con Seguro / Pago en Destino",
        72768: "Punto a Sucursal Estandar con Seguro / Pago en Destino",
        72769: "Punto a Punto Prioritario con Seguro / Pago en Destino",
        72770: "Punto a Sucursal Prioritario con Seguro / Pago en Destino",
        72771: "Punto a Punto Estandar / Pago en Destino",
        72772: "Punto a Sucursal Estandar / Pago en Destino",
        72951: "Punto a Punto Estandar con Seguro / Pago en Destino",
        72952: "Punto a Sucursal Estandar con Seguro / Pago en Destino",
        72954: "Punto a Punto Estandar con Seguro / Pago en Destino",
        72953: "Punto a Punto Prioritario con Seguro / Pago en Destino",
        72955: "Punto a Sucursal Prioritario con Seguro / Pago en Destino",
    }

    FRANJAS_HORARIAS = {
        1: "8 a 17hs",
        2: "8 a 12hs",
        3: "14 a 17hs",
    }

    @staticmethod
    def iterateresult(id_result, xml_result):
        tree = ET.fromstring(str(xml_result[id_result].as_xml()))
        r = []
        for node in tree.iter("Table"):
            t = {}
            for field in node.iter():
                if field.tag != "Table" and field.text:
                    value = field.text.strip()
                    if value:
                        if field.tag in OcaService.LABELS_FOR_INTEGERS:
                            value = int(value)
                        elif field.tag in OcaService.LABELS_FOR_FLOATS:
                            value = float(value)
                        elif field.tag in OcaService.LABELS_FOR_DATETIMES:
                            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S-03:00")
                        else:
                            value = value.encode("utf-8")
                        t[field.tag] = value
            r.append(t)
        return r

    @staticmethod
    def parse_list_result(xml_string, item_tag):
        """Parse XML list results (like Provincias, Localidades).

        Args:
            xml_string: XML content to parse
            item_tag: Tag name for individual items (e.g., 'Provincia')

        Returns:
            List of dictionaries with field names as keys
        """
        tree = ET.fromstring(xml_string)
        result = []
        for item in tree.iter(item_tag):
            row = {}
            for field in item:
                if field.text:
                    row[field.tag] = field.text.strip()
            result.append(row)
        return result

    def __init__(self, user, password, cuit, trace=False):
        self.user = user
        self.password = password
        self.CUIT = cuit
        self.client = SoapClient(
            wsdl=OcaService.OCA_WDSL,
            location=OcaService.WSDL_BASE_URI,
            exceptions=True,
            trace=trace,
        )

    def anularOrdenGenerada(self, orden):
        soap_response = self.client.AnularOrdenGenerada(
            usuario=self.user, password=self.password, nroOrden=orden
        )
        return self.iterateresult("AnularOrdenGeneradaResult", soap_response)

    def centroCostoPorOperativa(self, operativa):
        soap_response = self.client.GetCentroCostorPorOperativa(
            CUIT=self.CUIT, Operativa=operativa
        )
        return self.iterateresult("GetCentroCostorPorOperativaResult", soap_response)

    def centrosDeImposicion(self):
        soap_response = self.client.GetCentrosImposicion()
        return self.iterateresult("GetCentrosImposicionResult", soap_response)

    def centrosDeImposicionPorCP(self, cp):
        soap_response = self.client.GetCentrosImposicionPorCP(CodigoPostal=cp)
        return self.iterateresult("GetCentrosImposicionPorCPResult", soap_response)

    def ingresarOR(self, compra, dias_retiro, franja_horaria, confirmar_retiro=False):
        t_file = open(os.path.join(ROOT, "templates", "retiro.xml"))
        template = [line for line in t_file.readlines()]
        template = Template("".join(template))
        template_render = template.render(compra).replace("\t", "").replace("\n", "")
        logger.info(template_render)
        r = self.client.IngresoOR(
            usr=self.user,
            psw=self.password,
            XML_Retiro=template_render,
            ConfirmarRetiro="true" if confirmar_retiro else "false",
            DiasRetiro=dias_retiro,
            FranjaHoraria=franja_horaria,
        )
        return r

    def estadoUltimosEnvios(self, operativas, from_date, to_date):
        soap_response = self.client.GetEnviosUltimoEstado(
            cuit=self.CUIT,
            operativas=operativas,
            fechaDesta=from_date.strftime("%d/%m/%Y"),
            fechaHasta=to_date.strftime("%d/%m/%Y"),
        )
        return self.iterateresult("GetEnviosUltimoEstadoResult", soap_response)

    def listEnvios(self, from_date, to_date):
        soap_response = self.client.List_Envios(
            CUIT=self.CUIT,
            FechaDesde=from_date.strftime("%d/%m/%Y"),
            FechaHasta=to_date.strftime("%d/%m/%Y"),
        )
        return self.iterateresult("List_EnviosResult", soap_response)

    def tarifarEnvioCorporativo(
        self, peso_total, volumen_total, cp_origen, cp_destino, n_paquetes, operativa
    ):
        soap_response = self.client.Tarifar_Envio_Corporativo(
            PesoTotal=peso_total,
            VolumenTotal=volumen_total,
            CodigoPostalOrigen=cp_origen,
            CodigoPostalDestino=cp_destino,
            CantidadPaquetes=n_paquetes,
            Cuit=self.CUIT,
            Operativa=operativa,
        )
        return self.iterateresult("Tarifar_Envio_CorporativoResult", soap_response)

    def trackingOR(self, orden_retiro):
        soap_response = self.client.Tracking_OrdenRetiro(
            CUIT=self.CUIT, OrdenRetiro=orden_retiro
        )
        return self.iterateresult("Tracking_OrdenRetiroResult", soap_response)

    def trackingPiezaConID(self, pieza):
        soap_response = self.client.Tracking_Pieza(Pieza=pieza)
        return self.iterateresult("Tracking_PiezaResult", soap_response)

    def trackingPiezaConDNICUIT(self, nro_documento, cuit):
        soap_response = self.client.Tracking_Pieza(
            NroDocumentoCliente=nro_documento, CUIT=cuit
        )
        return self.iterateresult("Tracking_PiezaResult", soap_response)

    def getProvincias(self):
        """Get list of provinces with caching."""
        if not hasattr(self, "_provincias_cache"):
            soap_response = self.client.GetProvincias()
            xml_content = soap_response.GetProvinciasResult
            self._provincias_cache = self.parse_list_result(xml_content, "Provincia")
        return self._provincias_cache

    def centrosDeImposicionAdmision(self):
        """Get all admission centers for package drop-off."""
        soap_response = self.client.GetCentrosImposicionAdmision()
        return self.iterateresult("GetCentrosImposicionAdmisionResult", soap_response)

    def centrosDeImposicionAdmisionPorCP(self, cp):
        """Get admission centers near a postal code.

        Args:
            cp: Postal code to search near
        """
        soap_response = self.client.GetCentrosImposicionAdmisionPorCP(CodigoPostal=cp)
        return self.iterateresult(
            "GetCentrosImposicionAdmisionPorCPResult", soap_response
        )

    def getLocalidadesByProvincia(self, id_provincia):
        """Get all localities for a given province with caching.

        Args:
            id_provincia: Province ID to search localities for
        """
        if not hasattr(self, "_localidades_cache"):
            self._localidades_cache = {}

        if id_provincia not in self._localidades_cache:
            soap_response = self.client.GetLocalidadesByProvincia(
                idProvincia=id_provincia
            )
            xml_content = soap_response.GetLocalidadesByProvinciaResult
            self._localidades_cache[id_provincia] = self.parse_list_result(
                xml_content, "Provincia"
            )

        return self._localidades_cache[id_provincia]

    def clear_cache(self):
        """Clear cached province and localities data."""
        if hasattr(self, "_provincias_cache"):
            delattr(self, "_provincias_cache")
        if hasattr(self, "_localidades_cache"):
            delattr(self, "_localidades_cache")

    @staticmethod
    def parse_nested_list_result(xml_string, item_tag, nested_tag=None):
        """Parse XML list results with optional nested elements.

        Args:
            xml_string: XML content to parse
            item_tag: Tag name for individual items (e.g., 'Centro')
            nested_tag: Optional tag name for nested lists (e.g., 'Servicio')

        Returns:
            List of dictionaries with field names as keys.
            If nested_tag is provided, nested elements are parsed as lists.
        """
        tree = ET.fromstring(xml_string)
        result = []

        for item in tree.iter(item_tag):
            row = {}
            for field in item:
                # Check for nested elements first (container elements)
                if nested_tag:
                    nested_items = list(field.iter(nested_tag))
                    if nested_items:
                        # This field contains nested elements - parse them
                        row[field.tag] = []
                        for nested_item in nested_items:
                            nested_row = {}
                            for nested_field in nested_item:
                                if nested_field.text and nested_field.text.strip():
                                    nested_row[nested_field.tag] = (
                                        nested_field.text.strip()
                                    )
                            if nested_row:
                                row[field.tag].append(nested_row)
                    elif field.text and field.text.strip():
                        # Simple text field
                        row[field.tag] = field.text.strip()
                elif field.text and field.text.strip():
                    # No nested tag specified, just parse text fields
                    row[field.tag] = field.text.strip()
            result.append(row)

        return result

    def getServiciosDeCentrosImposicion(self):
        """Get all services for each pickup center.

        Returns a list of centers with their details and available services.
        Each center includes address, contact info, location coordinates,
        and a list of services offered at that location.

        Returns:
            List of dictionaries containing center information:
            - IdCentroImposicion: Center ID
            - Calle: Street address
            - Numero: Street number
            - Piso: Floor (if applicable)
            - Depto: Apartment (if applicable)
            - Localidad: City
            - Provincia: Province
            - Telefono: Phone number
            - Latitud: Latitude coordinate
            - Longitud: Longitude coordinate
            - TipoAgencia: Agency type
            - Sigla: Center code/symbol
            - Sucursal: Branch name
            - Servicios: List of services with:
                - IdTipoServicio: Service type ID
                - ServicioDesc: Service description
        """
        soap_response = self.client.GetServiciosDeCentrosImposicion()
        xml_content = soap_response.GetServiciosDeCentrosImposicionResult
        return self.parse_nested_list_result(xml_content, "Centro", "Servicio")

    def getELockerOCA(self):
        """Get all available OCA eLockers (Smart Lockers).

        Returns a list of available OCA eLockers (smart locker locations)
        with their addresses and identification codes.

        Returns:
            List of dictionaries containing locker information:
            - IDLocker: Locker ID
            - Sigla: Locker code
            - Descripcion: Description
            - Calle: Street address
            - Numero: Street number
            - Piso: Floor (if applicable)
            - Localidad: City
            - Provincia: Province
            - CodigoPostal: Postal code
        """
        soap_response = self.client.GetELockerOCA()
        return self.iterateresult("GetELockerOCAResult", soap_response)

    def getServiciosDeCentrosImposicionPorProvincia(self, provincia_id, localidad=""):
        """Get services by center filtered by province and locality.

        Similar to getServiciosDeCentrosImposicion but allows filtering
        by province ID and optionally by locality name.

        Args:
            provincia_id (int): Province ID to filter by
            localidad (str, optional): Locality/city name to filter by.
                                      Defaults to empty string (no filter).

        Returns:
            List of dictionaries containing center information with services,
            filtered by province and optionally locality.
        """
        soap_response = self.client.GetServiciosDeCentrosImposicion_xProvincia(
            provinciaID=provincia_id, localidad=localidad
        )
        xml_content = soap_response.GetServiciosDeCentrosImposicion_xProvinciaResult
        return self.parse_nested_list_result(xml_content, "Centro", "Servicio")
