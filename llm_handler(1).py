from groq import Groq
import os
from typing import List, Dict
from .rag_processor import RAGProcessor

class ChatbotHandler:
    """
    Maneja las interacciones con Groq + RAG (100% gratis)
    """
    
    def __init__(self):
        # Inicializar RAG
        self.rag = RAGProcessor()
        self.rag.initialize()
        self.data_loaded = self.rag.load_and_process_data()
        
        # Configurar Groq
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key:
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"
            self.api_available = True
        else:
            self.api_available = False
            print("⚠️ GROQ_API_KEY no configurada")
        
        # Sistema de prompts
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema"""
        
        base_prompt = """Eres un asistente virtual especializado en análisis de seguridad ciudadana para el Observatorio de Seguridad de Santander, Colombia.

CARACTERÍSTICAS:
- Respondes en español de manera clara y profesional
- Usas datos específicos de los contextos proporcionados
- Explicas conceptos técnicos de forma accesible
- Eres preciso y citas datos cuando están disponibles

INSTRUCCIONES:
1. SIEMPRE usa los datos del contexto cuando estén disponibles
2. Si el contexto tiene información relevante, úsala en tu respuesta
3. Si no hay datos en el contexto, indícalo claramente
4. Mantén respuestas CONCISAS (máximo 2-3 párrafos)
5. Ve directo al punto

Responde de manera útil, directa y basada en datos.
"""
        
        return base_prompt
    
    def get_response(self, user_message: str, max_tokens: int = 300) -> str:
        """
        Genera respuesta usando RAG + Groq
        """
        
        if not self.api_available:
            return self._fallback_response(user_message)
        
        try:
            # 🔍 PASO 1: Buscar contexto relevante con RAG
            context = ""
            if self.data_loaded:
                context = self.rag.get_context_for_query(user_message)
            
            # 📝 PASO 2: Construir mensajes con contexto
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Agregar contexto si existe
            if context and "No se encontraron" not in context:
                messages.append({
                    "role": "system", 
                    "content": f"CONTEXTO DE DATOS:\n{context}"
                })
            
            # Agregar pregunta del usuario
            messages.append({
                "role": "user", 
                "content": user_message
            })
            
            # 🤖 PASO 3: Generar respuesta con Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.95
            )
            
            # Obtener texto de respuesta
            if response.choices and response.choices[0].message.content:
                cleaned_response = self._clean_response(response.choices[0].message.content)
                return cleaned_response
            else:
                return self._fallback_response(user_message)
            
        except Exception as e:
            print(f"❌ Error con Groq+RAG: {e}")
            return self._fallback_response(user_message)
    
    def _clean_response(self, response: str) -> str:
        """Limpia y formatea la respuesta"""
        response = response.strip()
        
        if response and not response[-1] in ['.', '!', '?']:
            last_period = response.rfind('.')
            if last_period > len(response) * 0.7:
                response = response[:last_period + 1]
        
        return response
    
    def _fallback_response(self, user_message: str) -> str:
        """Respuesta de emergencia"""
        
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ['hola', 'buenos días', 'buenas tardes', 'hey']):
            return """¡Hola! Soy el asistente del Observatorio de Seguridad de Santander con búsqueda inteligente de datos.

Puedo ayudarte con:
- Estadísticas específicas por municipio
- Predicciones de seguridad
- Análisis de tendencias
- Datos históricos de criminalidad

¿Qué necesitas saber?"""
        
        else:
            return """Para consultas específicas, asegúrate de que GROQ_API_KEY esté configurada.

¿Hay algo específico sobre el observatorio que quieras saber?"""
    
    def get_data_summary(self) -> str:
        """Retorna resumen de datos disponibles"""
        if self.data_loaded:
            return self.rag.get_summary()
        else:
            return "⚠️ No hay datos cargados."
