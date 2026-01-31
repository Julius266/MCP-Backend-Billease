# Sistema de Logging de Métricas

Este sistema captura y almacena métricas detalladas de todos los mensajes procesados por el backend orquestador de WhatsApp-MCP.

## 📊 Características

El sistema registra automáticamente:
- **Mensaje entrante**: Texto enviado por el usuario
- **Mensaje saliente**: Respuesta generada por el modelo
- **Número de teléfono**: De dónde proviene el mensaje
- **Timestamp**: Hora exacta de llegada del mensaje
- **Herramientas MCP usadas**: Lista de tools MCP invocadas durante el procesamiento
- **Tiempo de procesamiento**: Duración del procesamiento del LLM (en segundos)
- **Tiempo total**: Duración total del proceso completo (en segundos)

## ⚙️ Configuración

### 1. Crear la Base de Datos

Ejecuta el script SQL proporcionado:

```bash
psql -U tu_usuario -d postgres -f create_metrics_table.sql
```

O crea la base de datos manualmente:

```sql
CREATE DATABASE billease_metrics;
\c billease_metrics
-- Luego ejecuta el contenido de create_metrics_table.sql
```

### 2. Configurar Variables de Entorno

En tu archivo `.env`, descomenta y configura las siguientes variables:

```env
# Metrics Database Configuration (OPCIONAL)
METRICS_DB_HOST=localhost
METRICS_DB_PORT=5432
METRICS_DB_NAME=billease_metrics
METRICS_DB_USER=tu_usuario
METRICS_DB_PASSWORD=tu_password
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 🔄 Funcionamiento

### Modo Opcional
El sistema de métricas es **completamente opcional**:
- ✅ Si las variables de entorno están configuradas → Los logs se registran
- ✅ Si las variables NO están configuradas → El sistema funciona normalmente sin logging
- ✅ Si hay un error en el logging → No afecta el flujo principal del sistema

### Flujo de Datos

```
Usuario → WhatsApp → Webhook
                      ↓
                [Captura inicio]
                      ↓
                 Procesar LLM
                      ↓
            [Trackear herramientas MCP]
                      ↓
              Generar respuesta
                      ↓
            [Calcular tiempos totales]
                      ↓
             Enviar por WhatsApp
                      ↓
          [Guardar métricas en DB] ← Opcional
                      ↓
                  Responder OK
```

## 📋 Estructura de la Tabla

**Nombre de la tabla**: `message_logs`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | SERIAL | ID único del registro |
| `phone_number` | VARCHAR(50) | Número de teléfono del usuario |
| `message_in` | TEXT | Mensaje entrante |
| `message_out` | TEXT | Respuesta del modelo |
| `mcp_tools_used` | JSONB | Array de herramientas MCP usadas |
| `processing_time` | FLOAT | Tiempo de procesamiento LLM (segundos) |
| `total_time` | FLOAT | Tiempo total del proceso (segundos) |
| `timestamp` | TIMESTAMP | Hora de llegada del mensaje |
| `created_at` | TIMESTAMP | Hora de creación del registro |

## 📈 Consultas Útiles

### Ver últimos 10 mensajes
```sql
SELECT 
    phone_number,
    message_in,
    message_out,
    mcp_tools_used,
    processing_time,
    total_time,
    timestamp
FROM message_logs
ORDER BY timestamp DESC
LIMIT 10;
```

### Herramientas MCP más usadas
```sql
SELECT 
    jsonb_array_elements_text(mcp_tools_used) as tool_name,
    COUNT(*) as usage_count
FROM message_logs
WHERE jsonb_array_length(mcp_tools_used) > 0
GROUP BY tool_name
ORDER BY usage_count DESC;
```

### Tiempo promedio de procesamiento
```sql
SELECT 
    AVG(processing_time) as avg_processing_time,
    AVG(total_time) as avg_total_time,
    MAX(processing_time) as max_processing_time,
    MAX(total_time) as max_total_time
FROM message_logs;
```

### Mensajes por usuario
```sql
SELECT 
    phone_number,
    COUNT(*) as message_count,
    AVG(processing_time) as avg_processing_time
FROM message_logs
GROUP BY phone_number
ORDER BY message_count DESC;
```

### Mensajes con errores
```sql
SELECT 
    phone_number,
    message_in,
    message_out,
    timestamp
FROM message_logs
WHERE message_out LIKE 'ERROR:%'
ORDER BY timestamp DESC;
```

## 🛡️ Seguridad

- Las credenciales de la base de datos se almacenan en `.env` (no subir a git)
- La conexión a la base de datos usa autenticación con usuario y contraseña
- Los errores de logging no exponen información sensible al usuario final
- El sistema continúa funcionando incluso si el logging falla

## 🚀 Ejecución

No hay cambios en la ejecución del sistema:

```bash
python main.py
```

El sistema detectará automáticamente si debe registrar métricas basándose en las variables de entorno.

## ⚠️ Notas Importantes

1. **No afecta el rendimiento**: El logging se hace después de responder al usuario
2. **Tolerante a fallos**: Si hay un error en el logging, el mensaje se procesa normalmente
3. **Opcional**: El sistema funciona perfectamente sin la base de datos de métricas
4. **PostgreSQL**: El sistema usa PostgreSQL, pero puede adaptarse a otras bases de datos relacionales
