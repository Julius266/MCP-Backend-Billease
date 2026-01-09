# 🤖 Backend WhatsApp con MCP + OpenAI

Backend de Python para crear un agente conversacional en WhatsApp que utiliza:
- **WhatsApp Business API (Meta)** para mensajería
- **MCP (Model Context Protocol)** para ejecutar herramientas/consultas a bases de datos
- **OpenAI GPT** para generar respuestas en lenguaje natural

## 📋 Flujo del Sistema

```
Usuario envía: "¿Cuántos usuarios activos tengo?"
      ↓
[WhatsApp] → Webhook Meta
      ↓
[Backend] Recibe mensaje JSON
      ↓
[Backend] Detecta keyword "usuarios"
      ↓
[Backend] → MCP: POST /messages
            { method: "tools/call", params: { name: "read_users_preview" } }
      ↓
[MCP] Ejecuta query PostgreSQL (u otra herramienta)
      ↓
[MCP] → Backend: { result: "[{id:1, nombre:'Juan'}, ...]" }
      ↓
[Backend] → OpenAI: "Usuario pregunta: '¿Cuántos usuarios?' Contexto: [datos]"
      ↓
[OpenAI] → Backend: "Hay 50 usuarios activos en el sistema..."
      ↓
[Backend] → WhatsApp API (Meta)
      ↓
Usuario recibe: "Hay 50 usuarios activos en el sistema..."
```

## 🚀 Configuración

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Edita el archivo `.env`:

```env
# OpenAI API
OPENAI_API_KEY=sk-proj-tu_clave_aqui

# WhatsApp Meta API
WHATSAPP_TOKEN=EAAxxxxxxxxxxxx  # Token de acceso desde Meta Developers
WHATSAPP_PHONE_NUMBER_ID=123456789  # ID del número de teléfono
WHATSAPP_VERIFY_TOKEN=mi_token_secreto_123  # Token que tú elijas

# MCP Server
MCP_SERVER_URL=http://localhost:8080  # URL de tu servidor MCP
```

### 3. Obtener credenciales de WhatsApp (Meta)

1. Ve a [Meta for Developers](https://developers.facebook.com/)
2. Crea una app → Elige "WhatsApp Business"
3. En la sección **WhatsApp** → **Getting Started**:
   - Copia el **Token de acceso temporal** → `WHATSAPP_TOKEN`
   - Copia el **Phone number ID** → `WHATSAPP_PHONE_NUMBER_ID`
4. Para producción, genera un token permanente en **System Users**

### 4. Configurar webhook en Meta

1. En Meta Developers → Tu App → **WhatsApp** → **Configuration**
2. En **Webhook**:
   - **Callback URL**: `https://tu-dominio.com/webhook/whatsapp`
   - **Verify token**: El mismo que pusiste en `WHATSAPP_VERIFY_TOKEN`
   - **Webhook fields**: Marca `messages`
3. Haz clic en **Verify and Save**

### 5. Exponer tu servidor local (desarrollo)

Para desarrollo local, usa **ngrok**:

```bash
ngrok http 8000
```

Copia la URL pública (ej: `https://abc123.ngrok.io`) y úsala como **Callback URL** en Meta.

### 6. Iniciar el servidor

```bash
python main.py
```

El servidor inicia en `http://0.0.0.0:8000`

## 🧪 Probar el sistema

### Verificar salud del servidor

```bash
curl http://localhost:8000/health
```

### Listar herramientas disponibles en MCP

```bash
curl http://localhost:8000/mcp/tools
```

### Enviar mensaje de prueba desde WhatsApp

1. Envía un mensaje al número de WhatsApp configurado
2. Prueba con palabras clave como:
   - "¿Cuántos usuarios tengo?"
   - "Muéstrame la lista de clientes"
   - "Dame información de usuarios"

## 📁 Estructura del Proyecto

```
.
├── main.py                 # FastAPI app principal con webhooks
├── requirements.txt        # Dependencias Python
├── .env                    # Variables de entorno
└── services/
    ├── whatsapp.py        # Cliente de WhatsApp Meta API
    ├── mcp_client.py      # Cliente para conectar con MCP
    ├── llm_service.py     # Cliente de OpenAI GPT
    └── chat_manager.py    # (Vacío - para futuras mejoras)
```

## 🔧 Personalización

### Agregar más palabras clave para MCP

Edita [`main.py`](main.py) en la función `process_user_message`:

```python
keywords_mcp = ["usuarios", "clientes", "datos", "ventas", "reportes"]
```

### Cambiar modelo de OpenAI

Edita [`services/llm_service.py`](services/llm_service.py):

```python
model="gpt-4-turbo"  # o "gpt-3.5-turbo" para más velocidad
```

### Llamar diferentes herramientas del MCP

Edita [`main.py`](main.py):

```python
# Para llamar otra herramienta:
sales_data = mcp.call_tool("get_sales_report", {"period": "monthly"})
```

## 🐛 Troubleshooting

### Error: "No se pudo conectar al servidor MCP"

✅ Verifica que tu servidor MCP esté corriendo en `http://localhost:8080`
✅ Prueba: `curl http://localhost:8080/messages -X POST`

### Error: "403 Verificación fallida" en webhook

✅ Verifica que `WHATSAPP_VERIFY_TOKEN` en `.env` coincida con el token en Meta Developers

### Error: "Authorization failed" al enviar mensajes

✅ Verifica que `WHATSAPP_TOKEN` sea válido (tokens temporales expiran en 24hrs)
✅ Genera un token permanente para producción

### No recibo mensajes

✅ Verifica que tu URL pública (ngrok) esté activa
✅ Verifica que en Meta → Webhooks esté suscrito a `messages`
✅ Revisa logs del servidor con `python main.py`

## 📚 Recursos

- [WhatsApp Business API - Meta](https://developers.facebook.com/docs/whatsapp)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Model Context Protocol (MCP)](https://github.com/anthropics/mcp)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🔐 Seguridad en Producción

- ✅ Usa tokens permanentes de WhatsApp
- ✅ Valida webhooks con `x-hub-signature-256` header
- ✅ Usa HTTPS (no HTTP)
- ✅ Mantén `.env` fuera del control de versiones
- ✅ Limita rate limiting en endpoints públicos

## 📝 Licencia

MIT
