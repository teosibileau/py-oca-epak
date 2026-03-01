# Oca e-Pak Python wrapper

This is a **Python wrapper** for the SOAP services provided by OCA Argentina to integrate their e-Pak shipping services.

**SOAP Service URL:** [http://webservice.oca.com.ar/oep_tracking/](http://webservice.oca.com.ar/oep_tracking/)

## Installation

```bash
pip install ocaepak
```

Or install from source:

```bash
pip install -e git+https://github.com/drkloc/py-oca-epak.git#egg=ocaepak
```

## Quick Start

```python
from ocaepak.client import OcaService

# Initialize with your credentials
user = 'your_user'
password = 'your_password'
cuit = 'your_cuit'

oca = OcaService(user, password, cuit)
```

## Available Methods

<details>
<summary><strong>AnularOrdenGenerada</strong> - Cancel a pickup order</summary>

Cancel an existing pickup order by its order number.

```python
orden = 7849055
result = oca.anularOrdenGenerada(orden)
```

**Parameters:**
- `orden` (int): The order number to cancel

**Returns:** List of dictionaries with cancellation result
</details>

<details>
<summary><strong>centroCostoPorOperativa</strong> - Get cost center by service type</summary>

Retrieve cost center information for a specific service type (operativa).

```python
operativa = 72771
result = oca.centroCostoPorOperativa(operativa)
```

**Parameters:**
- `operativa` (int): Service type code

**Returns:** List of dictionaries with cost center details

**Available operativas:**

```python
# View all available service types
print(OcaService.OPERATIVAS)
```

Available options:
- `72767`: Punto a Punto STD C/A P. en destino y SEGURO
- `72768`: Punto a Sucursal STD C/ P. en destino y SEGURO
- `72769`: PaP PRIOR C/P. en destino y SEGURO
- `72770`: PaS PRIO C/P. en destino y SEGURO
- `72771`: PaP STD C/P. en destino
- `72772`: PaS STD C/P. en destino
- `72951`: PAP STD C/SEG y PAGO E/Destino
- `72952`: PAS STD C/SEG y Pago E/Destino
- `72954`: PAP STD C/SEG y Pago en Destino
- `72953`: PAP PRIO C/SEG y Pago en Destino
- `72955`: PAS Prio c/seg y pago en Destino
</details>

<details>
<summary><strong>centrosDeImposicion</strong> - Get all pickup centers</summary>

Retrieve a list of all OCA pickup centers (Centros de Imposición).

```python
result = oca.centrosDeImposicion()
```

**Returns:** List of dictionaries with pickup center details
</details>

<details>
<summary><strong>centrosDeImposicionPorCP</strong> - Get pickup centers by postal code</summary>

Find pickup centers near a specific postal code.

```python
cp = 8430
result = oca.centrosDeImposicionPorCP(cp)
```

**Parameters:**
- `cp` (int): Postal code to search

**Returns:** List of dictionaries with nearby pickup centers
</details>

<details>
<summary><strong>centrosDeImposicionAdmision</strong> - Get admission centers</summary>

Retrieve all admission centers for package drop-off.

```python
result = oca.centrosDeImposicionAdmision()
```

**Returns:** List of dictionaries with admission center details
</details>

<details>
<summary><strong>centrosDeImposicionAdmisionPorCP</strong> - Get admission centers by postal code</summary>

Find admission centers near a specific postal code.

```python
cp = 1000
result = oca.centrosDeImposicionAdmisionPorCP(cp)
```

**Parameters:**
- `cp` (int): Postal code to search

**Returns:** List of dictionaries with nearby admission centers
</details>

<details>
<summary><strong>getProvincias</strong> - Get all provinces</summary>

Retrieve a list of all Argentine provinces with their IDs.

```python
result = oca.getProvincias()
```

**Returns:** List of dictionaries with province information:
```python
[
    {'IdProvincia': '1', 'Descripcion': 'BUENOS AIRES'},
    {'IdProvincia': '2', 'Descripcion': 'CAPITAL FEDERAL'},
    # ... more provinces
]
```
</details>

<details>
<summary><strong>getLocalidadesByProvincia</strong> - Get localities by province</summary>

Retrieve all localities (cities/towns) for a given province ID.

```python
id_provincia = 1  # Buenos Aires
result = oca.getLocalidadesByProvincia(id_provincia)
```

**Parameters:**
- `id_provincia` (int): Province ID (from getProvincias)

**Returns:** List of dictionaries with locality names:
```python
[
    {'Nombre': 'CAPITAL FEDERAL'},
    {'Nombre': '12 DE OCTUBRE'},
    # ... more localities
]
```
</details>

<details>
<summary><strong>getServiciosDeCentrosImposicion</strong> - Get services by center</summary>

Retrieve all pickup centers with their available services. This includes detailed center information (address, coordinates, contact) and a list of services offered at each location.

```python
result = oca.getServiciosDeCentrosImposicion()
```

**Returns:** List of dictionaries with center information:
```python
[
    {
        'IdCentroImposicion': '2',
        'Calle': 'BLVD. BUENOS AIRES',
        'Numero': '1459',
        'Localidad': 'LUIS GUILLON',
        'Provincia': 'BUENOS AIRES',
        'Telefono': '4367-5729',
        'Latitud': '-34.8098435',
        'Longitud': '-58.4477191',
        'TipoAgencia': 'Sucursal OCA',
        'Sigla': 'ADG',
        'Sucursal': 'SUCURSAL OCA: LUIS GUILLÓN',
        'Servicios': [
            {'IdTipoServicio': '1', 'ServicioDesc': 'Admisión de paquetes'},
            {'IdTipoServicio': '2', 'ServicioDesc': 'Entrega de paquetes'},
            {'IdTipoServicio': '3', 'ServicioDesc': 'Venta Estampillas'}
        ]
    },
    # ... more centers
]
```
</details>

<details>
<summary><strong>ingresarOR</strong> - Create pickup order</summary>

Create a new pickup order (Orden de Retiro) for package collection.

```python
from datetime import date

# Pickup configuration
dias_retiro = 4  # Days from now to pickup
franja_horaria = 1  # 1: 8-17hs, 2: 8-12hs, 3: 14-17hs
confirmar_retiro = False  # Auto-confirm (True) or manual confirmation (False)

# Create pickup order
result = oca.ingresarOR(
    compra,
    dias_retiro,
    franja_horaria,
    confirmar_retiro
)
```

**Parameters:**
- `compra` (dict): Package and delivery details (see structure below)
- `dias_retiro` (int): Days from now for pickup
- `franja_horaria` (int): Time window (1, 2, or 3)
- `confirmar_retiro` (bool): Auto-confirm the order

**Compra structure:**

```python
compra = {
    'numero_cuenta': '142357/000',
    'retiro': {
        'calle': '11 de Septiembre',
        'numero': 3123,
        'piso': '-',
        'departamento': '-',
        'cp': 1426,
        'localidad': 'Capital Federal',
        'provincia': '-',
        'contacto': 'Martina Pi',
        'solicitante': 'Martina Pi',
        'email': 'martina@pi.com',
        'observaciones': 'Observaciones',
        'centro_de_costo': 0  # 0 for PaP, 1 for PaS
    },
    'envios': [
        {
            'id_operativa': 72771,
            'numero_remito': 36300008254,
            'destinatario': {
                'apellido': 'Sib',
                'nombre': 'Thor',
                'calle': 'Avenida Perito Martino',
                'numero': 131,
                'piso': '-',
                'departamento': '-',
                'cp': 8231,
                'localidad': 'Bariloche',
                'provincia': 'Rio Negro',
                'telefono': '-',
                'email': '-',
                'celular': '-'
            },
            'paquetes': [
                {
                    'alto': 1,
                    'ancho': 1,
                    'largo': 1,
                    'peso': 1,
                    'valor_declarado': 100,
                    'cantidad': 1,
                }
            ]
        },
    ]
}
```

**Time windows (franja_horaria):**
```python
# Available time windows
OcaService.FRANJAS_HORARIAS = {
    1: "8 a 17hs",
    2: "8 a 12hs",
    3: "14 a 17hs"
}
```

**Returns:** SOAP response with order details
</details>

<details>
<summary><strong>estadoUltimosEnvios</strong> - Get recent shipments status</summary>

Retrieve the latest status for shipments within a date range for specific service types.

```python
from datetime import date, timedelta

operativas = ["72771", "72772"]
from_date = date.today() - timedelta(days=7)
to_date = date.today()

result = oca.estadoUltimosEnvios(operativas, from_date, to_date)
```

**Parameters:**
- `operativas` (list): List of service type codes
- `from_date` (datetime): Start date
- `to_date` (datetime): End date

**Returns:** List of dictionaries with shipment status information
</details>

<details>
<summary><strong>listEnvios</strong> - List shipments</summary>

List all shipments within a date range.

```python
from datetime import date, timedelta

to_date = date.today()
from_date = to_date - timedelta(days=4)

result = oca.listEnvios(from_date, to_date)
```

**Parameters:**
- `from_date` (datetime): Start date
- `to_date` (datetime): End date

**Returns:** List of dictionaries with shipment details
</details>

<details>
<summary><strong>tarifarEnvioCorporativo</strong> - Calculate shipping rate</summary>

Calculate the shipping cost for a corporate shipment.

```python
peso_total = 1.0  # kg
volumen_total = 20  # cm³
cp_origen = 1006
cp_destino = 8430
n_paquetes = 1
operativa = 72771

result = oca.tarifarEnvioCorporativo(
    peso_total,
    volumen_total,
    cp_origen,
    cp_destino,
    n_paquetes,
    operativa
)
```

**Parameters:**
- `peso_total` (float): Total weight in kg
- `volumen_total` (int): Total volume in cm³
- `cp_origen` (int): Origin postal code
- `cp_destino` (int): Destination postal code
- `n_paquetes` (int): Number of packages
- `operativa` (int): Service type code

**Returns:** List of dictionaries with pricing information
</details>

<details>
<summary><strong>trackingOR</strong> - Track pickup order</summary>

Track the status of a pickup order by its order number.

```python
orden_retiro = 12345
result = oca.trackingOR(orden_retiro)
```

**Parameters:**
- `orden_retiro` (int): Pickup order number

**Returns:** List of dictionaries with tracking information
</details>

<details>
<summary><strong>trackingPiezaConID</strong> - Track piece by ID</summary>

Track a package using its piece ID.

```python
pieza = "123456789"
result = oca.trackingPiezaConID(pieza)
```

**Parameters:**
- `pieza` (str): Piece tracking ID

**Returns:** List of dictionaries with tracking details
</details>

<details>
<summary><strong>trackingPiezaConDNICUIT</strong> - Track pieces by DNI/CUIT</summary>

Track all packages associated with a DNI or CUIT number.

```python
nro_documento = "30123456"
cuit = "20-12345678-9"
result = oca.trackingPiezaConDNICUIT(nro_documento, cuit)
```

**Parameters:**
- `nro_documento` (str): DNI or document number
- `cuit` (str): CUIT number

**Returns:** List of dictionaries with tracking information for all matching packages
</details>

## Response Parsing

The client includes two static methods for parsing XML responses:

### iterateresult
Parses DataSet XML responses with `<Table>` elements (used by most methods):

```python
from ocaepak.client import OcaService

# Parse a Table-based response
result = OcaService.iterateresult("ResultName", soap_response)
```

### parse_list_result
Parses simple list XML responses (used by getProvincias and getLocalidadesByProvincia):

```python
from ocaepak.client import OcaService

# Parse a list response
xml_string = "<Provincias>...</Provincias>"
result = OcaService.parse_list_result(xml_string, "Provincia")
```

### parse_nested_list_result
Parses XML responses with nested list structures (used by getServiciosDeCentrosImposicion):

```python
from ocaepak.client import OcaService

# Parse a response with nested elements
xml_string = "<CentrosDeImposicion>...</CentrosDeImposicion>"
result = OcaService.parse_nested_list_result(xml_string, "Centro", "Servicio")
```

**Parameters:**
- `xml_string` (str): XML content to parse
- `item_tag` (str): Tag name for individual items (e.g., 'Centro')
- `nested_tag` (str, optional): Tag name for nested lists (e.g., 'Servicio')

**Returns:** List of dictionaries with field names as keys. If `nested_tag` is provided, nested elements are parsed as lists.

## License

MIT License - See LICENSE file for details.
