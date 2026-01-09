# 📱 Guía Rápida: Configuración con Twilio WhatsApp

## 🎯 Ventajas de Twilio (vs Meta API)

✅ **Más simple de configurar** - Sin aprobaciones ni verificaciones complejas  
✅ **Ideal para desarrollo/pruebas** - Sandbox de WhatsApp listo en 5 minutos  
✅ **Webhook simple** - Solo POST con Form data (no JSON complejo)  
✅ **Probado y maduro** - SDK de Python estable

---

## 📋 Paso 1: Crear Cuenta en Twilio

1. Ve a: https://www.twilio.com/try-twilio
2. Regístrate con tu email
3. Verifica tu número de teléfono
4. Recibirás **$15 USD de crédito gratis** para pruebas

---

## 📋 Paso 2: Obtener Credenciales

1. En el dashboard de Twilio: https://console.twilio.com/
2. Encontrarás:
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: Haz clic en "Show" para ver el token

3. Copia estos valores a tu `.env`:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
```

---

## 📋 Paso 3: Activar WhatsApp Sandbox

1. En el menú lateral, busca: **Messaging** → **Try it out** → **Send a WhatsApp message**
2. O ve directo a: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
3. Verás un número de Twilio (ej: `+1 415 523 8886`)
4. **Desde tu WhatsApp personal:**
   - Agrega ese número a tus contactos
   - Envía el código que te muestra (ej: `join shadow-window`)
   - Recibirás: ✅ "Sandbox: You are all set!"

5. Copia el número a tu `.env`:

```env
TWILIO_WHATSAPP_NUMBER=+14155238886
```

---

## 📋 Paso 4: Configurar Webhook

1. En la misma página del Sandbox, baja hasta **Sandbox Configuration**
2. En **"WHEN A MESSAGE COMES IN"**:
   - Ingresa tu URL pública: `https://tu-ngrok.ngrok-free.app/webhook/whatsapp`
   - HTTP Method: **POST**
3. Haz clic en **Save**

### Obtener URL pública con ngrok:

```bash
# Instala ngrok: https://ngrok.com/download
ngrok http 8000
```

Copia la URL que te da (ej: `https://a1b2c3.ngrok-free.app`)

---

## 📋 Paso 5: Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## 📋 Paso 6: Iniciar el Servidor

```bash
python main.py
```

Verás:
```
🚀 Iniciando servidor en http://0.0.0.0:8000
📡 MCP Server: http://localhost:8080
📱 WhatsApp Service inicializado con Twilio
📞 Número: +14155238886
```

---

## ✅ Probar el Sistema

1. **Desde tu WhatsApp**, envía un mensaje al número de Twilio (ej: `+1 415 523 8886`)
2. Prueba con:
   - `Hola` → Respuesta del LLM
   - `¿Cuántos usuarios tengo?` → LLM + MCP + datos

3. **Revisa los logs del servidor** para ver el flujo:
   ```
   📨 Mensaje recibido de +521234567890
   💬 Contenido: ¿Cuántos usuarios tengo?
   🔧 Llamando al MCP para: ¿Cuántos usuarios tengo?
   📊 Datos del MCP recibidos: [{"id":1,"nombre":"Juan"}...]
   🤖 Llamando a OpenAI (gpt-4)...
   ✅ Respuesta generada: Tienes 2 usuarios activos...
   📤 Enviando respuesta a +521234567890
   ✅ Respuesta enviada correctamente
   ```

---

## 🐛 Troubleshooting

### Error: "Unable to create record: Invalid 'To' Phone Number"
✅ Verifica que hayas enviado `join <código>` al número de Twilio desde tu WhatsApp

### Error: "Authenticate" o "Invalid credentials"
✅ Verifica que `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` sean correctos

### No recibo mensajes en el servidor
✅ Verifica que ngrok esté corriendo (`ngrok http 8000`)
✅ Verifica que la URL del webhook en Twilio apunte a tu ngrok URL
✅ Verifica que el método sea POST (no GET)

### Error: "TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN son requeridos"
✅ Verifica que tu archivo `.env` tenga las credenciales
✅ Reinicia el servidor después de editar `.env`

---

## 💰 Costos de Twilio

### Sandbox (Gratis para desarrollo)
- ✅ **Gratis** para probar
- ⚠️ Solo funciona con números que hayan hecho "join"
- ⚠️ Los mensajes incluyen "Sent from your Twilio Sandbox"

### Número de WhatsApp propio (Producción)
- 💵 **$1.50 USD/mes** por el número
- 💵 **$0.005 USD** por mensaje recibido
- 💵 **$0.005-0.01 USD** por mensaje enviado
- 📝 Requiere aprobación de Meta (1-2 días)

**Para producción:**
1. Ve a **Messaging** → **WhatsApp** → **Senders**
2. Haz clic en **Request to add a Twilio number to WhatsApp**
3. Sigue el proceso de verificación

---

## 📚 Recursos

- [Twilio WhatsApp Quickstart](https://www.twilio.com/docs/whatsapp/quickstart/python)
- [Twilio Sandbox Setup](https://www.twilio.com/docs/whatsapp/sandbox)
- [Pricing](https://www.twilio.com/en-us/whatsapp/pricing)

---

## 🎯 Resumen

| Característica | Twilio Sandbox | Meta API |
|---|---|---|
| Tiempo de setup | ⚡ 5 minutos | ⏱️ 1-2 días |
| Aprobación | ✅ No requiere | ⚠️ Sí (Business Verification) |
| Costo desarrollo | 🆓 Gratis | 🆓 Gratis (1000 msg/mes) |
| Formato webhook | 📝 Form data (simple) | 📋 JSON anidado |
| Ideal para | 🧪 Desarrollo/Pruebas | 🚀 Producción |

---

**¡Listo!** Con Twilio puedes empezar a probar tu agente en **menos de 10 minutos** 🚀
