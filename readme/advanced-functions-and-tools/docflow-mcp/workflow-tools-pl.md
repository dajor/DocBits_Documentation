# Narzedzia przepływow pracy

DocFlow MCP udostepnia 8 narzedzi do zarzadzania i testowania zaawansowanych przepływow pracy.

## list\_workflows

Wyswietla wszystkie przepływy pracy dla biezacej organizacji.

**Parametry:** Brak

**Przykladowa odpowiedz:**

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

Pobiera szczegoly konkretnego przepływu pracy, w tym jego strukture wezlow i krawedzi.

**Parametry:**

| Parametr | Typ | Wymagany | Opis |
|----------|-----|----------|------|
| `workflow_id` | string | Tak | UUID przepływu pracy |

**Przykladowa odpowiedz:**

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

Tworzy nowy zaawansowany przepływ pracy z wezlami i krawedziami.

**Parametry:**

| Parametr | Typ | Wymagany | Opis |
|----------|-----|----------|------|
| `name` | string | Tak | Nazwa przepływu pracy (3-126 znakow) |
| `description` | string | Nie | Opcjonalny opis |
| `nodes` | array | Tak | Tablica wezlow przepływu pracy |
| `edges` | array | Tak | Tablica krawedzi laczacych wezly |

### Struktura wezla

Kazdy wezel wymaga:

| Pole | Typ | Opis |
|------|-----|------|
| `node_id` | string | Unikalny identyfikator wezla |
| `node_type` | string | `when`, `then`, `and`, `or` lub `delay` |
| `position` | object | Pozycja `{x: number, y: number}` na plotnie |
| `label` | string | Etykieta wyswietlana |
| `card` | object | Konfiguracja karty (patrz ponizej) |

### Struktura krawedzi

Kazda krawedz wymaga:

| Pole | Typ | Opis |
|------|-----|------|
| `edge_id` | string | Unikalny identyfikator krawedzi |
| `source_node_id` | string | ID wezla zrodlowego |
| `target_node_id` | string | ID wezla docelowego |
| `source_handle` | string | `success` lub `error` (opcjonalnie) |
| `target_handle` | string | `input` (opcjonalnie) |

### Konfiguracja karty

Karty definiuja, co robi wezel. Uzyj `list_cards` lub `sdk_list_cards_picker`, aby pobrac dostepne karty.

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
Wystarczy podac `id`, `card_type`, `version` i `variables` dla kazdej karty. Serwer automatycznie wzbogaca karty o metadane wyswietlania (svg, text, category) z bazy danych.
{% endhint %}

**Przykladowe zadanie:**

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

**Przykladowa odpowiedz:**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Aktualizuje istniejacy zaawansowany przepływ pracy. Mozna aktualizowac dowolna kombinacje nazwy, opisu, wezlow i krawedzi.

**Parametry:**

| Parametr | Typ | Wymagany | Opis |
|----------|-----|----------|------|
| `workflow_id` | string | Tak | UUID przepływu pracy do aktualizacji |
| `name` | string | Nie | Nowa nazwa |
| `description` | string | Nie | Nowy opis |
| `nodes` | array | Nie | Nowe wezly (zastepuje wszystkie istniejace wezly) |
| `edges` | array | Nie | Nowe krawedzie (zastepuje wszystkie istniejace krawedzie) |

**Przykladowa odpowiedz:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Usuwa przepływ pracy po ID (miekkie usuwanie).

**Parametry:**

| Parametr | Typ | Wymagany | Opis |
|----------|-----|----------|------|
| `workflow_id` | string | Tak | UUID przepływu pracy do usuniecia |

**Przykladowa odpowiedz:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Testuje wykonanie zaawansowanego przepływu pracy. Opcjonalnie mozna podac ID dokumentu, aby przetestowac z prawdziwym dokumentem.

**Parametry:**

| Parametr | Typ | Wymagany | Opis |
|----------|-----|----------|------|
| `workflow_id` | string | Tak | UUID zaawansowanego przepływu pracy |
| `doc_id` | string | Nie | UUID dokumentu do testowania |

**Przykladowa odpowiedz:**

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

Wyswietla wszystkie scenariusze testowe przepływow pracy dla organizacji.

**Parametry:** Brak

**Przykladowa odpowiedz:**

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

Wyswietla wszystkie dostepne karty przepływow pracy z ich warunkami i konfiguracja.

**Parametry:** Brak

**Przykladowa odpowiedz:**

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
Karty posiadaja flagi rol: `when_condition` (wyzwalacz), `and_condition` (dodatkowy warunek) i `then_condition` (akcja). Uzyj ich, aby okreslic, w jakich typach wezlow mozna uzyc danej karty.
{% endhint %}
