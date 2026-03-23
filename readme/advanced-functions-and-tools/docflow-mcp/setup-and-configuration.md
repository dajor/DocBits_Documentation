# Setup & Configuration

## API Endpoints

| Environment | MCP Endpoint |
|-------------|-------------|
| Development | `https://dev.api.docbits.com/api/mcp/` |
| Stage | `https://stage.api.docbits.com/api/mcp/` |
| Production | `https://api.docbits.com/api/mcp/` |

## Authentication

All MCP requests require a valid DocBits API key passed as a Bearer token. You can find your API key in **Settings > Integration** in the DocBits UI.

The token is sent via the `Authorization` header:

```
Authorization: Bearer <your-api-key>
```

{% hint style="warning" %}
Admin-only tools (`sdk_approve_card`, `sdk_reject_card`, `sdk_delete_submission`) require an organization admin token.
{% endhint %}

## Client Configuration

### Claude Code

Add the DocFlow MCP server using the CLI:

```bash
claude mcp add docflow-dev \
  --transport http \
  --header "Authorization: Bearer YOUR_API_KEY" \
  -- https://dev.api.docbits.com/api/mcp/
```

Or add it to your `.claude.json` configuration file:

```json
{
  "mcpServers": {
    "docflow-dev": {
      "type": "http",
      "url": "https://dev.api.docbits.com/api/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

You can also add it to a project-level `.mcp.json` file:

```json
{
  "mcpServers": {
    "docflow-dev": {
      "type": "http",
      "url": "https://dev.api.docbits.com/api/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docflow": {
      "type": "streamable-http",
      "url": "https://dev.api.docbits.com/api/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

{% hint style="info" %}
On macOS, the config file is at `~/Library/Application Support/Claude/claude_desktop_config.json`. On Windows: `%APPDATA%\Claude\claude_desktop_config.json`.
{% endhint %}

### OpenAI Codex

Codex CLI supports MCP servers. Add to your project configuration:

```json
{
  "mcpServers": {
    "docflow": {
      "type": "http",
      "url": "https://dev.api.docbits.com/api/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Generic MCP Client (Python)

For custom integrations using the MCP Python SDK:

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def connect():
    async with streamablehttp_client(
        url="https://dev.api.docbits.com/api/mcp/",
        headers={"Authorization": "Bearer YOUR_API_KEY"},
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
```

## Verifying Your Connection

After configuring your client, test the connection by calling the `list_workflows` tool. It requires no parameters and should return an array of workflows (or an empty array for new organizations).

{% hint style="info" %}
If you get authentication errors, verify that your API key is correct and that the `Authorization` header is being sent. Some MCP clients require you to restart after changing configuration.
{% endhint %}
