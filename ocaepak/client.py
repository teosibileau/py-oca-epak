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
        "NumeroEnvio",
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

    def trackingEnvioEstadoActual(self, numero_envio):
        """Get current shipment status with branch position.

        Returns shipment data with the current status and the global
        position of the branch where the package is currently located.

        Args:
            numero_envio (str): Shipment/tracking number

        Returns:
            List of dictionaries with current tracking information including:
            - Current status of the shipment
            - Branch position information
            - Location details
        """
        soap_response = self.client.TrackingEnvio_EstadoActual(numeroEnvio=numero_envio)
        return self.iterateresult("TrackingEnvio_EstadoActualResult", soap_response)

    def generateQrByOrdenDeRetiro(self, id_orden_retiro):
        """Generate QR code for a pickup order.

        Generates a base64 encoded QR code string for the given
        pickup order ID.

        Args:
            id_orden_retiro (str): Pickup order ID

        Returns:
            str: Base64 encoded QR code string
        """
        soap_response = self.client.GenerateQrByOrdenDeRetiro(
            usr=self.user, psw=self.password, idOrdenDeRetiro=id_orden_retiro
        )
        return soap_response.GenerateQrByOrdenDeRetiroResult

    def generateQrParaPaquetes(self, numero_envio, id_paquete):
        """Generate QR code for a package.

        Generates a base64 encoded QR code string for a specific
        package within a shipment.

        Args:
            numero_envio (str): Shipment/tracking number
            id_paquete (str): Package ID

        Returns:
            str: Base64 encoded QR code string
        """
        soap_response = self.client.GenerateQRParaPaquetes(
            usr=self.user,
            psw=self.password,
            numeroDeEnvio=numero_envio,
            idpaquete=id_paquete,
        )
        return soap_response.GenerateQRParaPaquetesResult

    def generateListQrPorEnvio(self, numero_envio):
        """Generate QR codes list for a shipment.

        Generates a list of base64 encoded QR code strings for all
        packages within a shipment.

        Args:
            numero_envio (str): Shipment/tracking number

        Returns:
            list: List of base64 encoded QR code strings
        """
        soap_response = self.client.GenerateListQrPorEnvio(
            usr=self.user, psw=self.password, numeroDeEnvio=numero_envio
        )
        return soap_response.GenerateListQrPorEnvioResult

    def generarConsolidacionDeOrdenesDeRetiro(self, ordenes):
        """Consolidate multiple pickup orders into one.

        This method consolidates multiple pickup orders (Ordenes de Retiro)
        into a single consolidated order. It returns the consolidation ID
        and the count of orders that were included.

        Args:
            ordenes (list): List of pickup order IDs to consolidate

        Returns:
            dict: Dictionary containing:
                - IdDeConsolidacion: Consolidation ID
                - CantidadDeOrdenes: Number of orders consolidated
        """
        # Convert list to comma-separated string
        ordenes_str = ",".join(str(o) for o in ordenes)
        soap_response = self.client.GenerarConsolidacionDeOrdenesDeRetiro(
            usr=self.user, psw=self.password, ordenesDeRetiro=ordenes_str
        )
        # Parse the response which is in format "IdDeConsolidacion|CantidadDeOrdenes"
        result_str = soap_response.GenerarConsolidacionDeOrdenesDeRetiroResult
        if result_str and "|" in result_str:
            parts = result_str.split("|")
            return {
                "IdDeConsolidacion": parts[0],
                "CantidadDeOrdenes": int(parts[1]) if len(parts) > 1 else 0,
            }
        return {"IdDeConsolidacion": result_str, "CantidadDeOrdenes": 0}

    # ============================================================
    # LABEL METHODS
    # ============================================================

    def getCSSDeEtiquetasPorOrdenOrNumeroEnvio(self, para_etiquetadora=False):
        """Get CSS styles for labels.

        Obtains the CSS styles for the base HTML code of labels
        belonging to a pickup order.

        Args:
            para_etiquetadora (bool): Whether the CSS is for a label printer

        Returns:
            str: CSS styles as a string
        """
        soap_response = self.client.GetCSSDeEtiquetasPorOrdenOrNumeroEnvio(
            paraEtiquetadora=para_etiquetadora
        )
        return soap_response.GetCSSDeEtiquetasPorOrdenOrNumeroEnvioResult

    def getDatosDeEtiquetasPorOrdenOrNumeroEnvio(
        self, id_orden_retiro, nro_envio=None, is_locker=False
    ):
        """Get label data for a pickup order or shipment.

        Obtains the source code of labels belonging to a pickup order
        or shipment number.

        Args:
            id_orden_retiro (int): Pickup order ID (required)
            nro_envio (str, optional): Shipment number
            is_locker (bool): Whether it's a locker delivery

        Returns:
            list: List of dictionaries with label data (Etiqueta objects)
        """
        soap_response = self.client.GetDatosDeEtiquetasPorOrdenOrNumeroEnvio(
            idOrdenRetiro=id_orden_retiro,
            nroEnvio=nro_envio if nro_envio else "",
            isLocker=is_locker,
        )
        # Parse the Etiqueta elements from the response
        xml_content = soap_response.GetDatosDeEtiquetasPorOrdenOrNumeroEnvioResult
        return self.parse_nested_list_result(xml_content, "Etiqueta")

    def getDivDeEtiquetaByIdPieza(self, id_pieza):
        """Get HTML div for a label by piece ID.

        Obtains the HTML div element for a label identified by piece ID.

        Args:
            id_pieza (str): Piece ID

        Returns:
            str: HTML div as a string
        """
        soap_response = self.client.GetDivDeEtiquetaByIdPieza(idPieza=id_pieza)
        return soap_response.GetDivDeEtiquetaByIdPiezaResult

    def getDivDeEtiquetasPorOrdenOrNumeroEnvio(self, id_orden_retiro, nro_envio=None):
        """Get HTML divs for labels by order or shipment.

        Obtains the HTML div elements for labels belonging to a pickup
        order or shipment number.

        Args:
            id_orden_retiro (int): Pickup order ID
            nro_envio (str, optional): Shipment number

        Returns:
            str: HTML divs as a string
        """
        soap_response = self.client.GetDivDeEtiquetasPorOrdenOrNumeroEnvio(
            idOrdenRetiro=id_orden_retiro, nroEnvio=nro_envio if nro_envio else ""
        )
        return soap_response.GetDivDeEtiquetasPorOrdenOrNumeroEnvioResult

    def getHtmlDeEtiquetasPorOrdenOrNumeroEnvio(self, id_orden_retiro, nro_envio=None):
        """Get full HTML for labels by order or shipment.

        Obtains the complete HTML source code for labels belonging to
        a pickup order or shipment number.

        Args:
            id_orden_retiro (int): Pickup order ID (required)
            nro_envio (str, optional): Shipment number

        Returns:
            str: Complete HTML as a string
        """
        soap_response = self.client.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvio(
            idOrdenRetiro=id_orden_retiro, nroEnvio=nro_envio if nro_envio else ""
        )
        return soap_response.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvioResult

    def getHtmlDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora(
        self, id_orden_retiro, nro_envio=None
    ):
        """Get HTML for labels formatted for label printer.

        Obtains the HTML source code for labels formatted specifically
        for label printers.

        Args:
            id_orden_retiro (int): Pickup order ID (required)
            nro_envio (str, optional): Shipment number

        Returns:
            str: HTML formatted for label printer as a string
        """
        soap_response = (
            self.client.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora(
                idOrdenRetiro=id_orden_retiro,
                nroEnvio=nro_envio if nro_envio else "",
            )
        )
        return (
            soap_response.GetHtmlDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadoraResult
        )

    def getHtmlDeEtiquetasPorOrdenes(self, id_ordenes):
        """Get HTML for labels from multiple orders.

        Obtains the HTML source code for labels from multiple pickup orders.

        Args:
            id_ordenes (list): List of pickup order IDs

        Returns:
            str: HTML as a string
        """
        # Convert list to comma-separated string
        ordenes_str = ",".join(str(o) for o in id_ordenes)
        soap_response = self.client.GetHtmlDeEtiquetasPorOrdenes(idOrdenes=ordenes_str)
        return soap_response.GetHtmlDeEtiquetasPorOrdenesResult

    def getPdfDeEtiquetasPorOrdenOrNumeroEnvio(
        self, id_orden_retiro, nro_envio=None, logistica_inversa=False
    ):
        """Get PDF for labels by order or shipment.

        Obtains a PDF containing labels belonging to a pickup order
        or shipment number.

        Args:
            id_orden_retiro (int): Pickup order ID (required)
            nro_envio (str, optional): Shipment number
            logistica_inversa (bool): Whether it's reverse logistics

        Returns:
            str: Base64 encoded PDF as a string
        """
        soap_response = self.client.GetPdfDeEtiquetasPorOrdenOrNumeroEnvio(
            idOrdenRetiro=id_orden_retiro,
            nroEnvio=nro_envio if nro_envio else "",
            logisticaInversa=logistica_inversa,
        )
        return soap_response.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioResult

    def getPdfDeEtiquetasPorOrdenOrNumeroEnvioAdidas(
        self, id_orden_retiro, nro_envio=None
    ):
        """Get Adidas-specific PDF for labels.

        Obtains an Adidas-specific PDF containing labels belonging to
        a pickup order or shipment number.

        Args:
            id_orden_retiro (int): Pickup order ID (required)
            nro_envio (str, optional): Shipment number

        Returns:
            str: Base64 encoded PDF as a string
        """
        soap_response = self.client.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioAdidas(
            idOrdenRetiro=id_orden_retiro, nroEnvio=nro_envio if nro_envio else ""
        )
        return soap_response.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioAdidasResult

    def getPdfDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora(
        self, id_orden_retiro, nro_envio=None
    ):
        """Get PDF for labels formatted for label printer.

        Obtains a PDF containing labels formatted specifically for
        label printers.

        Args:
            id_orden_retiro (int): Pickup order ID (required)
            nro_envio (str, optional): Shipment number

        Returns:
            str: Base64 encoded PDF as a string
        """
        soap_response = (
            self.client.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadora(
                idOrdenRetiro=id_orden_retiro,
                nroEnvio=nro_envio if nro_envio else "",
            )
        )
        return (
            soap_response.GetPdfDeEtiquetasPorOrdenOrNumeroEnvioParaEtiquetadoraResult
        )

    def obtenerEtiquetasZPL(
        self, orden_retiro=None, numero_envio=None, numero_bulto=None
    ):
        """Get ZPL code for labels.

        Obtains ZPL (Zebra Programming Language) code for labels.
        At least one of orden_retiro or numero_envio must be provided.
        If numero_bulto is provided, numero_envio is required.

        Args:
            orden_retiro (str, optional): Pickup order ID
            numero_envio (str, optional): Shipment number
            numero_bulto (str, optional): Package number

        Returns:
            list: List of ZPL code strings
        """
        soap_response = self.client.ObtenerEtiquetasZPL(
            ordenRetiro=orden_retiro if orden_retiro else "",
            numeroEnvio=numero_envio if numero_envio else "",
            numeroBulto=numero_bulto if numero_bulto else "",
        )
        return soap_response.ObtenerEtiquetasZPLResult
