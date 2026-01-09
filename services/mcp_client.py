"""Cliente MCP basado en el SDK oficial `mcp` (python-sdk).

Usa `ClientSessionGroup` y el transporte `streamablehttp_client` para
conectarse a tu servidor FastMCP (`streamable_http_app`) vía HTTP.

Esto delega toda la lógica de sesiones, `sessionId`, rutas internas, etc.
al SDK oficial, que es exactamente el mismo stack que usa VS Code/Copilot.
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp.client.session_group import ClientSessionGroup, StreamableHttpParameters

load_dotenv()


class MCPClient:
    def __init__(self, url: str | None = None) -> None:
        """Inicializa el cliente MCP.

        Args:
            url: URL base del servidor MCP HTTP, por ejemplo
                 "http://localhost:8080/mcp/" (la misma que usas en mcp.json).
        """

        # Debe ser la misma URL que en .vscode/mcp.json (sin /messages).
        self.url = url or os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp/")
        print(f"🔌 MCP Client (python-sdk) conectando a: {self.url}")

        self._group: ClientSessionGroup | None = None
        self._connected: bool = False

    async def _ensure_connected(self) -> None:
        """Establece la conexión con el servidor MCP si aún no existe."""

        if self._connected and self._group is not None:
            return

        self._group = ClientSessionGroup()
        await self._group.__aenter__()

        params = StreamableHttpParameters(url=self.url)
        await self._group.connect_to_server(params)

        self._connected = True

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Lista las herramientas disponibles en el servidor MCP.

        Devuelve una lista de dicts sencillos con al menos ``name`` y
        ``description`` para que el LLM pueda registrarlos como tools.
        """

        try:
            await self._ensure_connected()
            assert self._group is not None

            tools_dict = self._group.tools  # nombre -> types.Tool
            result: List[Dict[str, Any]] = []

            for name, tool in tools_dict.items():
                if hasattr(tool, "model_dump"):
                    data = tool.model_dump()
                    # Aseguramos que tenga al menos un "name" consistente.
                    data.setdefault("name", name)
                    result.append(data)
                else:
                    result.append({"name": name})

            return result

        except Exception as e:
            print(f"Error listando herramientas MCP (python-sdk): {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] | None = None) -> Any:
        """Llama a una herramienta MCP por nombre usando el SDK oficial.

        Args:
            tool_name: Nombre lógico de la herramienta (por ejemplo,
                       "read_users_preview" o "get_report_sales").
            arguments: Diccionario de argumentos para la herramienta.
        """

        arguments = arguments or {}

        try:
            await self._ensure_connected()
            assert self._group is not None

            result = await self._group.call_tool(tool_name, arguments)

            # `result.content` suele ser una lista de objetos con `text`.
            content = getattr(result, "content", None)
            if content and len(content) > 0:
                first = content[0]
                text = getattr(first, "text", None)
                if text is not None:
                    return text

            # Fallback: devolver el propio resultado serializado
            try:
                if hasattr(result, "model_dump_json"):
                    return result.model_dump_json()
                if hasattr(result, "model_dump"):
                    return result.model_dump()
            except Exception:
                pass

            return str(result)

        except Exception as e:
            raise Exception(f"Error llamando a herramienta MCP '{tool_name}': {e}")