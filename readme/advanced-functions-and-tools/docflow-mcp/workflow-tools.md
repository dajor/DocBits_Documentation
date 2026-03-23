# Workflow Tools

DocFlow MCP provides 8 tools for managing and testing advanced workflows.

## list\_workflows

List all workflows for the current organization.

**Parameters:** None

**Example Response:**

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

Get details of a specific workflow including its node and edge structure.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | UUID of the workflow |

**Example Response:**

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

Create a new advanced workflow with nodes and edges.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Workflow name (3-126 characters) |
| `description` | string | No | Optional description |
| `nodes` | array | Yes | Array of workflow nodes |
| `edges` | array | Yes | Array of edges connecting nodes |

### Node Structure

Each node requires:

| Field | Type | Description |
|-------|------|-------------|
| `node_id` | string | Unique identifier for the node |
| `node_type` | string | `when`, `then`, `and`, `or`, or `delay` |
| `position` | object | `{x: number, y: number}` position on canvas |
| `label` | string | Display label |
| `card` | object | Card configuration (see below) |

### Edge Structure

Each edge requires:

| Field | Type | Description |
|-------|------|-------------|
| `edge_id` | string | Unique identifier for the edge |
| `source_node_id` | string | ID of the source node |
| `target_node_id` | string | ID of the target node |
| `source_handle` | string | `success` or `error` (optional) |
| `target_handle` | string | `input` (optional) |

### Card Configuration

Cards define what a node does. Use `list_cards` or `sdk_list_cards_picker` to get available cards.

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
You only need to provide `id`, `card_type`, `version`, and `variables` for each card. The server automatically enriches cards with display metadata (svg, text, category) from the database.
{% endhint %}

**Example Request:**

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

**Example Response:**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Update an existing advanced workflow. You can update any combination of name, description, nodes, and edges.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | UUID of workflow to update |
| `name` | string | No | New name |
| `description` | string | No | New description |
| `nodes` | array | No | New nodes (replaces all existing nodes) |
| `edges` | array | No | New edges (replaces all existing edges) |

**Example Response:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Delete a workflow by ID (soft delete).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | UUID of workflow to delete |

**Example Response:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Test an advanced workflow execution. Optionally provide a document ID to test with a real document.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | UUID of the advanced workflow |
| `doc_id` | string | No | UUID of a document to test with |

**Example Response:**

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

List all workflow test scenarios for the organization.

**Parameters:** None

**Example Response:**

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

List all available workflow cards with their conditions and configuration.

**Parameters:** None

**Example Response:**

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
Cards have role flags: `when_condition` (trigger), `and_condition` (additional condition), and `then_condition` (action). Use these to determine which node types a card can be used in.
{% endhint %}
