---
name: shipments
description: "Create and manage OCA pickup orders (Ordenes de Retiro). Use when users need to create new shipments, cancel orders, calculate shipping rates, or manage pickup schedules."
---

# OCA Shipment Management

Create and manage pickup orders (Ordenes de Retiro) with OCA's e-Pak API.

## Create Pickup Order

Create a new pickup order (Orden de Retiro) for package collection:

```python
from datetime import date
from ocaepak.client import OcaService

oca = OcaService(user, password, cuit)

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

### Compra Structure

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

### Time Windows (franja_horaria)

```python
OcaService.FRANJAS_HORARIAS = {
    1: "8 a 17hs",
    2: "8 a 12hs",
    3: "14 a 17hs"
}
```

## Cancel Pickup Order

Cancel an existing pickup order:

```python
orden = 7849055
result = oca.anularOrdenGenerada(orden)
```

**Parameters:**
- `orden` (int): The order number to cancel

**Returns:** List of dictionaries with cancellation result

## Get Cost Center by Service Type

Retrieve cost center information for a specific service type:

```python
operativa = 72771
result = oca.centroCostoPorOperativa(operativa)
```

**Parameters:**
- `operativa` (int): Service type code (see OPERATIVAS)

**Returns:** List of dictionaries with cost center details

## Calculate Shipping Rate

Calculate the shipping cost for a corporate shipment:

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

## When to Use This Skill

Use this skill when:
- Creating new pickup orders for shipments
- Cancelling existing orders
- Calculating shipping costs before creating orders
- Setting up recurring pickups
- Managing delivery schedules
