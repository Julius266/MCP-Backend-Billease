-- Script SQL para crear la tabla de logs de métricas
-- Base de datos sugerida: PostgreSQL

-- Tabla: message_logs
-- Almacena todas las métricas de mensajes procesados por el sistema

CREATE TABLE IF NOT EXISTS message_logs (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(50) NOT NULL,
    message_in TEXT NOT NULL,
    message_out TEXT NOT NULL,
    mcp_tools_used JSONB DEFAULT '[]'::jsonb,
    processing_time FLOAT NOT NULL,
    total_time FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejorar el rendimiento de consultas
CREATE INDEX IF NOT EXISTS idx_message_logs_phone_number ON message_logs(phone_number);
CREATE INDEX IF NOT EXISTS idx_message_logs_timestamp ON message_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_message_logs_created_at ON message_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_message_logs_mcp_tools_used ON message_logs USING GIN(mcp_tools_used);

-- Comentarios de las columnas
COMMENT ON TABLE message_logs IS 'Almacena métricas y logs de todos los mensajes procesados por el sistema WhatsApp-MCP';
COMMENT ON COLUMN message_logs.id IS 'ID único del registro';
COMMENT ON COLUMN message_logs.phone_number IS 'Número de teléfono del usuario (formato: +521234567890)';
COMMENT ON COLUMN message_logs.message_in IS 'Mensaje entrante del usuario';
COMMENT ON COLUMN message_logs.message_out IS 'Respuesta generada por el modelo';
COMMENT ON COLUMN message_logs.mcp_tools_used IS 'Array JSON de herramientas MCP utilizadas durante el procesamiento';
COMMENT ON COLUMN message_logs.processing_time IS 'Tiempo de procesamiento del LLM en segundos';
COMMENT ON COLUMN message_logs.total_time IS 'Tiempo total del proceso completo en segundos';
COMMENT ON COLUMN message_logs.timestamp IS 'Hora de llegada del mensaje del usuario';
COMMENT ON COLUMN message_logs.created_at IS 'Fecha y hora de creación del registro en la base de datos';
