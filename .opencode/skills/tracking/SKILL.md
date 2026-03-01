---
name: tracking
description: "Track OCA Argentina shipments using various methods. Use when users need to get the status of packages, track by pickup order, piece ID, DNI/CUIT, or shipment number."
---

# OCA Shipment Tracking

Track shipments and pickup orders using OCA's e-Pak API.

## Track Pickup Order

Track the status of a pickup order (Orden de Retiro):

```python
from ocaepak.client import OcaService

oca = OcaService(user, password, cuit)

orden_retiro = 12345
result = oca.trackingOR(orden_retiro)
```

**Parameters:**
- `orden_retiro` (int): Pickup order number

**Returns:** List of dictionaries with tracking information

## Track by Piece ID

Track a package using its piece ID:

```python
pieza = "123456789"
result = oca.trackingPiezaConID(pieza)
```

**Parameters:**
- `pieza` (str): Piece tracking ID

**Returns:** List of dictionaries with tracking details

## Track by DNI/CUIT

Track all packages associated with a DNI or CUIT number:

```python
nro_documento = "30123456"
cuit = "20-12345678-9"
result = oca.trackingPiezaConDNICUIT(nro_documento, cuit)
```

**Parameters:**
- `nro_documento` (str): DNI or document number
- `cuit` (str): CUIT number

**Returns:** List of dictionaries with tracking information for all matching packages

## Get Current Shipment Status

Get the current status of a shipment with branch position information:

```python
numero_envio = "123456789"
result = oca.trackingEnvioEstadoActual(numero_envio)
```

**Parameters:**
- `numero_envio` (str): Shipment/tracking number

**Returns:** List of dictionaries with current tracking information:
```python
[
    {
        'NumeroEnvio': 123456789,
        'Estado': b'En transito',
        'Sucursal': b'BUENOS AIRES',
        'Fecha': datetime(2024, 1, 15, 10, 30)
    }
]
```

## Get Recent Shipments Status

Retrieve the latest status for shipments within a date range:

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

## List All Shipments

List all shipments within a date range:

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

## When to Use This Skill

Use this skill when:
- Checking the status of a specific package
- Finding all packages for a customer
- Getting branch/office location of a shipment
- Monitoring recent shipment activity
- Auditing shipment history
