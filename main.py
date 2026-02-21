from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, HTTPException
from services.mcp_client import MCPClient
from services.llm_service import LLMService
from services.whatsapp import WhatsAppService
from services.metrics_logger import MetricsLogger
import os
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando servicios...")

    app.state.mcp = MCPClient()
    app.state.llm = LLMService()
    app.state.whatsapp = WhatsAppService()
    app.state.metrics = MetricsLogger()

    print("✅ Todos los servicios iniciados correctamente")

    yield  # La app corre aquí

    # ── SHUTDOWN ─────────────────────────────────────────────
    print("🛑 Apagando servicios...")

    try:
        await app.state.mcp.close()  # Si tu MCPClient tiene método de cierre
        print("✅ MCPClient cerrado")
    except Exception as e:
        print(f"⚠️ Error cerrando MCPClient: {e}")

    print("👋 Servicios apagados correctamente")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
):
    """
    Webhook que recibe los mensajes de WhatsApp desde Twilio.

    Flujo:
    1. Usuario envía mensaje por WhatsApp
    2. Twilio envía webhook a este endpoint (Form data)
    3. Procesamos con MCP + LLM
    4. Enviamos respuesta por WhatsApp
    """
    # Acceder a los servicios desde app.state
    mcp: MCPClient = request.app.state.mcp
    llm: LLMService = request.app.state.llm
    whatsapp: WhatsAppService = request.app.state.whatsapp
    metrics: MetricsLogger = request.app.state.metrics

    # Capturar tiempo inicial y timestamp
    start_time = time.time()
    message_timestamp = datetime.now()

    # Twilio envía el número con formato "whatsapp:+521234567890"
    user_number = From.replace("whatsapp:", "")
    user_message = Body

    print(f"\n📨 Mensaje recibido de {user_number}")
    print(f"💬 Contenido: {user_message}")

    try:
        # Nuevo flujo: dejamos que el modelo decida si usar MCP o no
        # usando OpenAI tools que internamente llaman al servidor MCP.
        print("🤖 Procesando mensaje a través de OpenAI con tools/MCP...")

        # Tiempo antes de procesar con LLM
        llm_start_time = time.time()

        # Procesar con LLM y capturar herramientas usadas
        response, tools_used = await llm.chat_with_mcp(user_message, mcp)

        # Tiempo de procesamiento del LLM
        processing_time = time.time() - llm_start_time

        # Enviar la respuesta por WhatsApp
        print(f"📤 Enviando respuesta a {user_number}")
        whatsapp.send_message(user_number, response)
        print(f"✅ Respuesta enviada correctamente\n")

        # Calcular tiempo total
        total_time = time.time() - start_time

        # Registrar métricas (solo si está habilitado)
        metrics.log_message(
            phone_number=user_number,
            message_in=user_message,
            message_out=response,
            mcp_tools_used=tools_used,
            processing_time=processing_time,
            total_time=total_time,
            timestamp=message_timestamp,
        )

        return {"status": "success"}

    except Exception as e:
        error_msg = f"Lo siento, ocurrió un error al procesar tu solicitud. Por favor intenta de nuevo."
        print(f"❌ Error procesando mensaje: {str(e)}")
        whatsapp.send_message(user_number, error_msg)

        # Registrar error en métricas también (tiempo total hasta el error)
        total_time = time.time() - start_time
        metrics.log_message(
            phone_number=user_number,
            message_in=user_message,
            message_out=f"ERROR: {error_msg}",
            mcp_tools_used=[],
            processing_time=0,
            total_time=total_time,
            timestamp=message_timestamp,
        )

        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health():
    """Endpoint de salud del servicio"""
    return {
        "status": "ok",
        "mcp_url": os.getenv("MCP_SERVER_URL"),
        "twilio_configured": bool(os.getenv("TWILIO_ACCOUNT_SID")),
    }


@app.get("/mcp/tools")
async def list_mcp_tools(request: Request):
    """Lista todas las herramientas disponibles en el MCP"""
    # Acceder a los servicios desde app.state
    mcp: MCPClient = request.app.state.mcp

    try:
        tools = await mcp.list_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    print("🚀 Iniciando servidor en http://0.0.0.0:8000")
    print(f"📡 MCP Server: {os.getenv('MCP_SERVER_URL')}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
