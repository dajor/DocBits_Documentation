# Outils de workflow

DocFlow MCP fournit 8 outils pour gérer et tester les workflows avancés.

## list\_workflows

Lister tous les workflows de l'organisation actuelle.

**Paramètres :** Aucun

**Exemple de réponse :**

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

Obtenir les détails d'un workflow spécifique, y compris sa structure de nœuds et d'arêtes.

**Paramètres :**

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `workflow_id` | string | Oui | UUID du workflow |

**Exemple de réponse :**

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

Créer un nouveau workflow avancé avec des nœuds et des arêtes.

**Paramètres :**

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `name` | string | Oui | Nom du workflow (3-126 caractères) |
| `description` | string | Non | Description optionnelle |
| `nodes` | array | Oui | Tableau de nœuds de workflow |
| `edges` | array | Oui | Tableau d'arêtes reliant les nœuds |

### Structure des nœuds

Chaque nœud nécessite :

| Champ | Type | Description |
|-------|------|-------------|
| `node_id` | string | Identifiant unique du nœud |
| `node_type` | string | `when`, `then`, `and`, `or` ou `delay` |
| `position` | object | Position `{x: number, y: number}` sur le canevas |
| `label` | string | Libellé d'affichage |
| `card` | object | Configuration de la carte (voir ci-dessous) |

### Structure des arêtes

Chaque arête nécessite :

| Champ | Type | Description |
|-------|------|-------------|
| `edge_id` | string | Identifiant unique de l'arête |
| `source_node_id` | string | ID du nœud source |
| `target_node_id` | string | ID du nœud cible |
| `source_handle` | string | `success` ou `error` (optionnel) |
| `target_handle` | string | `input` (optionnel) |

### Configuration des cartes

Les cartes définissent ce qu'un nœud fait. Utilisez `list_cards` ou `sdk_list_cards_picker` pour obtenir les cartes disponibles.

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
Vous devez uniquement fournir `id`, `card_type`, `version` et `variables` pour chaque carte. Le serveur enrichit automatiquement les cartes avec les métadonnées d'affichage (svg, texte, catégorie) depuis la base de données.
{% endhint %}

**Exemple de requête :**

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

**Exemple de réponse :**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Mettre à jour un workflow avancé existant. Vous pouvez mettre à jour toute combinaison de nom, description, nœuds et arêtes.

**Paramètres :**

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `workflow_id` | string | Oui | UUID du workflow à mettre à jour |
| `name` | string | Non | Nouveau nom |
| `description` | string | Non | Nouvelle description |
| `nodes` | array | Non | Nouveaux nœuds (remplace tous les nœuds existants) |
| `edges` | array | Non | Nouvelles arêtes (remplace toutes les arêtes existantes) |

**Exemple de réponse :**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Supprimer un workflow par ID (suppression logique).

**Paramètres :**

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `workflow_id` | string | Oui | UUID du workflow à supprimer |

**Exemple de réponse :**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Tester l'exécution d'un workflow avancé. Vous pouvez optionnellement fournir un ID de document pour tester avec un document réel.

**Paramètres :**

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `workflow_id` | string | Oui | UUID du workflow avancé |
| `doc_id` | string | Non | UUID d'un document pour le test |

**Exemple de réponse :**

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

Lister tous les scénarios de test de workflow pour l'organisation.

**Paramètres :** Aucun

**Exemple de réponse :**

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

Lister toutes les cartes de workflow disponibles avec leurs conditions et configuration.

**Paramètres :** Aucun

**Exemple de réponse :**

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
Les cartes ont des indicateurs de rôle : `when_condition` (déclencheur), `and_condition` (condition supplémentaire) et `then_condition` (action). Utilisez-les pour déterminer dans quels types de nœuds une carte peut être utilisée.
{% endhint %}
