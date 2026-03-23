# Workflow Tools

DocFlow MCP biedt 8 tools voor het beheren en testen van geavanceerde workflows.

## list\_workflows

Alle workflows van de huidige organisatie weergeven.

**Parameters:** Geen

**Voorbeeldrespons:**

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

Details van een specifieke workflow ophalen, inclusief de node- en edge-structuur.

**Parameters:**

| Parameter | Type | Vereist | Beschrijving |
|-----------|------|---------|-------------|
| `workflow_id` | string | Ja | UUID van de workflow |

**Voorbeeldrespons:**

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

Een nieuwe geavanceerde workflow aanmaken met nodes en edges.

**Parameters:**

| Parameter | Type | Vereist | Beschrijving |
|-----------|------|---------|-------------|
| `name` | string | Ja | Workflownaam (3-126 tekens) |
| `description` | string | Nee | Optionele beschrijving |
| `nodes` | array | Ja | Array van workflownodes |
| `edges` | array | Ja | Array van edges die nodes verbinden |

### Node-structuur

Elke node vereist:

| Veld | Type | Beschrijving |
|------|------|-------------|
| `node_id` | string | Unieke identificatie voor de node |
| `node_type` | string | `when`, `then`, `and`, `or` of `delay` |
| `position` | object | `{x: number, y: number}` positie op het canvas |
| `label` | string | Weergavelabel |
| `card` | object | Kaartconfiguratie (zie hieronder) |

### Edge-structuur

Elke edge vereist:

| Veld | Type | Beschrijving |
|------|------|-------------|
| `edge_id` | string | Unieke identificatie voor de edge |
| `source_node_id` | string | ID van de bronnode |
| `target_node_id` | string | ID van de doelnode |
| `source_handle` | string | `success` of `error` (optioneel) |
| `target_handle` | string | `input` (optioneel) |

### Kaartconfiguratie

Kaarten definiëren wat een node doet. Gebruik `list_cards` of `sdk_list_cards_picker` om beschikbare kaarten op te halen.

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
U hoeft alleen `id`, `card_type`, `version` en `variables` op te geven voor elke kaart. De server verrijkt kaarten automatisch met weergavemetadata (svg, tekst, categorie) uit de database.
{% endhint %}

**Voorbeeldverzoek:**

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

**Voorbeeldrespons:**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Een bestaande geavanceerde workflow bijwerken. U kunt elke combinatie van naam, beschrijving, nodes en edges bijwerken.

**Parameters:**

| Parameter | Type | Vereist | Beschrijving |
|-----------|------|---------|-------------|
| `workflow_id` | string | Ja | UUID van de bij te werken workflow |
| `name` | string | Nee | Nieuwe naam |
| `description` | string | Nee | Nieuwe beschrijving |
| `nodes` | array | Nee | Nieuwe nodes (vervangt alle bestaande nodes) |
| `edges` | array | Nee | Nieuwe edges (vervangt alle bestaande edges) |

**Voorbeeldrespons:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Een workflow verwijderen op basis van ID (zachte verwijdering).

**Parameters:**

| Parameter | Type | Vereist | Beschrijving |
|-----------|------|---------|-------------|
| `workflow_id` | string | Ja | UUID van de te verwijderen workflow |

**Voorbeeldrespons:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Een geavanceerde workflow-uitvoering testen. Optioneel kunt u een document-ID opgeven om met een echt document te testen.

**Parameters:**

| Parameter | Type | Vereist | Beschrijving |
|-----------|------|---------|-------------|
| `workflow_id` | string | Ja | UUID van de geavanceerde workflow |
| `doc_id` | string | Nee | UUID van een document om mee te testen |

**Voorbeeldrespons:**

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

Alle testscenario's voor workflows van de organisatie weergeven.

**Parameters:** Geen

**Voorbeeldrespons:**

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

Alle beschikbare workflowkaarten weergeven met hun condities en configuratie.

**Parameters:** Geen

**Voorbeeldrespons:**

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
Kaarten hebben rolvlaggen: `when_condition` (trigger), `and_condition` (aanvullende voorwaarde) en `then_condition` (actie). Gebruik deze om te bepalen in welke nodetypes een kaart kan worden gebruikt.
{% endhint %}
