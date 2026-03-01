---
name: geographic
description: "Query OCA's geographic data including provinces, localities, pickup centers, and eLockers. Use when users need to find pickup locations, filter by postal code, or get service availability by region."
---

# OCA Geographic Services

Query geographic data from OCA's e-Pak API including provinces, localities, pickup centers, and eLockers.

## Get All Provinces

Retrieve a list of all Argentine provinces with their IDs:

```python
from ocaepak.client import OcaService

oca = OcaService(user, password, cuit)

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

Results are cached for the session.

## Get Localities by Province

Retrieve all localities (cities/towns) for a given province ID:

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

Results are cached per province for the session.

## Get All Pickup Centers

Retrieve a list of all OCA pickup centers (Centros de Imposición):

```python
result = oca.centrosDeImposicion()
```

**Returns:** List of dictionaries with pickup center details

## Get Pickup Centers by Postal Code

Find pickup centers near a specific postal code:

```python
cp = 8430
result = oca.centrosDeImposicionPorCP(cp)
```

**Parameters:**
- `cp` (int): Postal code to search

**Returns:** List of dictionaries with nearby pickup centers

## Get Admission Centers

Retrieve all admission centers for package drop-off:

```python
result = oca.centrosDeImposicionAdmision()
```

**Returns:** List of dictionaries with admission center details

## Get Admission Centers by Postal Code

Find admission centers near a specific postal code:

```python
cp = 1000
result = oca.centrosDeImposicionAdmisionPorCP(cp)
```

**Parameters:**
- `cp` (int): Postal code to search

**Returns:** List of dictionaries with nearby admission centers

## Get Services by Center

Retrieve all pickup centers with their available services:

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

## Get Services by Province

Retrieve pickup centers and their services filtered by province:

```python
# Get all centers in Buenos Aires (province ID 2)
result = oca.getServiciosDeCentrosImposicionPorProvincia(2)

# Get centers in a specific city
result = oca.getServiciosDeCentrosImposicionPorProvincia(2, "LA PLATA")
```

**Parameters:**
- `provincia_id` (int): Province ID to filter by
- `localidad` (str, optional): Locality/city name to filter by. Defaults to empty string (all localities).

**Returns:** List of dictionaries with center information and services

## Get Available eLockers

Retrieve all available OCA eLockers (Smart Lockers):

```python
result = oca.getELockerOCA()
```

**Returns:** List of dictionaries with eLocker information:
```python
[
    {
        'IDLocker': 5199,
        'Sigla': b'62A',
        'Descripcion': b'SmartLocker OCA - ParkingCity',
        'Calle': b'Maipu',
        'Numero': b'119',
        'Piso': None,
        'Localidad': b'ALBERDI',
        'Provincia': b'CORDOBA',
        'CodigoPostal': b'5000'
    },
    # ... more lockers
]
```

## When to Use This Skill

Use this skill when:
- Building address selection forms
- Finding nearby pickup locations
- Filtering services by region
- Setting up delivery options
- Showing eLocker locations to customers
- Validating province and locality inputs
