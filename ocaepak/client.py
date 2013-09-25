from pysimplesoap.client import SoapClient
from xml.etree import ElementTree as ET

from datetime import datetime


import os
from jinja2 import Template

ROOT = os.path.dirname(os.path.realpath(__file__))


class OcaService(object):
    WSDL_BASE_URI = 'http://webservice.oca.com.ar/oep_tracking/Oep_Track.asmx'
    OCA_WDSL = '%s?WSDL' % WSDL_BASE_URI
    LABELS_FOR_INTEGERS = [
        'Numero',
        'Piso',
        'idCentroImposicion',
        'idTipoSercicio',
        'PlazoEntrega',
        'Tarifador'
    ]
    LABELS_FOR_FLOATS = [
        'Precio',
        'Adicional',
        'Total'
    ]
    LABELS_FOR_DATETIMES = [
        'fecha'
    ]

    OPERATIVAS = {
        72767: 'Punto a Punto Estandar con Seguro / Pago en Destino',
        72768: 'Punto a Sucursal Estandar con Seguro / Pago en Destino',
        72769: 'Punto a Punto Prioritario con Seguro / Pago en Destino',
        72770: 'Punto a Sucursal Prioritario con Seguro / Pago en Destino',
        72771: 'Punto a Punto Estandar / Pago en Destino',
        72772: 'Punto a Sucursal Estandar / Pago en Destino',
        72951: 'Punto a Punto Estandar con Seguro / Pago en Destino',
        72952: 'Punto a Sucursal Estandar con Seguro / Pago en Destino',
        72952: 'Punto a Punto Estandar con Seguro / Pago en Destino',
        72953: 'Punto a Punto Prioritario con Seguro / Pago en Destino',
        72952: 'Punto a Sucursal Prioritario con Seguro / Pago en Destino'
    }

    FRANJAS_HORARIAS = {
        1: '8 a 17hs',
        2: '8 a 12hs',
        3: '14 a 17hs',
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
                        elif field.tag in OcaService.LABELS_FOR_FLOATS:
                            value = float(value)
                        elif field.tag in OcaService.LABELS_FOR_DATETIMES:
                            value = datetime.strptime(
                                value,
                                '%Y-%m-%dT%H:%M:%S-03:00'
                            )
                        else:
                            value = value.encode('utf-8')
                        t[field.tag] = value
            r.append(t)
        return r

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

    def ingresarOR(self, compra, dias_retiro, franja_horaria,
                   confirmar_retiro=False):
        t_file = open(os.path.join(ROOT, 'templates', 'retiro.xml'))
        template = [l for l in t_file.readlines()]
        template = Template(''.join(template))
        template_render = template.render(compra).replace('\t', '').replace('\n', '')
        print template_render
        r = self.client.IngresoOR(
            usr=self.user,
            psw=self.password,
            XML_Retiro=template_render,
            ConfirmarRetiro='true' if confirmar_retiro else 'false',
            DiasRetiro=dias_retiro,
            FranjaHoraria=franja_horaria
        )
        return r

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
