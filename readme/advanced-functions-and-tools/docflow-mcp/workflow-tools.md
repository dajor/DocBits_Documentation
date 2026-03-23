# Ferramentas de Workflow

O DocFlow MCP fornece 8 ferramentas para gerenciar e testar workflows avançados.

## list\_workflows

Lista todos os workflows da organização atual.

**Parâmetros:** Nenhum

**Exemplo de Resposta:**

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

Obtém detalhes de um workflow específico, incluindo sua estrutura de nós e arestas.

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sim | UUID do workflow |

**Exemplo de Resposta:**

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

Cria um novo workflow avançado com nós e arestas.

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|----------|-------------|
| `name` | string | Sim | Nome do workflow (3-126 caracteres) |
| `description` | string | Não | Descrição opcional |
| `nodes` | array | Sim | Array de nós do workflow |
| `edges` | array | Sim | Array de arestas conectando os nós |

### Estrutura do Nó

Cada nó requer:

| Campo | Tipo | Descrição |
|-------|------|-------------|
| `node_id` | string | Identificador único do nó |
| `node_type` | string | `when`, `then`, `and`, `or` ou `delay` |
| `position` | object | Posição `{x: number, y: number}` no canvas |
| `label` | string | Rótulo de exibição |
| `card` | object | Configuração do card (veja abaixo) |

### Estrutura da Aresta

Cada aresta requer:

| Campo | Tipo | Descrição |
|-------|------|-------------|
| `edge_id` | string | Identificador único da aresta |
| `source_node_id` | string | ID do nó de origem |
| `target_node_id` | string | ID do nó de destino |
| `source_handle` | string | `success` ou `error` (opcional) |
| `target_handle` | string | `input` (opcional) |

### Configuração do Card

Cards definem o que um nó faz. Use `list_cards` ou `sdk_list_cards_picker` para obter os cards disponíveis.

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
Você só precisa fornecer `id`, `card_type`, `version` e `variables` para cada card. O servidor enriquece automaticamente os cards com metadados de exibição (svg, text, category) do banco de dados.
{% endhint %}

**Exemplo de Requisição:**

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

**Exemplo de Resposta:**

```json
{
  "success": true,
  "workflow_id": "new-uuid-here",
  "name": "Simple Invoice Router"
}
```

## update\_advanced\_workflow

Atualiza um workflow avançado existente. Você pode atualizar qualquer combinação de nome, descrição, nós e arestas.

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sim | UUID do workflow a ser atualizado |
| `name` | string | Não | Novo nome |
| `description` | string | Não | Nova descrição |
| `nodes` | array | Não | Novos nós (substitui todos os nós existentes) |
| `edges` | array | Não | Novas arestas (substitui todas as arestas existentes) |

**Exemplo de Resposta:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## delete\_workflow

Exclui um workflow por ID (exclusão lógica).

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sim | UUID do workflow a ser excluído |

**Exemplo de Resposta:**

```json
{
  "success": true,
  "workflow_id": "a1b2c3d4-..."
}
```

## test\_advanced\_workflow

Testa a execução de um workflow avançado. Opcionalmente, forneça um ID de documento para testar com um documento real.

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|----------|-------------|
| `workflow_id` | string | Sim | UUID do workflow avançado |
| `doc_id` | string | Não | UUID de um documento para teste |

**Exemplo de Resposta:**

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

Lista todos os cenários de teste de workflow da organização.

**Parâmetros:** Nenhum

**Exemplo de Resposta:**

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

Lista todos os cards de workflow disponíveis com suas condições e configuração.

**Parâmetros:** Nenhum

**Exemplo de Resposta:**

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
Os cards possuem flags de função: `when_condition` (gatilho), `and_condition` (condição adicional) e `then_condition` (ação). Use-as para determinar em quais tipos de nó um card pode ser utilizado.
{% endhint %}
