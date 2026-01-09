# 📱 Guía de Configuración: WhatsApp Business API (Meta)

## 🎯 Objetivo
Configurar tu número de WhatsApp para recibir y enviar mensajes usando la API oficial de Meta.

---

## 📋 Paso 1: Crear App en Meta for Developers

1. Ve a: https://developers.facebook.com/apps
2. Haz clic en **"Create App"** (Crear aplicación)
3. Selecciona **"Business"** como tipo de app
4. Completa:
   - **Display name**: "Billease WhatsApp Bot" (o el nombre que prefieras)
   - **Contact email**: Tu email
   - **Business Account**: Crea una nueva o selecciona existente
5. Haz clic en **"Create App"**

---

## 📋 Paso 2: Agregar WhatsApp al App

1. En el dashboard de tu app, busca **"WhatsApp"** en la lista de productos
2. Haz clic en **"Set Up"** (Configurar)
3. Elige tu **Business Portfolio** (o crea uno nuevo)

---

## 📋 Paso 3: Obtener Credenciales

### 3.1 Token de Acceso (Access Token)

1. En la sección **WhatsApp** → **API Setup**
2. Encontrarás un **"Temporary access token"** (token temporal)
3. **Copia este token** → Lo usarás como `WHATSAPP_TOKEN` en el `.env`

⚠️ **IMPORTANTE**: Este token expira en **24 horas**. Para producción, necesitarás generar un token permanente (ver Paso 6).

### 3.2 Phone Number ID

1. En la misma sección **API Setup**
2. Verás una tabla con **"Phone number ID"**
3. **Copia este ID** → Lo usarás como `WHATSAPP_PHONE_NUMBER_ID` en el `.env`

### 3.3 Número de WhatsApp de Prueba

Por defecto, Meta te da un número de prueba. Puedes:
- Enviar mensajes a **hasta 5 números de teléfono** que agregues como "testers"
- Para agregar testers: En **API Setup** → **"To"** → Haz clic en **"Manage phone number list"**

---

## 📋 Paso 4: Configurar Webhook

### 4.1 Obtener URL Pública

Necesitas una URL pública HTTPS para que Meta envíe webhooks. Opciones:

**Opción A: Desarrollo local con ngrok**
```bash
# Instalar ngrok: https://ngrok.com/download
ngrok http 8000
```
Copia la URL que te da (ej: `https://abc123.ngrok-free.app`)

**Opción B: Servidor en la nube**
- Heroku, Railway, Render, DigitalOcean, etc.
- Asegúrate de tener HTTPS configurado

### 4.2 Configurar Webhook en Meta

1. En **WhatsApp** → **Configuration** → **Webhook**
2. Haz clic en **"Edit"**
3. Completa:
   - **Callback URL**: `https://tu-url-publica.com/webhook/whatsapp`
   - **Verify token**: Elige una contraseña (ej: `mi_secreto_123`)
     - ⚠️ Este token debe coincidir con `WHATSAPP_VERIFY_TOKEN` en tu `.env`
4. Haz clic en **"Verify and Save"**

Si todo está bien, verás ✅ "Webhook verified" (Webhook verificado)

### 4.3 Suscribir a Eventos

1. Después de verificar el webhook, en **Webhook fields**:
2. Marca la casilla **"messages"** 
3. Guarda los cambios

---

## 📋 Paso 5: Configurar Variables de Entorno

Edita tu archivo `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-tu_clave_aqui

# WhatsApp Meta API
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxxxx          # ← Token del Paso 3.1
WHATSAPP_PHONE_NUMBER_ID=123456789012345       # ← ID del Paso 3.2
WHATSAPP_VERIFY_TOKEN=mi_secreto_123           # ← Token que elegiste en Paso 4.2

# MCP Server
MCP_SERVER_URL=http://localhost:8080
```

---

## 📋 Paso 6: Token Permanente (Producción)

El token temporal expira en 24hrs. Para producción:

### Opción 1: Token de Usuario del Sistema (Recomendado)

1. Ve a **Business Settings** en Meta Business Suite
2. En el menú lateral: **Users** → **System Users**
3. Haz clic en **"Add"** (Agregar)
4. Nombre: "WhatsApp Bot User"
5. Role: **Admin**
6. Después de crear, haz clic en **"Add Assets"** (Agregar activos)
7. Selecciona **Apps** → Tu app → Marca **"Manage app"**
8. Haz clic en **"Generate New Token"**
9. Selecciona **whatsapp_business_messaging** y **whatsapp_business_management**
10. **Copia este token** (¡No podrás verlo de nuevo!)
11. Actualiza `WHATSAPP_TOKEN` en `.env` con este nuevo token

### Opción 2: Extender Token Temporal

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=TU_APP_ID&client_secret=TU_APP_SECRET&fb_exchange_token=TU_TOKEN_TEMPORAL"
```

---

## 📋 Paso 7: Agregar Tu Número Real (Producción)

Para usar tu propio número de WhatsApp Business:

1. Ve a **WhatsApp** → **API Setup**
2. Haz clic en **"Add phone number"**
3. Sigue el proceso de verificación de Meta (puede tardar 1-2 días)
4. Necesitarás:
   - Un número de teléfono que NO esté registrado en WhatsApp
   - Verificar que eres el dueño del negocio
   - Completar el proceso de **Meta Business Verification**

⚠️ **NOTA**: Este proceso es **gratis** pero requiere tiempo de aprobación.

---

## ✅ Verificación: ¿Todo está listo?

Checklist:
- [ ] App creada en Meta for Developers
- [ ] WhatsApp agregado a la app
- [ ] Token de acceso copiado (`WHATSAPP_TOKEN`)
- [ ] Phone Number ID copiado (`WHATSAPP_PHONE_NUMBER_ID`)
- [ ] Webhook configurado y verificado ✅
- [ ] Suscrito a eventos de "messages"
- [ ] Variables en `.env` actualizadas
- [ ] Número de prueba o real agregado

---

## 🧪 Probar el Sistema

1. **Inicia tu servidor:**
   ```bash
   python main.py
   ```

2. **Verifica la salud:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Envía un mensaje de prueba:**
   - Desde tu teléfono, envía un mensaje al número de WhatsApp configurado
   - Prueba: "Hola" o "¿Cuántos usuarios tengo?"
   - Deberías recibir una respuesta automática

---

## 🐛 Problemas Comunes

### Error: "403 Verification Failed"
- ✅ Verifica que `WHATSAPP_VERIFY_TOKEN` coincida en `.env` y Meta Developers
- ✅ Reinicia el servidor después de cambiar `.env`

### Error: "Access token has expired"
- ✅ Genera un token permanente (Paso 6)

### No recibo mensajes
- ✅ Verifica que tu URL pública esté activa (ngrok no expiró)
- ✅ Verifica logs del servidor: `python main.py`
- ✅ En Meta → Webhooks, verifica que esté ✅ "Verified"

### Error: "Cannot send message"
- ✅ Si usas número de prueba, agrega tu número como "tester"
- ✅ Verifica que `WHATSAPP_TOKEN` sea válido

---

## 📚 Recursos Adicionales

- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Getting Started Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [Webhook Setup](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/components)
- [Message Templates](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-message-templates)

---

## 💡 Tips

1. **Desarrollo**: Usa token temporal + ngrok
2. **Producción**: Token permanente + servidor con HTTPS
3. **Costos**: Meta ofrece 1,000 conversaciones gratis/mes
4. **Rate Limits**: 80 mensajes/segundo por número

---

¿Listo para empezar? 🚀 Sigue estos pasos y tu bot estará funcionando en minutos!
