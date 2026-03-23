# Strumenti per i Workflow

DocFlow MCP fornisce 8 strumenti per la gestione e il test dei workflow avanzati.

## list\_workflows

Elenca tutti i workflow dell'organizzazione corrente.

**Parametri:** Nessuno

**Esempio di Risposta:**

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

Ottieni i dettagli di un workflow specifico, inclusa la struttura di nodi e archi.

**Parametri:**

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|----------|-------------|
| `workflow_id` | string | Si | UUID del workflow |

**Esempio di Risposta:**

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

Crea un nuovo workflow avanzato con nodi e archi.

**Parametri:**

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|----------|-------------|
| `name` | string | Si | Nome del workflow (3-126 caratteri) |
| `description` | string | No | Descrizione opzionale |
| `nodes` | array | Si | Array di nodi del workflow |
| `edges` | array | Si | Array di archi che collegano i nodi |

### Struttura dei Nodi

Ogni nodo richiede:

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `node_id` | string | Identificatore univoco del nodo |
| `node_type` | string | `when`, `then`, `and`, `or` oppure `delay` |
| `position` | object | Posizione `{x: number, y: number}` sul canvas |
| `label` | string | Etichetta visualizzata |
| `card` | object | Configurazione della card (vedi sotto) |

### Struttura degli Archi

Ogni arco richiede:

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `edge_id` | string | Identificatore univoco dell'arco |
| `source_node_id` | string | ID del nodo sorgente |
| `target_node_id` | string | ID del nodo destinazione |
| `source_handle` | string | `success` o `error` (opzionale) |
| `target_handle` | string | `input` (opzionale) |

### Configurazione delle Card

Le card definiscono cosa fa un nodo. Usa `list_cards` o `sdk_list_cards_picker` per ottenere le card disponibili.

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
Devi fornire solo `id`, `card_type`, `version` e `variables` per ogni card. Il server arricchisce automaticamente le card con metadati di visualizzazione (svg, text, category) dal database.
{% endhint %}

**Esempio di Richiesta:**

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

**Esempio di Risposta:**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Aggiorna un workflow avanzato esistente. Puoi aggiornare qualsiasi combinazione di nome, descrizione, nodi e archi.

**Parametri:**

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|----------|-------------|
| `workflow_id` | string | Si | UUID del workflow da aggiornare |
| `name` | string | No | Nuovo nome |
| `description` | string | No | Nuova descrizione |
| `nodes` | array | No | Nuovi nodi (sostituisce tutti i nodi esistenti) |
| `edges` | array | No | Nuovi archi (sostituisce tutti gli archi esistenti) |

**Esempio di Risposta:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Elimina un workflow tramite ID (eliminazione logica).

**Parametri:**

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|----------|-------------|
| `workflow_id` | string | Si | UUID del workflow da eliminare |

**Esempio di Risposta:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Testa l'esecuzione di un workflow avanzato. Fornisci opzionalmente un ID documento per testare con un documento reale.

**Parametri:**

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|----------|-------------|
| `workflow_id` | string | Si | UUID del workflow avanzato |
| `doc_id` | string | No | UUID di un documento per il test |

**Esempio di Risposta:**

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

Elenca tutti gli scenari di test dei workflow per l'organizzazione.

**Parametri:** Nessuno

**Esempio di Risposta:**

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

Elenca tutte le card disponibili per i workflow con le relative condizioni e configurazione.

**Parametri:** Nessuno

**Esempio di Risposta:**

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
Le card hanno flag di ruolo: `when_condition` (trigger), `and_condition` (condizione aggiuntiva) e `then_condition` (azione). Usa questi flag per determinare in quali tipi di nodo una card puo' essere utilizzata.
{% endhint %}
