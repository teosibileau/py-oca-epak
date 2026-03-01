---
name: labels
description: "Generate QR codes and shipping labels for OCA shipments. Use when users need to create printable labels, generate QR codes for pickup orders or shipments, or obtain label data in various formats (HTML, PDF, ZPL)."
---

# OCA Labels and QR Codes

Generate QR codes and shipping labels using OCA's e-Pak API.

## Generate QR by Pickup Order

Generate a base64 encoded QR code string for a specific pickup order:

```python
from ocaepak.client import OcaService

oca = OcaService(user, password, cuit)

id_orden_retiro = "12345"
qr_base64 = oca.generateQrByOrdenDeRetiro(id_orden_retiro)
```

**Parameters:**
- `id_orden_retiro` (str): Pickup order ID

**Returns:** Base64 encoded QR code string

## Generate QR for Package

Generate a QR code for a specific package within a shipment:

```python
numero_envio = "987654321"
id_paquete = "PKG001"
qr_base64 = oca.generateQrParaPaquetes(numero_envio, id_paquete)
```

**Parameters:**
- `numero_envio` (str): Shipment/tracking number
- `id_paquete` (str): Package ID

**Returns:** Base64 encoded QR code string

## Generate QR Codes for Shipment

Generate a list of QR codes for all packages within a shipment:

```python
numero_envio = "555666777"
qr_list = oca.generateListQrPorEnvio(numero_envio)
```

**Parameters:**
- `numero_envio` (str): Shipment/tracking number

**Returns:** List of base64 encoded QR code strings

## Consolidate Pickup Orders

Consolidate multiple pickup orders into a single consolidated order:

```python
ordenes = ["12345", "12346", "12347"]
result = oca.generarConsolidacionDeOrdenesDeRetiro(ordenes)
```

**Parameters:**
- `ordenes` (list): List of pickup order IDs to consolidate

**Returns:** Dictionary with consolidation information:
```python
{
    'IdDeConsolidacion': 'CONS123',
    'CantidadDeOrdenes': 3
}
```

## Get Label CSS Styles

Obtain the CSS styles for label HTML:

```python
css = oca.getCSSDeEtiquetasPorOrdenOrNumeroEnvio(para_etiquetadora=True)
```

**Parameters:**
- `para_etiquetadora` (bool, optional): Whether the CSS is for a label printer. Defaults to False.

**Returns:** CSS styles as a string

## Get Label Data

Obtain structured data for labels:

```python
labels = oca.getDatosDeEtiquetasPorOrdenOrNumeroEnvio(
    id_orden_retiro=12345,
    nro_envio="987654321",
    is_locker=False
)
```

**Parameters:**
- `id_orden_retiro` (int): Pickup order ID (required)
- `nro_envio` (str, optional): Shipment number
- `is_locker` (bool): Whether it's a locker delivery. Defaults to False.

**Returns:** List of dictionaries with label data

## Get Label HTML

Obtain the complete HTML source code for labels:

```python
html = oca.getHtmlDeEtiquetasPorOrdenOrNumeroEnvio(
    id_orden_retiro=12345,
    nro_envio="987654321"
)
```

**Parameters:**
- `id_orden_retiro` (int): Pickup order ID (required)
- `nro_envio` (str, optional): Shipment number

**Returns:** Complete HTML as a string

## Get Label PDF

Obtain a PDF containing labels:

```python
pdf_base64 = oca.getPdfDeEtiquetasPorOrdenOrNumeroEnvio(
    id_orden_retiro=12345,
    nro_envio="987654321",
    logistica_inversa=False
)
```

**Parameters:**
- `id_orden_retiro` (int): Pickup order ID (required)
- `nro_envio` (str, optional): Shipment number
- `logistica_inversa` (bool, optional): Whether it's reverse logistics. Defaults to False.

**Returns:** Base64 encoded PDF as a string

## Get ZPL Label Code

Obtain ZPL (Zebra Programming Language) code for labels:

```python
zpl_codes = oca.obtenerEtiquetasZPL(
    orden_retiro="12345",
    numero_envio="987654321",
    numero_bulto="1"
)
```

**Parameters:**
- `orden_retiro` (str, optional): Pickup order ID
- `numero_envio` (str, optional): Shipment number
- `numero_bulto` (str, optional): Package number (requires numero_envio if provided)

**Returns:** List of ZPL code strings

## When to Use This Skill

Use this skill when:
- Generating QR codes for pickup orders
- Creating printable shipping labels
- Generating label data for custom label designs
- Creating ZPL code for Zebra printers
- Consolidating multiple orders into one pickup
- Generating PDF labels for batch printing
