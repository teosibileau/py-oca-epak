# Oca e-Pak python wrapper

This is a **FIRST DRAFT** of a python wrapper to the SOAP services ([http://webservice.oca.com.ar/oep_tracking/](http://webservice.oca.com.ar/oep_tracking/)) provided by OCA Argentina to integrate their e-Pak services within your platform.


## Installation

```bash
pip install -e git+https://github.com/drkloc/py-oca-epak.git#egg=ocaepak
```

## Usage

```python
from ocaepak.client import OcaService
# Initialize with your user, password and cuit
(user, password, cuit) = ('your_user', 'your_password', 'your_cuit')
oca = OcaService(user,password, cuit)
```

### AnularOrdenGenerada

Initialize and:

```python
orden = 7849055
oca.anularOrdenGenerada(orden)
```

### GetCentroCostoPorOperativa

Initialize and:

```python
operativa = 72771
oca.centroCostoPorOperativa(operativa)
```

You can check the list of availables 'operatives' with:

```python
print OcaService.OPERATIVAS
```

which outputs a dict containing the following:

+ 72767: 'Punto a Punto STD C/A P. en destino y SEGURO',
+ 72768: 'Punto a Sucursal STD C/ P. en destino y SEGURO',
+ 72769: 'PaP PRIOR C/P. en destino y SEGURO',
+ 72770: 'PaS PRIO C/P. en destino y SEGURO',
+ 72771: 'PaP STD C/P. en destino',
+ 72772: 'PaS STD C/P. en destino',
+ 72951: 'PAP STD C/SEG y PAGO E/Destino',
+ 72952: 'PAS STD C/SEG y Pago E/Destino',
+ 72952: 'PAP STD C/SEG y PAGO EN Destino',
+ 72953: 'PAP PRIO C/SEG y Pago en Destino',
+ 72952: 'PAS Prio c/seg y pago en Destino'

### GetCentrosImposicion

Initialize and:

```python
oca.centrosDeImposicion(orden)
```

### GetCentrosImposicionPorCP

Initialize and:

```python
cp = 8430
oca.centrosDeImposicion(cp)
```

### IngresoOR

Initialize and:

```python

dias_retiro = 4 # delta of days to retired the package
franja_horaria = 1 # 1:8-17 2:8-12 3:14-17
confirmar_retiro = False # Direct confirmation or Manual Confirmation
oca.centrosDeImposicion(
	xml_retiro,
	dias_retiro,
	franja_horaria,
	confirmar_retiro
)
```

xml_retiro should resemble the following:

```xml
<?xml version="1.0"?>
	<ROWS>
		<cabecera ver="1.0" nrocuenta="numero cuenta OCA"/>
		<retiro calle="Calle retiro" nro="numero retiro" piso="piso retiro" depto="departamento retiro" cp="codigo postal retiro" localidad="localidad retiro" provincia="provincia retiro" contacto="contacto retiro" email="e-mail del contacto retiro" solicitante="solicitante retiro" observaciones="observaciones retiro" centrocosto="centro costo retiro"/>
	<envios>
		<envio idoperativa="idoperativa" nroremito="numero remito" >
			<destinatario apellido="Apellido destinatario" nombre="Nombre destinatario" calle="Calle destinatario" nro="Numero destinatario" piso="Piso destinatario" depto="Depto destinatario" cp="codigo postal destinatario" localidad="localidad destinatario" provincia="provincia destinatario" telefono="telefono destinatario" email="email destinatario" idci="IdCentroImposicion" celular="celular destinatario"/>
			<paquetes>
				<paquete alto="10" ancho="11" largo="12" peso="15" valor="200" cant="1" />
				<paquete alto="11" ancho="20" largo="20" peso="30" valor="300" cant="2" />
			</paquetes>
		</envio>
	</envios>
</ROWS>
```

### List_Envios

Initialize and:

```python
from datetime import date, timedelta
to_date = date.today()
from_date = to_date - timedelta(days=4)
oca.estadoUltimosEnvios(from_date, to_date)
```

### Tarifar_Envio_Corporativo

Initialize and:

```python
peso_total = 1 # Kgs
volumen_total = 20 # ccc
cp_origen = 1006
cp_destino = 8430
n_paquetes = 1
operativa = 72771
oca.tarifarEnvioCorporativo(
	peso_total,
	volumen_total,
	cp_origen,
	cp_destino,
	n_paquetes,
	operativa
)
```

### Tracking_OrdenRetiro

### Tracking_Pieza