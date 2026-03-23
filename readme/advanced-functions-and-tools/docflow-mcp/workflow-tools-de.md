# Workflow-Tools

DocFlow MCP bietet 8 Tools zur Verwaltung und zum Testen erweiterter Workflows.

## list\_workflows

Alle Workflows der aktuellen Organisation auflisten.

**Parameter:** Keine

**Beispielantwort:**

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

Details eines bestimmten Workflows einschliesslich seiner Knoten- und Kantenstruktur abrufen.

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|------|----------|-------------|
| `workflow_id` | string | Ja | UUID des Workflows |

**Beispielantwort:**

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

Einen neuen erweiterten Workflow mit Knoten und Kanten erstellen.

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|------|----------|-------------|
| `name` | string | Ja | Workflow-Name (3-126 Zeichen) |
| `description` | string | Nein | Optionale Beschreibung |
| `nodes` | array | Ja | Array von Workflow-Knoten |
| `edges` | array | Ja | Array von Kanten, die Knoten verbinden |

### Knotenstruktur

Jeder Knoten erfordert:

| Feld | Typ | Beschreibung |
|-------|------|-------------|
| `node_id` | string | Eindeutiger Bezeichner fuer den Knoten |
| `node_type` | string | `when`, `then`, `and`, `or` oder `delay` |
| `position` | object | `{x: number, y: number}` Position auf der Arbeitsflaeche |
| `label` | string | Anzeigebezeichnung |
| `card` | object | Karten-Konfiguration (siehe unten) |

### Kantenstruktur

Jede Kante erfordert:

| Feld | Typ | Beschreibung |
|-------|------|-------------|
| `edge_id` | string | Eindeutiger Bezeichner fuer die Kante |
| `source_node_id` | string | ID des Quellknotens |
| `target_node_id` | string | ID des Zielknotens |
| `source_handle` | string | `success` oder `error` (optional) |
| `target_handle` | string | `input` (optional) |

### Karten-Konfiguration

Karten definieren, was ein Knoten tut. Verwenden Sie `list_cards` oder `sdk_list_cards_picker`, um verfuegbare Karten abzurufen.

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
Sie muessen nur `id`, `card_type`, `version` und `variables` fuer jede Karte angeben. Der Server ergaenzt Karten automatisch mit Anzeige-Metadaten (svg, text, category) aus der Datenbank.
{% endhint %}

**Beispielanfrage:**

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

**Beispielantwort:**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Einen bestehenden erweiterten Workflow aktualisieren. Sie koennen eine beliebige Kombination aus Name, Beschreibung, Knoten und Kanten aktualisieren.

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|------|----------|-------------|
| `workflow_id` | string | Ja | UUID des zu aktualisierenden Workflows |
| `name` | string | Nein | Neuer Name |
| `description` | string | Nein | Neue Beschreibung |
| `nodes` | array | Nein | Neue Knoten (ersetzt alle bestehenden Knoten) |
| `edges` | array | Nein | Neue Kanten (ersetzt alle bestehenden Kanten) |

**Beispielantwort:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Einen Workflow anhand der ID loeschen (Soft-Delete).

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|------|----------|-------------|
| `workflow_id` | string | Ja | UUID des zu loeschenden Workflows |

**Beispielantwort:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Einen erweiterten Workflow testen. Optional kann eine Dokument-ID angegeben werden, um mit einem echten Dokument zu testen.

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|------|----------|-------------|
| `workflow_id` | string | Ja | UUID des erweiterten Workflows |
| `doc_id` | string | Nein | UUID eines Dokuments zum Testen |

**Beispielantwort:**

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

Alle Workflow-Testszenarien der Organisation auflisten.

**Parameter:** Keine

**Beispielantwort:**

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

Alle verfuegbaren Workflow-Karten mit ihren Bedingungen und Konfigurationen auflisten.

**Parameter:** Keine

**Beispielantwort:**

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
Karten haben Rollen-Flags: `when_condition` (Ausloeser), `and_condition` (zusaetzliche Bedingung) und `then_condition` (Aktion). Verwenden Sie diese, um zu bestimmen, in welchen Knotentypen eine Karte verwendet werden kann.
{% endhint %}
