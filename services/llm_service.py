"""Servicio de LLM que se comunica con OpenAI y herramientas MCP.

Este módulo implementa dos modos de uso:

1) generate_response: modo simple, sin tools (se mantiene por compatibilidad).
2) chat_with_mcp: modo recomendado, donde el modelo usa tools de OpenAI que
   internamente llaman al servidor MCP HTTP (FastMCP streamable_http_app).
"""

import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

load_dotenv()


class LLMService:

    system_message_base = """
        Eres el asistente financiero y operativo conversacional exclusivo de Billease, un sistema de gestión empresarial (ERP/POS). Tu objetivo principal es facilitar a los dueños de negocio la consulta, interpretación y análisis de sus datos transaccionales en tiempo real.

        DIRECTRICES DE INTERACCIÓN:
        1) Saludo y Presentación: Si el usuario te saluda, te pide ayuda inicial o pregunta qué puedes hacer, preséntate de manera profesional y resolutiva. Explica brevemente que eres su asistente integrado a Billease, diseñado para extraer y resumir de forma segura los reportes prioritarios de su negocio para agilizar su toma de decisiones.
        2) Formato y Claridad: Transforma cualquier dato técnico (JSON, estructuras de base de datos) en respuestas estructuradas y fáciles de leer. Utiliza Markdown (negritas para métricas clave, viñetas para listas) y emojis de forma estratégica para reducir la carga cognitiva del usuario.
        3) Tono y Personalidad: Mantén un perfil profesional, objetivo, respetuoso y directo. Responde siempre en idioma español.

        RESTRICCIONES Y SEGURIDAD (CUMPLIMIENTO ESTRICTO):
        - Límite de Dominio: Tu conocimiento se restringe a las finanzas, operaciones y datos del sistema Billease (usuarios, facturas, sucursales, reportes). Si el usuario pregunta sobre otros sistemas ERP, temas cotidianos o información ajena al negocio, responde: "Lo siento, soy un asistente financiero especializado en el sistema Billease. Disculpa, pero no puedo ayudarte con consultas fuera de este ámbito operativo."
        - Límite de Responsabilidad: No estás autorizado para emitir recomendaciones de inversión o dictar decisiones empresariales críticas. Si se te solicita una opinión de este tipo, responde: "Mi función es proporcionarle e interpretar los datos precisos de su negocio para que tome decisiones informadas. Para estrategias críticas, le sugiero consultar con un asesor financiero profesional."
    """

    def __init__(self):
        """Servicio de LLM usando OpenAI GPT.

        Usa la API de OpenAI y expone helpers para:
        - generate_response: respuesta directa sin tools.
        - chat_with_mcp: flujo con tools que delega en el servidor MCP.
        """

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurado en .env")

        self.client = OpenAI(api_key=api_key)
        # Modelo por defecto. Puedes cambiar a otro compatible con tools.
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # ------------------------------------------------------------------
    #  MODO SIMPLE (sin tools) - se mantiene para compatibilidad
    # ------------------------------------------------------------------
    def generate_response(self, user_message: str, context: str = "") -> str:
        """Genera respuesta directa usando GPT con contexto opcional.

        Este método NO usa tools; es el flujo "clásico" MCP → contexto → LLM.
        """

        system_prompt = self.system_message_base

        if context:
            user_prompt = (
                f'El usuario pregunta: "{user_message}"\n\n'
                f"Datos de la base de datos:\n{context}\n\n"
                "Por favor, responde la pregunta del usuario usando estos datos de "
                "forma clara y amigable."
            )
        else:
            user_prompt = user_message

        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            print(f"🤖 Llamando a OpenAI (modo simple, modelo={self.model})...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            answer = response.choices[0].message.content
            if answer:
                print(f"✅ Respuesta generada: {answer[:120]}...")

            return answer or "Lo siento, no pude generar una respuesta."

        except Exception as e:
            print(f"❌ Error llamando a OpenAI (modo simple): {str(e)}")
            return (
                "Lo siento, no pude generar una respuesta en este momento. "
                "Por favor intenta de nuevo."
            )

    # ------------------------------------------------------------------
    #  MODO AVANZADO: tools de OpenAI que delegan en MCP
    # ------------------------------------------------------------------
    def _build_system_prompt(self) -> str:
        """Prompt de sistema compartido para el flujo con tools.

        Le explica al modelo que puede usar herramientas (tools) para obtener
        datos reales de Billease a través del servidor MCP.
        """

        return (
            self.system_message_base
            + """
                Puedes utilizar herramientas para consultar datos en tiempo real (ventas, usuarios, reportes, etc.). 
                Cuando sea útil, llama a la herramienta adecuada con los parámetros correctos, espera la respuesta y luego elabora una explicación clara y amable en español para el usuario. Si los datos vienen en JSON, resúmelos de forma entendible (por ejemplo, contando registros, listando nombres importantes, etc.).
                Todas las herramientas que puedes usar están relacionadas con el sistema Billease. Y solo son para consultar datos del sistema Billease, no devuelvas como respuestas datos como el ID de las tablas.
                Si el usuario te pide algo que implique crear/editar/borrar datos de la base de datos, responde con el siguiente mensaje: 'Disculpa, no tengo permisos para realizar ese tipo de acción, por ahora no puedo ayudarte con lo que me pides, pero puedo ayudarte con otro tipo de información.'
            """
        )

    def _build_openai_tools(
        self, mcp_tools: List[Dict[str, Any]]
    ) -> List[ChatCompletionToolParam]:
        """Convierte la descripción de tools MCP en tools de OpenAI.

        Espera que cada tool MCP tenga al menos: name, description y, si es
        posible, inputSchema con la definición de parámetros.
        """

        openai_tools: List[ChatCompletionToolParam] = []

        for tool in mcp_tools:
            name = tool.get("name")
            if not name:
                continue

            description = tool.get("description", "")

            # FastMCP suele exponer "inputSchema" como JSON Schema.
            parameters = tool.get("inputSchema") or {
                "type": "object",
                "properties": {},
                "required": [],
            }

            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": description,
                        "parameters": parameters,
                    },
                }
            )

        return openai_tools

    async def chat_with_mcp(
        self, user_message: str, mcp_client: Any
    ) -> tuple[str, List[str]]:
        """Flujo completo: usuario → OpenAI (tools) → MCP → respuesta.

        - Obtiene la lista de tools MCP.
        - Las registra como tools de OpenAI.
        - Deja que el modelo decida si llama o no a alguna tool.
        - Cuando el modelo pide una tool, se ejecuta realmente contra el MCP
          vía `mcp_client.call_tool` y luego se sigue el loop hasta que el
          modelo devuelva una respuesta final en lenguaje natural.

        Returns:
            tuple[str, List[str]]: (respuesta_final, lista_de_herramientas_usadas)
        """

        # Lista para trackear herramientas MCP usadas
        tools_used: List[str] = []

        # 1) Descubrir tools MCP
        try:
            mcp_tools = await mcp_client.list_tools() or []
            print(f"🧩 Tools MCP disponibles: {[t.get('name') for t in mcp_tools]}")
        except Exception as e:
            print(f"⚠️ No se pudieron listar tools MCP: {e}")
            # Si falla, degradar al modo simple sin tools.
            response = self.generate_response(user_message)
            return (response, tools_used)

        openai_tools: List[ChatCompletionToolParam] = self._build_openai_tools(
            mcp_tools
        )

        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_message},
        ]

        try:
            print(f"🤖 Llamando a OpenAI con tools (modelo={self.model})...")

            # Primera llamada: solo pasamos tools y tool_choice si hay tools.
            if openai_tools:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                    temperature=0.3,
                    max_tokens=800,
                )
            else:
                # Sin tools disponibles, degradamos a un chat normal.
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=800,
                )

            # Loop de tool-calls hasta obtener respuesta final
            while True:
                choice = response.choices[0]
                message = choice.message

                # Si el modelo ya devuelve texto sin tool_calls, terminamos
                if not getattr(message, "tool_calls", None):
                    final_answer = (
                        message.content or "Lo siento, no pude generar una respuesta."
                    )
                    print(f"✅ Respuesta final generada: {final_answer[:120]}...")
                    return (final_answer, tools_used)

                # Registrar el mensaje del asistente que solicita tools
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in message.tool_calls or []
                        ],
                    }
                )

                # Ejecutar cada tool requerida contra el MCP
                for tool_call in message.tool_calls or []:
                    tool_name = tool_call.function.name
                    raw_args = tool_call.function.arguments or "{}"

                    # Agregar herramienta a la lista de herramientas usadas
                    if tool_name not in tools_used:
                        tools_used.append(tool_name)

                    try:
                        args = json.loads(raw_args) if raw_args else {}
                    except json.JSONDecodeError:
                        print(
                            f"⚠️ No se pudieron parsear argumentos de la tool "
                            f"{tool_name}: {raw_args}"
                        )
                        args = {}

                    print(f"🔧 Ejecutando tool MCP '{tool_name}' con args={args}...")

                    try:
                        tool_result = await mcp_client.call_tool(tool_name, args)
                    except Exception as e:
                        tool_result = (
                            f"Error ejecutando herramienta {tool_name}: {e}. "
                            "Informa al usuario de que hubo un problema con "
                            "la herramienta."
                        )

                    # Asegurar contenido en string
                    if not isinstance(tool_result, str):
                        try:
                            tool_result = json.dumps(tool_result, ensure_ascii=False)
                        except Exception:
                            tool_result = str(tool_result)

                    # Añadir mensaje de tool a la conversación
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        }
                    )

                # Volver a llamar al modelo con los resultados de las tools
                print("🔁 Enviando resultados de tools de vuelta al modelo...")

                # Igual que en la primera llamada: solo incluimos tools cuando hay.
                if openai_tools:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto",
                        temperature=0.3,
                        max_tokens=800,
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=800,
                    )

        except Exception as e:
            print(f"❌ Error en flujo con tools/MCP: {e}")
            return (
                "Lo siento, hubo un problema al consultar los datos internos. "
                "Por favor intenta de nuevo más tarde.",
                tools_used,
            )
