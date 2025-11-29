import streamlit as st
import streamlit.components.v1 as components
from chatbot.llm_handler import ChatbotHandler

# Configuración de la página
st.set_page_config(
    page_title="Observatorio de Seguridad - Santander",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS con Grid Layout para control total
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Ocultar branding */
    #MainMenu, footer, header, .stDeployButton { 
        visibility: hidden; 
    }
    
    /* Fondo blanco sin padding */
    .main {
        background: #ffffff;
        padding: 0 !important;
    }
    
    .stApp {
        background: #ffffff;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Eliminar gaps de columnas */
    [data-testid="column"] {
        padding: 0 !important;
        gap: 0 !important;
    }
    
    .row-widget {
        gap: 0 !important;
    }
    
    /* Forzar alineación superior en columnas */
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
        align-items: flex-start !important;
    }
    
    [data-testid="column"] > div {
        padding: 0.5rem;
    }
    
    /* Power BI iframe */
    iframe {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        display: block;
    }
    
    /* CHAT CONTAINER */
    .chat-container {
        height: 650px;
        display: flex;
        flex-direction: column;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Header del chat */
    .chat-header {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 1rem;
        border-bottom: 1px solid #e5e7eb;
        flex-shrink: 0;
    }
    
    .chat-header h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .chat-header p {
        margin: 0.25rem 0 0 0;
        font-size: 0.75rem;
        opacity: 0.9;
    }
    
    /* Área de mensajes */
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        max-height: calc(650px - 130px); /* Altura total - header - input */
    }
    
    /* Contenedor de chat de Streamlit */
    [data-testid="stChatMessageContainer"] {
        max-height: calc(650px - 130px);
        overflow-y: auto !important;
        overflow-x: hidden;
        display: flex;
        flex-direction: column;
    }
    
    /* Mensajes */
    .stChatMessage {
        background: #f9fafb;
        border-radius: 12px;
        padding: 0.875rem;
        border: 1px solid #e5e7eb;
        max-width: 85%;
        word-wrap: break-word;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: #eff6ff;
        border-color: #bfdbfe;
        margin-left: auto;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: #f9fafb;
        border-color: #e5e7eb;
        margin-right: auto;
    }
    
    .stChatMessage p,
    .stChatMessage div {
        color: #1f2937 !important;
        line-height: 1.5;
        font-size: 0.875rem;
        margin: 0;
    }
    
    /* Input del chat */
    [data-testid="stChatInput"] {
        border-top: 1px solid #e5e7eb;
        padding: 1rem;
        background: #ffffff;
        flex-shrink: 0;
    }
    
    .stChatInput textarea {
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        font-size: 0.875rem;
        padding: 0.75rem !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Mensaje de bienvenida */
    .welcome-message {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border: 1px solid #bae6fd;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .welcome-message h4 {
        color: #0c4a6e;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .welcome-message p {
        color: #075985;
        font-size: 0.8rem;
        margin: 0;
        line-height: 1.5;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f9fafb;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .chat-container {
            height: 500px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# JavaScript para auto-scroll al final (como WhatsApp)
st.components.v1.html("""
    <script>
    function scrollChatToBottom() {
        // Buscar el contenedor de mensajes de Streamlit
        const messagesContainer = window.parent.document.querySelector('[data-testid="stVerticalBlock"]');
        if (messagesContainer) {
            // Scroll suave al final
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // También intentar con otros selectores
        const chatMessages = window.parent.document.querySelector('.chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Ejecutar al cargar
    setTimeout(scrollChatToBottom, 100);
    setTimeout(scrollChatToBottom, 500);
    setTimeout(scrollChatToBottom, 1000);
    
    // Observar cambios en el DOM
    const observer = new MutationObserver(scrollChatToBottom);
    const targetNode = window.parent.document.body;
    if (targetNode) {
        observer.observe(targetNode, { childList: true, subtree: true });
    }
    </script>
""", height=0)

# Crear 2 columnas con proporción 7:3
col_dashboard, col_chat = st.columns([7, 3], gap="small")

# ========== DASHBOARD ==========
with col_dashboard:
    # URL de Power BI
    POWER_BI_URL = "https://app.powerbi.com/view?r=eyJrIjoiZGNkYWQ1MzgtMTNhYi00MGNiLWE4MGItYjU3MGNlMjlkNjQ2IiwidCI6ImEyYmE0MzQ1LTc3NjQtNGQyMi1iNmExLTdjZjUyOGYzYjNhNSIsImMiOjR9"
    components.iframe(POWER_BI_URL, height=650, scrolling=True)

# ========== CHATBOT ==========
with col_chat:
    # Inicializar chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = ChatbotHandler()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Header
    st.markdown("""
        <div class="chat-header">
            <h3>💬 Asistente Virtual</h3>
            <p>Consulta sobre seguridad en Santander</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Container con altura fija y scroll
    chat_container = st.container(height=500)
    
    with chat_container:
        # Mensaje de bienvenida
        if len(st.session_state.chat_history) == 0:
            st.markdown("""
                <div class="welcome-message">
                    <h4>👋 ¡Bienvenido!</h4>
                    <p>Puedo ayudarte con información sobre seguridad ciudadana en Santander. 
                    Pregunta sobre estadísticas, predicciones o datos de municipios.</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Mostrar historial
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Input (fuera del container)
    if user_input := st.chat_input("Escribe tu consulta aquí..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner(""):
            response = st.session_state.chatbot.get_response(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
