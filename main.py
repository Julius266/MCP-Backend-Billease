from fastapi import FastAPI, Request, Form, HTTPException
from services.mcp_client import MCPClient
from services.llm_service import LLMService
from services.whatsapp import WhatsAppService
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

mcp = MCPClient()
llm = LLMService()
whatsapp = WhatsAppService()


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
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
    # Twilio envía el número con formato "whatsapp:+521234567890"
    user_number = From.replace("whatsapp:", "")
    user_message = Body
    
    print(f"\n📨 Mensaje recibido de {user_number}")
    print(f"💬 Contenido: {user_message}")
    
    try:
        # Nuevo flujo: dejamos que el modelo decida si usar MCP o no
        # usando OpenAI tools que internamente llaman al servidor MCP.
        print("🤖 Procesando mensaje a través de OpenAI con tools/MCP...")
        response = await llm.chat_with_mcp(user_message, mcp)
        
        # Enviar la respuesta por WhatsApp
        print(f"📤 Enviando respuesta a {user_number}")
        whatsapp.send_message(user_number, response)
        print(f"✅ Respuesta enviada correctamente\n")
        
        return {"status": "success"}
    
    except Exception as e:
        error_msg = f"Lo siento, ocurrió un error al procesar tu solicitud. Por favor intenta de nuevo."
        print(f"❌ Error procesando mensaje: {str(e)}")
        whatsapp.send_message(user_number, error_msg)
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health():
    """Endpoint de salud del servicio"""
    return {
        "status": "ok",
        "mcp_url": os.getenv("MCP_SERVER_URL"),
        "twilio_configured": bool(os.getenv("TWILIO_ACCOUNT_SID"))
    }


@app.get("/mcp/tools")
async def list_mcp_tools():
    """Lista todas las herramientas disponibles en el MCP"""
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