"""
Script de prueba para verificar la conexión con el MCP y OpenAI
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.mcp_client import MCPClient
from services.llm_service import LLMService
from dotenv import load_dotenv

load_dotenv()

import asyncio


async def test_mcp_connection_async() -> bool:
    """Prueba la conexión con el servidor MCP"""
    print("\n" + "="*50)
    print("🔧 Probando conexión con MCP...")
    print("="*50)
    
    try:
        mcp = MCPClient()

        # Listar herramientas disponibles
        print("\n📋 Listando herramientas disponibles:")
        tools = await mcp.list_tools()

        if tools:
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.get('name')} - {tool.get('description', 'Sin descripción')}")
        else:
            print("⚠️  No se encontraron herramientas")

        # Probar llamada a herramienta
        print("\n🔨 Probando herramienta 'read_users_preview':")
        result = await mcp.call_tool("read_users_preview")
        print(f"✅ Resultado: {result[:200]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_openai_connection():
    """Prueba la conexión con OpenAI"""
    print("\n" + "="*50)
    print("🤖 Probando conexión con OpenAI...")
    print("="*50)
    
    try:
        llm = LLMService()
        
        # Prueba simple
        print("\n💬 Generando respuesta de prueba:")
        response = llm.generate_response("Hola, ¿cómo estás?")
        print(f"✅ Respuesta: {response}")
        
        # Prueba con contexto
        print("\n📊 Generando respuesta con contexto:")
        context = '[{"id": 1, "nombre": "Juan"}, {"id": 2, "nombre": "María"}]'
        response = llm.generate_response("¿Cuántos usuarios tengo?", context)
        print(f"✅ Respuesta: {response}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_full_flow_async() -> bool:
    """Prueba el flujo completo: usuario → OpenAI tools → MCP → respuesta"""
    print("\n" + "="*50)
    print("🚀 Probando flujo completo...")
    print("="*50)
    
    try:
        mcp = MCPClient()
        llm = LLMService()

        user_question = "¿Cuántos usuarios activos tengo y qué información puedes ver de ellos?"

        print("\n1️⃣ Enviando pregunta al modelo con tools/MCP...")
        response = await llm.chat_with_mcp(user_question, mcp)

        print("\n✅ Respuesta final (OpenAI + MCP):")
        print(f"   Pregunta: {user_question}")
        print(f"   Respuesta: {response}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "🧪 SUITE DE PRUEBAS - BACKEND WHATSAPP + MCP + OPENAI ".center(50, "="))
    
    results = {
        "MCP": asyncio.run(test_mcp_connection_async()),
        "OpenAI": test_openai_connection(),
        "Flujo Completo": asyncio.run(test_full_flow_async()),
    }
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa la configuración.")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
