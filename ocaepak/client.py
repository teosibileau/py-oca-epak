from pysimplesoap.client import SoapClient
from xml.etree import ElementTree as ET
from datetime import datetime


class OcaService(object):
    WSDL_BASE_URI = 'http://webservice.oca.com.ar/oep_tracking/Oep_Track.asmx'
    OCA_WDSL = '%s?WSDL' % WSDL_BASE_URI
    LABELS_FOR_INTEGERS = [
        'Numero',
        'Piso',
        'idCentroImposicion'
    ]
    LABELS_FOR_DATETIMES = [
        'fecha'
    ]

    OPERATIVAS = {
        72767: 'Punto a Punto STD C/A P. en destino y SEGURO',
        72768: 'Punto a Sucursal STD C/ P. en destino y SEGURO',
        72769: 'PaP PRIOR C/P. en destino y SEGURO',
        72770: 'PaS PRIO C/P. en destino y SEGURO',
        72771: 'PaP STD C/P. en destino',
        72772: 'PaS STD C/P. en destino',
        72951: 'PAP STD C/SEG y PAGO E/Destino',
        72952: 'PAS STD C/SEG y Pago E/Destino',
        72952: 'PAP STD C/SEG y PAGO EN Destino',
        72953: 'PAP PRIO C/SEG y Pago en Destino',
        72952: 'PAS Prio c/seg y pago en Destino'
    }

    @classmethod
    def iterateresult(cls, id_result, xml_result):
        tree = ET.fromstring(
            str(
                xml_result[id_result].as_xml()
            )
        )
        r = []
        for node in tree.getiterator('Table'):
            t = {}
            for field in node.getiterator():
                if field.tag != 'Table' and field.text:
                    value = field.text.strip()
                    if value:
                        if field.tag in OcaService.LABELS_FOR_INTEGERS:
                            value = int(value)
                        if field.tag in OcaService.LABELS_FOR_DATETIMES:
                            value = datetime.strptime(
                                value,
                                '%Y-%m-%dT%H:%M:%S-03:00'
                            )
                        t[field.tag] = value
            r.append(t)
        return r

    def __init__(self, user, password, cuit):
        self.user = user
        self.password = password
        self.CUIT = cuit
        self.client = SoapClient(
            wsdl=OcaService.OCA_WDSL,
            location=OcaService.WSDL_BASE_URI
        )

    def anularOrdenGenerada(self, orden):
        return OcaService.iterateresult(
            'AnularOrdenGeneradaResult',
            self.client.AnularOrdenGenerada(
                usuario=self.user,
                password=self.password,
                nroOrden=orden
            )
        )

    def centroCostoPorOperativa(self, operativa):
        return OcaService.iterateresult(
            'GetCentroCostorPorOperativaResult',
            self.client.GetCentroCostorPorOperativa(
                CUIT=self.CUIT,
                Operativa=operativa
            )
        )

    def centrosDeImposicion(self):
        return OcaService.iterateresult(
            'GetCentrosImposicionResult',
            self.client.GetCentrosImposicion()
        )

    def centrosDeImposicionPorCP(self, cp):
        return OcaService.iterateresult(
            'GetCentrosImposicionPorCPResult',
            self.client.GetCentrosImposicionPorCP(
                CodigoPostal=cp
            )
        )

    def ingresarOR(self, xml_retiro, dias_retiro, franja_horaria,
                   confirmar_retiro=False):
        return OcaService.iterateresult(
            'IngresoORResult',
            self.client.IngresoOR(
                Usr=self.user,
                Psw=self.password,
                XML_Retiro=xml_retiro,
                ConfirmarRetiro=confirmar_retiro,
                DiasRetiro=dias_retiro,
                FranjaHoraria=franja_horaria
            )
        )

    def estadoUltimosEnvios(self, operativas, from_date, to_date):
        return OcaService.iterateresult(
            'GetEnviosUltimoEstadoResult',
            self.client.GetEnviosUltimoEstado(
                cuit=self.CUIT,
                operativas=operativas,
                fechaDesta=from_date.strftime('%d/%m/%Y'),
                fechaHasta=to_date.strftime('%d/%m/%Y')
            )
        )

    def listEnvios(self, from_date, to_date):
        return OcaService.iterateresult(
            'List_EnviosResult',
            self.client.List_Envios(
                CUIT=self.CUIT,
                FechaDesde=from_date.strftime('%d/%m/%Y'),
                FechaHasta=to_date.strftime('%d/%m/%Y')
            )
        )

    def tarifarEnvioCorporativo(self, peso_total, volumen_total, cp_origen,
                                cp_destino, n_paquetes, operativa):
        return OcaService.iterateresult(
            'Tarifar_Envio_CorporativoResult',
            self.client.Tarifar_Envio_Corporativo(
                PesoTotal=peso_total,
                VolumenTotal=volumen_total,
                CodigoPostalOrigen=cp_origen,
                CodigoPostalDestino=cp_destino,
                CantidadPaquetes=n_paquetes,
                Cuit=self.CUIT,
                Operativa=operativa
            )
        )

    def trackingOR(self, orden_retiro):
        return OcaService.iterateresult(
            'Tracking_OrdenRetiroResult',
            self.client.Tracking_OrdenRetiro(
                CUIT=self.CUIT,
                OrdenRetiro=orden_retiro
            )
        )

    def trackingPiezaConID(self, pieza):
        return OcaService.iterateresult(
            'Tracking_PiezaResult',
            self.client.Tracking_Pieza(
                Pieza=pieza
            )
        )

    def trackingPiezaConDNICUIT(self, nro_documento, cuit):
        return OcaService.iterateresult(
            'Tracking_PiezaResult',
            self.client.Tracking_Pieza(
                NroDocumentoCliente=nro_documento,
                CUIT=cuit
            )
        )
