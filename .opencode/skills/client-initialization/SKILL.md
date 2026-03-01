---
name: client-initialization
description: "Initialize and configure the OcaService client for OCA Argentina's e-Pak SOAP shipping API. Use when users need to set up the client with credentials, understand the required parameters, or configure optional settings."
---

# Oca e-Pak Client Initialization

Initialize the OcaService client to interact with OCA Argentina's e-Pak shipping API.

## Installation

```bash
pip install ocaepak
```

Or install from source:

```bash
pip install -e git+https://github.com/drkloc/py-oca-epak.git#egg=ocaepak
```

## Basic Usage

```python
from ocaepak.client import OcaService

# Initialize with your credentials
user = 'your_user'
password = 'your_password'
cuit = 'your_cuit'

oca = OcaService(user, password, cuit)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user` | str | Yes | API username provided by OCA |
| `password` | str | Yes | API password provided by OCA |
| `cuit` | str | Yes | CUIT number (e.g., '20-12345678-9') |

## Available Constants

The OcaService class provides constants for common values:

### Service Types (OPERATIVAS)

```python
from ocaepak.client import OcaService

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

### Time Windows (FRANJAS_HORARIAS)

```python
print(OcaService.FRANJAS_HORARIAS)
# {1: "8 a 17hs", 2: "8 a 12hs", 3: "14 a 17hs"}
```

## Caching

The client caches geographic data (provincias, localidades) for the duration of the client instance to reduce API calls:

```python
# First call fetches from API
provincias = oca.getProvincias()

# Subsequent calls return cached data
provincias_cached = oca.getProvincias()  # Uses cache
```

## Error Handling

The client may raise exceptions for:
- Invalid credentials
- Network errors
- API errors (invalid parameters, etc.)

```python
from ocaepak.client import OcaService

try:
    oca = OcaService(user, password, cuit)
    result = oca.getProvincias()
except Exception as e:
    print(f"Error: {e}")
```

## When to Use This Skill

Use this skill when:
- Setting up the client for the first time
- Understanding available service types and time windows
- Configuring credentials for OCA e-Pak API access
- Learning about caching behavior
