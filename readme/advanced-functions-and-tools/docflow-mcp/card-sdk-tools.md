# Card SDK Tools

The Card SDK tools let you create, validate, test, and manage custom partner cards through MCP. Partner cards extend DocFlow with custom business logic written in Python.

## Card Lifecycle

```
Create → Validate → Test → Approve → Use in Workflows
```

1. **Create** a card with `sdk_create_card` or `sdk_import_github`
2. **Validate** with `sdk_validate_card` (5-stage validation)
3. **Test** with `sdk_test_card` (sandboxed execution)
4. **Approve** with `sdk_approve_card` (admin required)
5. The card is now available in `list_cards` and can be used in workflows

## Development Tools

### sdk\_create\_card

Create a new partner card from source code and manifests. Runs full 5-stage validation and stores the card in the database. The card starts in a pending state and requires admin approval to activate.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `app_manifest` | object | Yes | App manifest with id, name, version, partner info |
| `card_manifest` | object | Yes | Card manifest with id, title, entry\_point, class\_name, args |
| `card_type` | string | Yes | `action` or `condition` |
| `source_code` | string | Yes | Python source code (must extend `PartnerCard`) |
| `test_code` | string | Yes | Pytest test code for the card |
| `locales` | object | No | Locale translations, e.g. `{"en": {...}, "de": {...}}` |

**App Manifest Example:**

```json
{
  "id": "com.acme.invoice-tools",
  "name": "Invoice Tools",
  "version": "1.0.0",
  "partner": {
    "id": "acme",
    "name": "Acme Corp"
  }
}
```

**Card Manifest Example:**

```json
{
  "id": "amount-threshold",
  "title": {"en": "Amount Threshold Check"},
  "entry_point": "src/amount_threshold.py",
  "class_name": "AmountThreshold",
  "args": [
    {
      "id": "threshold",
      "title": {"en": "Threshold Amount"},
      "type": "number",
      "required": true
    }
  ]
}
```

**Source Code Example:**

```python
from api.sdk.base import PartnerCard
from api.sdk.result import CardResult, CardStatus

class AmountThreshold(PartnerCard):
    def execute(self, context):
        threshold = float(self.variables.get("threshold", 0))
        total = context.document_fields.get("total_amount", 0)
        if float(total) > threshold:
            return CardResult(
                status=CardStatus.SUCCESS,
                message=f"Amount {total} exceeds threshold {threshold}"
            )
        return CardResult(
            status=CardStatus.FAILURE,
            message=f"Amount {total} below threshold {threshold}"
        )
```

**Example Response:**

```json
{
  "success": true,
  "cards": ["amount-threshold"],
  "validation_report": {
    "status": "validated",
    "stages": {
      "structure": {"passed": true},
      "ast_analysis": {"passed": true},
      "dependencies": {"passed": true},
      "tests": {"passed": true},
      "behavioral": {"passed": true}
    }
  }
}
```

### sdk\_validate\_card

Run 5-stage validation on a partner card without saving. Two modes:

- **Mode A** — Validate an existing card by ID
- **Mode B** — Validate new source code inline

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_id` | string | No | UUID of existing card (Mode A) |
| `app_manifest` | object | No | App manifest (Mode B) |
| `card_manifest` | object | No | Card manifest (Mode B) |
| `card_type` | string | No | `action` or `condition` (Mode B) |
| `source_code` | string | No | Python source code (Mode B) |
| `test_code` | string | No | Test code (Mode B) |

{% hint style="info" %}
Provide either `card_id` alone (Mode A) or `app_manifest` + `card_manifest` + `source_code` together (Mode B).
{% endhint %}

**Validation Stages:**

1. **Structure** — Verifies file layout, manifest schema, required files
2. **AST Analysis** — Checks Python syntax, class hierarchy, method signatures
3. **Dependencies** — Validates imports against allowed modules
4. **Tests** — Runs the card's test suite
5. **Behavioral** — Executes the card in sandbox to check runtime behavior

### sdk\_test\_card

Execute a partner card in a sandboxed environment with a mock context. Uses the same security model as production (restricted builtins, import whitelist, 10-second timeout).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_id` | string | No | UUID of existing card (Mode A) |
| `source_code` | string | No | Source code for inline testing (Mode B) |
| `class_name` | string | No | Class name for inline testing (Mode B) |
| `variables` | object | No | Variables to pass to the card constructor |
| `mock_context` | object | No | Mock execution context |

**Mock Context Fields:**

```json
{
  "document_id": "doc-uuid",
  "document_type": "INVOICE",
  "document_fields": {
    "total_amount": "1500.00",
    "currency": "EUR",
    "vendor_name": "Acme Corp"
  },
  "metadata": {
    "custom_key": "custom_value"
  }
}
```

**Example Response:**

```json
{
  "success": true,
  "status": "CardStatus.SUCCESS",
  "message": "Amount 1500.00 exceeds threshold 1000",
  "data": {},
  "logs": ["Checking threshold...", "Amount exceeds threshold"]
}
```

### sdk\_import\_github

Import a partner app from a GitHub repository. Clones the repo, reads `app.json`, and imports all cards found in the `.docflowcompose` directory.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `github_url` | string | Yes | GitHub HTTPS URL (e.g. `https://github.com/org/repo`) |
| `branch` | string | No | Branch to clone (default: `main`) |
| `token` | string | No | GitHub token for private repos |

**Expected Repository Structure:**

```
repo/
  app.json
  .docflowcompose/
    flow/
      actions/
        my-action.json
      conditions/
        my-condition.json
  src/
    my_action.py
    my_condition.py
  tests/
    test_card.py
```

**Example Response:**

```json
{
  "success": true,
  "message": "Imported 2 cards from GitHub. Status: validated",
  "app_id": "com.acme.invoice-tools",
  "cards_created": ["my-action", "my-condition"],
  "validation_report": {"status": "validated"}
}
```

## Management Tools

### sdk\_list\_submissions

List all partner card submissions for the current organization.

**Parameters:** None

**Example Response:**

```json
[
  {
    "card_id": "card-uuid",
    "card_name": "Amount Threshold Check",
    "partner_app_id": "com.acme.invoice-tools",
    "partner_status": "validated",
    "version": "1.0.0",
    "card_type": "condition",
    "enabled": false,
    "submitted_at": "2025-03-20T10:00:00"
  }
]
```

### sdk\_get\_submission\_status

Get the validation status and report for a specific partner card submission.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_id` | string | Yes | UUID of the partner card |

**Example Response:**

```json
{
  "card_id": "card-uuid",
  "status": "validated",
  "validation_report": {
    "status": "validated",
    "stages": {
      "structure": {"passed": true},
      "ast_analysis": {"passed": true},
      "dependencies": {"passed": true},
      "tests": {"passed": true},
      "behavioral": {"passed": true}
    }
  }
}
```

### sdk\_approve\_card

Approve a validated partner card and activate it for use in workflows. The card is registered in the runtime registry and becomes available in `list_cards`.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_id` | string | Yes | UUID of the partner card |

{% hint style="warning" %}
Requires organization admin permissions. The card must be in `validated` or `rejected` state.
{% endhint %}

### sdk\_reject\_card

Reject a partner card submission and deactivate it.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_id` | string | Yes | UUID of the partner card |
| `reason` | string | No | Reason for rejection |

{% hint style="warning" %}
Requires organization admin permissions.
{% endhint %}

### sdk\_delete\_submission

Deactivate or delete a partner card submission. Rejected or disabled cards are physically deleted from the database. Active cards are deactivated first.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `card_id` | string | Yes | UUID of the partner card |

{% hint style="warning" %}
Requires organization admin permissions.
{% endhint %}

### sdk\_list\_cards\_picker

List all enabled, non-deprecated cards with role flags. Useful for determining which cards can be used in which node types when building workflows.

**Parameters:** None

**Example Response:**

```json
[
  {
    "card_id": "card-uuid",
    "card_name": "Document Type Is",
    "category": "Document",
    "card_type": "document_type_is",
    "is_when": true,
    "is_and": false,
    "is_then": false,
    "is_partner_card": false
  }
]
```
