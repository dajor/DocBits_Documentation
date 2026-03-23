# Herramientas de flujos de trabajo

DocFlow MCP proporciona 8 herramientas para gestionar y probar flujos de trabajo avanzados.

## list\_workflows

Listar todos los flujos de trabajo de la organización actual.

**Parámetros:** Ninguno

**Ejemplo de respuesta:**

```json
[
  {
    "id": "a1b2c3d4-...",
    "name": "Invoice Approval",
    "version": 3,
    "enabled": true,
    "doc_types": ["INVOICE"],
    "workflow_type": "advanced",
    "created_on": "2025-01-15 10:30:00",
    "last_modified_on": "2025-03-20 14:22:00"
  }
]
```

## get\_workflow

Obtener detalles de un flujo de trabajo específico, incluyendo su estructura de nodos y aristas.

**Parámetros:**

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sí | UUID del flujo de trabajo |

**Ejemplo de respuesta:**

```json
{
  "id": "a1b2c3d4-...",
  "name": "Invoice Approval",
  "version": 3,
  "enabled": true,
  "doc_types": ["INVOICE"],
  "workflow_type": "advanced",
  "description": "Routes invoices based on amount",
  "advanced_config": {
    "nodes": [
      {"node_id": "when-1", "node_type": "when", "label": "Amount > 1000"},
      {"node_id": "then-1", "node_type": "then", "label": "Send for Approval"}
    ],
    "edges": [
      {"source_node_id": "when-1", "target_node_id": "then-1"}
    ]
  }
}
```

## create\_advanced\_workflow

Crear un nuevo flujo de trabajo avanzado con nodos y aristas.

**Parámetros:**

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|----------|-------------|
| `name` | string | Sí | Nombre del flujo de trabajo (3-126 caracteres) |
| `description` | string | No | Descripción opcional |
| `nodes` | array | Sí | Array de nodos del flujo de trabajo |
| `edges` | array | Sí | Array de aristas que conectan nodos |

### Estructura de nodos

Cada nodo requiere:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `node_id` | string | Identificador único del nodo |
| `node_type` | string | `when`, `then`, `and`, `or` o `delay` |
| `position` | object | Posición `{x: number, y: number}` en el lienzo |
| `label` | string | Etiqueta de visualización |
| `card` | object | Configuración de la tarjeta (ver abajo) |

### Estructura de aristas

Cada arista requiere:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `edge_id` | string | Identificador único de la arista |
| `source_node_id` | string | ID del nodo de origen |
| `target_node_id` | string | ID del nodo de destino |
| `source_handle` | string | `success` o `error` (opcional) |
| `target_handle` | string | `input` (opcional) |

### Configuración de tarjetas

Las tarjetas definen lo que hace un nodo. Usa `list_cards` o `sdk_list_cards_picker` para obtener las tarjetas disponibles.

```json
{
  "id": "card-uuid-here",
  "card_type": "document_type_is",
  "version": 1,
  "variables": [
    {"id": "var-uuid", "data": "INVOICE", "data_type": "string"}
  ]
}
```

{% hint style="info" %}
Solo necesitas proporcionar `id`, `card_type`, `version` y `variables` para cada tarjeta. El servidor enriquece automáticamente las tarjetas con metadatos de visualización (svg, text, category) desde la base de datos.
{% endhint %}

**Ejemplo de solicitud:**

```json
{
  "name": "Simple Invoice Router",
  "description": "Routes invoices to approval",
  "nodes": [
    {
      "node_id": "when-1",
      "node_type": "when",
      "position": {"x": 100, "y": 100},
      "label": "Document is Invoice",
      "card": {
        "id": "card-uuid",
        "card_type": "document_type_is",
        "version": 1,
        "variables": [
          {"id": "var-uuid", "data": "INVOICE", "data_type": "string"}
        ]
      }
    },
    {
      "node_id": "then-1",
      "node_type": "then",
      "position": {"x": 100, "y": 300},
      "label": "Send Notification",
      "card": {
        "id": "card-uuid-2",
        "card_type": "send_email",
        "version": 1,
        "variables": []
      }
    }
  ],
  "edges": [
    {
      "edge_id": "e1",
      "source_node_id": "when-1",
      "target_node_id": "then-1",
      "source_handle": "success",
      "target_handle": "input"
    }
  ]
}
```

**Ejemplo de respuesta:**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Actualizar un flujo de trabajo avanzado existente. Puedes actualizar cualquier combinación de nombre, descripción, nodos y aristas.

**Parámetros:**

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sí | UUID del flujo de trabajo a actualizar |
| `name` | string | No | Nuevo nombre |
| `description` | string | No | Nueva descripción |
| `nodes` | array | No | Nuevos nodos (reemplaza todos los nodos existentes) |
| `edges` | array | No | Nuevas aristas (reemplaza todas las aristas existentes) |

**Ejemplo de respuesta:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Eliminar un flujo de trabajo por ID (eliminación lógica).

**Parámetros:**

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sí | UUID del flujo de trabajo a eliminar |

**Ejemplo de respuesta:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Probar la ejecución de un flujo de trabajo avanzado. Opcionalmente proporciona un ID de documento para probar con un documento real.

**Parámetros:**

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sí | UUID del flujo de trabajo avanzado |
| `doc_id` | string | No | UUID de un documento para probar |

**Ejemplo de respuesta:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-...",
  "execution_time": 0.234,
  "workflow_result": "completed",
  "node_results": {
    "when-1": {"status": "success", "output": true},
    "then-1": {"status": "success"}
  },
  "logs": [
    {
      "node_id": "when-1",
      "node_type": "when",
      "status": "success",
      "error": null,
      "duration_ms": 12
    }
  ]
}
```

## list\_test\_scenarios

Listar todos los escenarios de prueba de flujos de trabajo de la organización.

**Parámetros:** Ninguno

**Ejemplo de respuesta:**

```json
[
  {
    "id": "scenario-uuid",
    "name": "Invoice over 1000 EUR",
    "workflow_id": "a1b2c3d4-...",
    "enabled": true,
    "status": "passed",
    "last_run": "2025-03-20 14:00:00"
  }
]
```

## list\_cards

Listar todas las tarjetas de flujo de trabajo disponibles con sus condiciones y configuración.

**Parámetros:** Ninguno

**Ejemplo de respuesta:**

```json
[
  {
    "id": "card-uuid",
    "text": "Document Type Is",
    "card_type": "document_type_is",
    "card_version": 1,
    "category": "Document",
    "when_condition": true,
    "and_condition": false,
    "then_condition": false
  },
  {
    "id": "card-uuid-2",
    "text": "Send Email Notification",
    "card_type": "send_email",
    "card_version": 1,
    "category": "Communication",
    "when_condition": false,
    "and_condition": false,
    "then_condition": true
  }
]
```

{% hint style="info" %}
Las tarjetas tienen indicadores de rol: `when_condition` (disparador), `and_condition` (condición adicional) y `then_condition` (acción). Utiliza estos indicadores para determinar en qué tipos de nodo se puede usar una tarjeta.
{% endhint %}
