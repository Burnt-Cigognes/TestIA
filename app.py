import streamlit as st
from openai import OpenAI
import PyPDF2
from pptx import Presentation
import base64
import io

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="IA CIC",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS — DESIGN RAFFINÉ "CABINET DE CONSEIL"
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background: #10131c;
        color: #ddd8ce;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #13172200;
        border-right: 1px solid #1f2535;
        backdrop-filter: blur(20px);
    }
    section[data-testid="stSidebar"] > div {
        background: #131722;
        padding-top: 0;
    }

    /* ── Sidebar labels ── */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextArea label {
        color: #6b7089 !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 500 !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {
        background: #1b2030 !important;
        border: 1px solid #252c3f !important;
        border-radius: 8px !important;
        color: #ddd8ce !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSelectbox"] svg { fill: #6b7089; }

    /* ── Text area ── */
    .stTextArea textarea {
        background: #1b2030 !important;
        border: 1px solid #252c3f !important;
        border-radius: 8px !important;
        color: #ddd8ce !important;
        font-size: 0.82rem !important;
        font-family: 'DM Sans', sans-serif !important;
        resize: vertical;
    }
    .stTextArea textarea:focus {
        border-color: #b8995a !important;
        box-shadow: 0 0 0 2px rgba(184,153,90,0.15) !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #1b2030;
        border: 1px dashed #252c3f;
        border-radius: 10px;
        padding: 6px;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #b8995a;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #252c3f !important;
        color: #6b7089 !important;
        border-radius: 7px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.06em !important;
        transition: all 0.2s ease !important;
        width: 100%;
        padding: 6px 12px !important;
    }
    .stButton > button:hover {
        border-color: #b8995a !important;
        color: #b8995a !important;
        background: rgba(184,153,90,0.06) !important;
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        background: transparent;
        padding: 12px 0;
        border-bottom: 1px solid #191e2b;
    }
    [data-testid="stChatMessage"]:last-child {
        border-bottom: none;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] {
        background: #1b2030 !important;
        border: 1px solid #252c3f !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ddd8ce !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #b8995a !important;
        box-shadow: 0 0 0 3px rgba(184,153,90,0.1) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #10131c; }
    ::-webkit-scrollbar-thumb { background: #252c3f; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #b8995a; }

    /* ── Custom components ── */
    .sidebar-header {
        padding: 24px 16px 16px;
        border-bottom: 1px solid #1f2535;
        margin-bottom: 16px;
    }
    .sidebar-brand {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.35rem;
        font-weight: 600;
        color: #ddd8ce;
        letter-spacing: 0.02em;
        line-height: 1.2;
    }
    .sidebar-brand span { color: #b8995a; }
    .sidebar-tagline {
        font-size: 0.68rem;
        color: #6b7089;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .section-divider {
        height: 1px;
        background: #1f2535;
        margin: 16px 0;
    }
    .section-label {
        font-size: 0.67rem;
        color: #6b7089;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-weight: 500;
        margin-bottom: 10px;
    }
    .model-free { color: #5a9e7a; }
    .model-paid { color: #b8995a; }
    .file-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #1b2030;
        border: 1px solid #252c3f;
        border-radius: 20px;
        padding: 4px 10px;
        font-size: 0.75rem;
        color: #6b7089;
        margin: 6px 0;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .chat-header {
        padding: 28px 0 16px;
        border-bottom: 1px solid #1f2535;
        margin-bottom: 8px;
    }
    .chat-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.6rem;
        font-weight: 500;
        color: #ddd8ce;
        letter-spacing: -0.01em;
    }
    .chat-title span { color: #b8995a; }
    .chat-meta {
        font-size: 0.73rem;
        color: #6b7089;
        margin-top: 4px;
        letter-spacing: 0.06em;
    }
    .welcome-box {
        background: linear-gradient(135deg, #161b28 0%, #1a1f2e 100%);
        border: 1px solid #1f2535;
        border-left: 3px solid #b8995a;
        border-radius: 10px;
        padding: 24px 28px;
        margin: 20px 0;
    }
    .welcome-box h3 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.2rem;
        font-weight: 500;
        color: #ddd8ce;
        margin: 0 0 10px;
    }
    .welcome-box p {
        font-size: 0.85rem;
        color: #8b90a8;
        margin: 0;
        line-height: 1.7;
    }
    .capability-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 16px;
    }
    .capability-item {
        background: #10131c;
        border: 1px solid #1f2535;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 0.8rem;
        color: #8b90a8;
    }
    .capability-item .icon { font-size: 1rem; margin-bottom: 4px; display: block; }
    .stat-row {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .stat-pill {
        background: #10131c;
        border: 1px solid #1f2535;
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.72rem;
        color: #6b7089;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. MODÈLES DISPONIBLES
# ==========================================
MODELS = {
    "✦ Claude 4 Sonnet — Expert & Code": {
        "id": "anthropic/claude-sonnet-4-5",
        "type": "paid",
        "desc": "Meilleur pour l'analyse, la rédaction et le code complexe"
    },
    "◈ Gemini Flash 2.0 — Rapide & Images": {
        "id": "google/gemini-flash-1.5",
        "type": "paid",
        "desc": "Vision, documents, réponses rapides"
    },
    "○ Qwen 3 Coder — Gratuit": {
        "id": "qwen/qwen3-coder:free",
        "type": "free",
        "desc": "Spécialisé code, gratuit"
    },
    "○ Gemma 4 (27B) — Gratuit": {
        "id": "google/gemma-3-27b-it:free",
        "type": "free",
        "desc": "Modèle généraliste, gratuit"
    },
    "○ DeepSeek R2 — Gratuit": {
        "id": "deepseek/deepseek-r1:free",
        "type": "free",
        "desc": "Raisonnement avancé, gratuit"
    },
}

DEFAULT_SYSTEM_PROMPT = (
    "Tu es un assistant IA professionnel, expert et bienveillant. "
    "Tu réponds de manière claire, structurée et concise en français par défaut, "
    "sauf si l'utilisateur s'adresse à toi dans une autre langue. "
    "Lorsque tu analyses des documents ou des images, tu es précis et exhaustif."
)


# ==========================================
# 4. FONCTIONS UTILITAIRES
# ==========================================
def extract_text_from_pdf(file) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join(
            page.extract_text() or "" for page in pdf_reader.pages
        )
    except Exception as e:
        return f"[Erreur lecture PDF : {e}]"


def extract_text_from_pptx(file) -> str:
    try:
        prs = Presentation(file)
        slides_text = []
        for i, slide in enumerate(prs.slides, 1):
            slide_content = [f"— Slide {i} —"]
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_content.append(shape.text.strip())
            slides_text.append("\n".join(slide_content))
        return "\n\n".join(slides_text)
    except Exception as e:
        return f"[Erreur lecture PPTX : {e}]"


def encode_image_to_base64(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")


def build_api_messages(history: list, system_prompt: str) -> list:
    """
    Reconstruit la liste de messages pour l'API OpenRouter.
    L'historique stocke des dicts {role, content, display_content}.
    """
    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        api_messages.append({
            "role": msg["role"],
            "content": msg["api_content"],  # peut être str ou list (multimodal)
        })
    return api_messages


# ==========================================
# 5. AUTHENTIFICATION
# ==========================================
def check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown("""
    <div style='max-width:360px;margin:80px auto;'>
        <div style='text-align:center;margin-bottom:32px;'>
            <div style='font-family:"Cormorant Garamond",serif;font-size:2rem;
                        color:#ddd8ce;font-weight:600;'>
                IA <span style='color:#b8995a;'>CIC</span>
            </div>
            <div style='font-size:0.72rem;color:#6b7089;letter-spacing:.14em;
                        text-transform:uppercase;margin-top:6px;'>
                Accès collaborateurs
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Mot de passe", type="password", label_visibility="collapsed",
                            placeholder="Mot de passe…")
        if st.button("Accéder →", use_container_width=True):
            if pwd == st.secrets.get("APP_PASSWORD", ""):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    return False


if not check_password():
    st.stop()


# ==========================================
# 6. INITIALISATION SESSION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT


# ==========================================
# 7. CLIENT OPENROUTER
# ==========================================
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["OPENROUTER_API_KEY"],
        default_headers={
            "HTTP-Referer": "https://iacic.streamlit.app",
            "X-Title": "IA CIC",
        }
    )

client = get_client()


# ==========================================
# 8. SIDEBAR
# ==========================================
with st.sidebar:
    # Branding
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-brand">IA <span>CIC</span></div>
        <div class="sidebar-tagline">Intelligence Artificielle Collaborative</div>
    </div>
    """, unsafe_allow_html=True)

    # Sélection du modèle
    st.markdown('<div class="section-label">Modèle</div>', unsafe_allow_html=True)
    selected_model_name = st.selectbox(
        "Modèle",
        list(MODELS.keys()),
        label_visibility="collapsed"
    )
    model_info = MODELS[selected_model_name]
    tag = "PAYANT" if model_info["type"] == "paid" else "GRATUIT"
    color = "#b8995a" if model_info["type"] == "paid" else "#5a9e7a"
    st.markdown(
        f'<div style="font-size:0.72rem;color:{color};margin-top:4px;">'
        f'● {tag} — {model_info["desc"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Prompt système
    st.markdown('<div class="section-label">Instructions système</div>', unsafe_allow_html=True)
    st.session_state.system_prompt = st.text_area(
        "Système",
        value=st.session_state.system_prompt,
        height=110,
        label_visibility="collapsed",
        placeholder="Définir le comportement de l'IA…"
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Fichier joint
    st.markdown('<div class="section-label">Pièce jointe</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Fichier",
        type=["pdf", "pptx", "png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].upper()
        st.markdown(
            f'<div class="file-chip">📎 {uploaded_file.name[:32]}{"…" if len(uploaded_file.name) > 32 else ""}'
            f'<span style="color:#b8995a;margin-left:4px;">{ext}</span></div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Statistiques conversation
    msg_count = len(st.session_state.messages)
    user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-pill">💬 {msg_count} messages</div>'
        f'<div class="stat-pill">👤 {user_count} questions</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    if st.button("🗑  Nouvelle conversation"):
        st.session_state.messages = []
        st.rerun()


# ==========================================
# 9. ZONE PRINCIPALE — EN-TÊTE
# ==========================================
st.markdown(f"""
<div class="chat-header">
    <div class="chat-title">Intelligence <span>Artificielle</span></div>
    <div class="chat-meta">
        Modèle actif : {selected_model_name.split('—')[0].strip()}
        &nbsp;·&nbsp; {len(st.session_state.messages)} messages dans cette session
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 10. ÉCRAN D'ACCUEIL (si pas de messages)
# ==========================================
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <h3>Bienvenue sur votre espace IA</h3>
        <p>
            Posez vos questions, analysez vos documents, rédigez, codez ou explorez
            des idées. Choisissez le modèle adapté à votre besoin dans le panneau latéral.
        </p>
        <div class="capability-grid">
            <div class="capability-item">
                <span class="icon">📄</span>
                Analyse de PDF & PowerPoint
            </div>
            <div class="capability-item">
                <span class="icon">🖼️</span>
                Lecture d'images & captures
            </div>
            <div class="capability-item">
                <span class="icon">💻</span>
                Génération & debug de code
            </div>
            <div class="capability-item">
                <span class="icon">✍️</span>
                Rédaction & synthèse
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 11. AFFICHAGE DE L'HISTORIQUE
# ==========================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Affiche le contenu lisible (texte uniquement, pas le base64)
        st.markdown(message["display_content"])


# ==========================================
# 12. ZONE DE SAISIE & LOGIQUE D'ENVOI
# ==========================================
if prompt := st.chat_input("Posez votre question…"):

    # ── Construire le contenu multimodal pour l'API ──
    api_content = [{"type": "text", "text": prompt}]
    display_content = prompt  # Ce qui s'affiche dans l'interface
    file_note = ""

    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_ext = uploaded_file.name.split(".")[-1].lower()

        if file_ext in ("png", "jpg", "jpeg", "webp"):
            b64 = encode_image_to_base64(file_bytes)
            mime = f"image/{file_ext}" if file_ext != "jpg" else "image/jpeg"
            api_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"}
            })
            file_note = f"\n\n📎 *Image jointe : {uploaded_file.name}*"

        elif file_ext == "pdf":
            text = extract_text_from_pdf(io.BytesIO(file_bytes))
            api_content[0]["text"] += f"\n\n--- Contenu du PDF : {uploaded_file.name} ---\n{text}"
            file_note = f"\n\n📎 *PDF joint : {uploaded_file.name}*"

        elif file_ext == "pptx":
            text = extract_text_from_pptx(io.BytesIO(file_bytes))
            api_content[0]["text"] += f"\n\n--- Contenu du PowerPoint : {uploaded_file.name} ---\n{text}"
            file_note = f"\n\n📎 *PowerPoint joint : {uploaded_file.name}*"

        display_content = prompt + file_note

    # ── Ajouter le message utilisateur à l'historique ──
    st.session_state.messages.append({
        "role": "user",
        "api_content": api_content,     # envoyé à l'API
        "display_content": display_content  # affiché dans le chat
    })

    with st.chat_message("user"):
        st.markdown(display_content)

    # ── Appel à l'IA avec l'historique complet ──
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            api_messages = build_api_messages(
                st.session_state.messages,
                st.session_state.system_prompt
            )

            stream = client.chat.completions.create(
                model=model_info["id"],
                messages=api_messages,
                stream=True,
                max_tokens=4096,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    full_response += delta.content
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ Erreur API : `{e}`"
            response_placeholder.error(full_response)

    # ── Ajouter la réponse à l'historique ──
    st.session_state.messages.append({
        "role": "assistant",
        "api_content": full_response,    # texte simple pour les tours suivants
        "display_content": full_response
    })