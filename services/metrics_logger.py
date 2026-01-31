"""
Servicio de logging de métricas para mensajes de WhatsApp.

Este servicio es completamente opcional y no interfiere con el flujo normal.
Solo se activa si las variables de entorno de la base de datos están configuradas.
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class MetricsLogger:
    """
    Logger de métricas para mensajes de WhatsApp.
    
    Tabla requerida: message_logs
    
    Campos:
    - id: SERIAL PRIMARY KEY
    - phone_number: VARCHAR(50) - Número de teléfono del usuario
    - message_in: TEXT - Mensaje entrante del usuario
    - message_out: TEXT - Respuesta del modelo
    - mcp_tools_used: JSONB - Array de herramientas MCP utilizadas
    - processing_time: FLOAT - Tiempo de procesamiento en segundos
    - total_time: FLOAT - Tiempo total del proceso en segundos
    - timestamp: TIMESTAMP - Hora de llegada del mensaje
    - created_at: TIMESTAMP DEFAULT NOW()
    """
    
    def __init__(self):
        """Inicializa el logger de métricas si las variables de entorno están configuradas."""
        self.enabled = False
        self.db_config = self._load_db_config()
        
        if self.db_config:
            self.enabled = True
            self._test_connection()
            print("📊 MetricsLogger habilitado - Se registrarán logs en la base de datos")
        else:
            print("⚠️ MetricsLogger deshabilitado - Variables de entorno de DB no configuradas")
    
    def _load_db_config(self) -> Optional[Dict[str, str]]:
        """Carga la configuración de la base de datos desde variables de entorno."""
        required_vars = [
            "METRICS_DB_HOST",
            "METRICS_DB_PORT",
            "METRICS_DB_NAME",
            "METRICS_DB_USER",
            "METRICS_DB_PASSWORD"
        ]
        
        config = {}
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                return None
            config[var] = value
        
        return {
            "host": config["METRICS_DB_HOST"],
            "port": config["METRICS_DB_PORT"],
            "database": config["METRICS_DB_NAME"],
            "user": config["METRICS_DB_USER"],
            "password": config["METRICS_DB_PASSWORD"]
        }
    
    def _test_connection(self):
        """Prueba la conexión a la base de datos."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            print("✅ Conexión a base de datos de métricas exitosa")
        except Exception as e:
            print(f"⚠️ Error conectando a base de datos de métricas: {e}")
            print("⚠️ MetricsLogger se deshabilitará automáticamente")
            self.enabled = False
    
    @contextmanager
    def _get_connection(self):
        """Context manager para manejar conexiones a la base de datos."""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def log_message(
        self,
        phone_number: str,
        message_in: str,
        message_out: str,
        mcp_tools_used: List[str],
        processing_time: float,
        total_time: float,
        timestamp: datetime
    ):
        """
        Registra un mensaje y sus métricas en la base de datos.
        
        Args:
            phone_number: Número de teléfono del usuario
            message_in: Mensaje entrante
            message_out: Respuesta del modelo
            mcp_tools_used: Lista de herramientas MCP utilizadas
            processing_time: Tiempo de procesamiento en segundos
            total_time: Tiempo total en segundos
            timestamp: Hora de llegada del mensaje
        """
        if not self.enabled:
            return
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO message_logs 
                        (phone_number, message_in, message_out, mcp_tools_used, 
                         processing_time, total_time, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        query,
                        (
                            phone_number,
                            message_in,
                            message_out,
                            json.dumps(mcp_tools_used),
                            processing_time,
                            total_time,
                            timestamp
                        )
                    )
            print(f"📊 Métrica registrada en DB para {phone_number}")
        except Exception as e:
            # No queremos que un error en el logging rompa el flujo principal
            print(f"⚠️ Error registrando métrica en DB (no afecta flujo principal): {e}")
