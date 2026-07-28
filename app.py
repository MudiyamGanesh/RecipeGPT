import os
import json
import base64
from datetime import datetime

import streamlit as st

from recipe import create_recipegpt_chain


# ==========================================================
# CONFIGURATION
# ==========================================================
RECENTS_DIR = "recents"
IMAGES_DIR = "images"

os.makedirs(RECENTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="RecipeGPT AI",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# LOAD BACKEND (CACHED)
# ==========================================================
@st.cache_resource
def load_chain():
    return create_recipegpt_chain()


# ==========================================================
# SESSION STATE
# ==========================================================
if "qa_chain" not in st.session_state:
    with st.spinner("Loading RecipeGPT AI..."):
        st.session_state.qa_chain = load_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_chat_file" not in st.session_state:
    st.session_state.current_chat_file = None

if "carousel_index" not in st.session_state:
    st.session_state.carousel_index = 0


# ==========================================================
# CUSTOM CSS
# ==========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

    /* Global Typography & Scrolling */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
        scroll-behavior: smooth;
    }

    /* Main App Background */
    .stApp, [data-testid="stAppViewContainer"], .main {
        background: #F5A623 !important; /* Vibrant Solid Orange */
        color: #FFFFFF !important;
    }
    
    /* Header (Top Nav) transparent */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Remove Streamlit padding for full-width hero */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 6rem !important;
    }

    /* Sidebar Restyling */
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: none !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.08) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #D97706 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    [data-testid="collapsedControl"] {
        color: #FFFFFF !important;
        background: rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
    }

    /* Sidebar Buttons */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #E53935 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(229, 57, 53, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #D32F2F !important;
        box-shadow: 0 6px 16px rgba(229, 57, 53, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #D97706 !important;
        border: 1px solid rgba(217, 119, 6, 0.15) !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 0.8rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: #FFF8F0 !important;
        border-color: #D97706 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(217, 119, 6, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button p {
        color: inherit !important;
    }

    /* Chat Messages Glassmorphism */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.22) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 24px !important;
        padding: 1.5rem 1.8rem !important;
        margin-bottom: 1.5rem !important;
        color: #FFFFFF !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1) !important;
        animation: fadeInUp 0.5s ease forwards;
        transition: transform 0.3s ease !important;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        font-weight: 500 !important;
    }

    [data-testid="stChatMessage"] [data-testid="stIconMaterial"] {
        color: #FFFFFF !important;
    }

    /* Avatars */
    [data-testid="stChatMessageAvatarUser"] {
        background: #E53935 !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stChatMessageAvatarAssistant"] {
        background: #FFFFFF !important;
        color: #D97706 !important;
    }

    /* FIX: Completely Remove Black Background from Bottom Container */
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] > div,
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    .stChatFloatingInputContainer {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Ensure padding at the bottom */
    [data-testid="stBottomBlockContainer"] {
        padding-bottom: 2rem !important;
    }

    /* Chat Input Fixed Bottom */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 30px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.15) !important;
        padding: 0.3rem !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(255, 255, 255, 0.9) !important;
    }

    [data-testid="stChatInput"] button {
        background: #E53935 !important;
        color: #FFFFFF !important;
        border-radius: 50% !important;
        transition: all 0.3s ease !important;
        height: 2.5rem !important;
        width: 2.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-right: 0.3rem !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: #D32F2F !important;
        transform: scale(1.08) !important;
        box-shadow: 0 4px 12px rgba(229, 57, 53, 0.4) !important;
    }

    [data-testid="stChatInput"] svg {
        fill: #FFFFFF !important;
    }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* =========================================================
       YUMMY HERO FULL-SCREEN STYLES
       ========================================================= */
    .hero-wrapper {
        position: relative;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        height: calc(100vh - 120px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-top: -3rem; /* Offset Streamlit padding */
    }

    .fake-topnav {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 2rem 4rem;
        z-index: 10;
    }
    .topnav-logo {
        font-weight: 900;
        font-size: 1.4rem;
        color: #FFFFFF;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .topnav-links {
        display: flex;
        gap: 3rem;
    }
    .topnav-links span {
        font-size: 0.9rem;
        font-weight: 700;
        color: rgba(255,255,255,0.85);
        letter-spacing: 2px;
        cursor: pointer;
        transition: color 0.2s;
    }
    .topnav-links span:hover {
        color: #FFFFFF;
    }
    .topnav-icon {
        font-size: 1.4rem;
        color: #FFFFFF;
        cursor: pointer;
    }

    .yummy-container {
        position: relative;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .yummy-bg-text {
        position: absolute;
        font-size: 15vw;
        font-weight: 900;
        color: #FFFFFF;
        z-index: 1;
        text-shadow: 0px 20px 50px rgba(0,0,0,0.15);
        white-space: nowrap;
        line-height: 1;
        letter-spacing: 0.1em;
    }
    .yummy-img-wrapper {
        position: relative;
        z-index: 2;
        width: 60%;
        max-width: 650px;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: float 5s ease-in-out infinite;
        filter: drop-shadow(0 40px 50px rgba(0,0,0,0.35));
    }
    .hero-center-img {
        width: 100%;
        height: auto;
        object-fit: contain;
        max-height: 60vh;
    }
    
    .carousel-fade {
        position: absolute;
        opacity: 0;
        animation-name: heroCarousel;
        animation-iteration-count: infinite;
        animation-timing-function: ease-in-out;
    }

    .yummy-small-text-1 {
        position: absolute;
        top: 28%;
        left: 12%;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 0.4em;
        color: #FFFFFF;
        z-index: 3;
        text-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .yummy-small-text-2 {
        position: absolute;
        bottom: 28%;
        right: 12%;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 0.4em;
        color: #FFFFFF;
        z-index: 3;
        text-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }

    .fake-bottom-btn {
        position: absolute;
        bottom: 3rem;
        right: 4rem;
        z-index: 10;
    }
    .fake-bottom-btn button {
        background: #E53935;
        color: white;
        border: none;
        padding: 0.8rem 2.5rem;
        border-radius: 30px;
        font-weight: 800;
        letter-spacing: 2px;
        font-size: 0.9rem;
        box-shadow: 0 10px 20px rgba(229,57,53,0.4);
        cursor: pointer;
        transition: transform 0.2s;
    }
    .fake-bottom-btn button:hover {
        transform: scale(1.05);
    }

    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-25px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    /* Responsive adjustments */
    @media (max-width: 1024px) {
        .yummy-bg-text { font-size: 18vw; }
        .yummy-small-text-1, .yummy-small-text-2 { font-size: 1.2rem; }
        .fake-topnav { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def get_recent_files():
    files = [
        os.path.join(RECENTS_DIR, f)
        for f in os.listdir(RECENTS_DIR)
        if f.endswith(".json")
    ]
    files.sort(reverse=True)
    return files


def generate_chat_title(first_message):
    title = first_message.strip().replace("\n", " ")
    if len(title) > 40:
        title = title[:40] + "..."
    return title or "Untitled Chat"


def save_current_conversation():
    messages = st.session_state.messages

    if not messages:
        return

    conversation = []
    i = 0
    while i < len(messages) - 1:
        if (
            messages[i]["role"] == "user"
            and messages[i + 1]["role"] == "assistant"
        ):
            conversation.append(
                {
                    "user": messages[i]["content"],
                    "assistant": messages[i + 1]["content"],
                }
            )
            i += 2
        else:
            i += 1

    if not conversation:
        return

    if st.session_state.current_chat_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = generate_chat_title(conversation[0]["user"])
        safe_title = "".join(
            c for c in title if c.isalnum() or c in (" ", "-", "_")
        ).strip().replace(" ", "_")

        filename = f"{timestamp}_{safe_title}.json"
        st.session_state.current_chat_file = os.path.join(
            RECENTS_DIR,
            filename,
        )

    data = {
        "timestamp": datetime.now().isoformat(),
        "title": generate_chat_title(conversation[0]["user"]),
        "conversation": conversation,
    }

    with open(st.session_state.current_chat_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_conversation(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conversation = data.get("conversation", [])

    st.session_state.messages = []

    chain = st.session_state.qa_chain
    chain.memory.clear()

    for turn in conversation:
        user_msg = turn["user"]
        ai_msg = turn["assistant"]

        st.session_state.messages.append(
            {"role": "user", "content": user_msg}
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": ai_msg}
        )

        chain.memory.chat_memory.add_user_message(user_msg)
        chain.memory.chat_memory.add_ai_message(ai_msg)

    st.session_state.current_chat_file = file_path


def start_new_chat():
    save_current_conversation()
    st.session_state.messages = []
    st.session_state.qa_chain.memory.clear()
    st.session_state.current_chat_file = None


def get_food_images():
    supported = (".png", ".jpg", ".jpeg", ".webp")
    return [
        os.path.join(IMAGES_DIR, f)
        for f in sorted(os.listdir(IMAGES_DIR))
        if f.lower().endswith(supported)
    ]


# ==========================================================
# SIDEBAR
# ==========================================================
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 2.5rem;">
        <span style="font-size: 2.2rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">🍽️</span>
        <h2 style="color: #D97706; font-weight: 800; margin: 0; font-size: 1.6rem; letter-spacing: -0.02em;">
            RecipeGPT
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)

if st.sidebar.button("➕ New Chat", use_container_width=True, type="primary"):
    start_new_chat()
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<h3 style='color: #D97706; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-bottom: 1rem;'>Recent Chats</h3>", 
    unsafe_allow_html=True
)

recent_files = get_recent_files()

if recent_files:
    for file_path in recent_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            title = data.get("title") or os.path.basename(file_path)

            col1, col2 = st.sidebar.columns([5, 1])

            with col1:
                if st.button(
                    title,
                    key=f"open_{file_path}",
                    use_container_width=True,
                ):
                    save_current_conversation()
                    load_conversation(file_path)
                    st.rerun()

            with col2:
                if st.button(
                    "🗑️",
                    key=f"delete_{file_path}",
                    use_container_width=True,
                ):
                    os.remove(file_path)

                    if st.session_state.current_chat_file == file_path:
                        st.session_state.messages = []
                        st.session_state.qa_chain.memory.clear()
                        st.session_state.current_chat_file = None

                    st.rerun()

        except Exception:
            continue
else:
    st.sidebar.markdown(
        "<div style='color: #D97706; opacity: 0.7; font-size: 0.9rem; font-weight: 500;'>No saved conversations yet.</div>",
        unsafe_allow_html=True
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<h3 style='color: #D97706; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-bottom: 1rem;'>Features</h3>", 
    unsafe_allow_html=True
)
st.sidebar.markdown(
    """
    <div style='color: #D97706; font-size: 0.95rem; line-height: 1.8; font-weight: 500;'>
        ✨ Recipe Generation<br>
        🔍 Ingredient Suggestions<br>
        🥗 Ingredient-Based Search<br>
        📅 Meal Planning<br>
        🧠 Conversation Memory
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# CHAT INPUT & STATE UPDATE
# ==========================================================
prompt = st.chat_input("Ask for a recipe, ingredient swap, or meal plan...") 

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )


# ==========================================================
# MAIN LAYOUT & CHAT HISTORY
# ==========================================================
if not st.session_state.messages:
    images = get_food_images()
    total_images = len(images)
    
    img_tags = ""
    dynamic_keyframes = ""

    if images:
        animation_duration = max(10, total_images * 4)
        
        if total_images > 1:
            for i, img_path in enumerate(images):
                img_b64 = get_base64_image(img_path)
                delay = (animation_duration / total_images) * i
                img_tags += f'''
                <img src="data:image/png;base64,{img_b64}" 
                     class="hero-center-img carousel-fade" 
                     style="animation-delay: {delay}s; animation-duration: {animation_duration}s;">
                '''
            
            # Generate mathematically perfect crossfade keyframes dynamically
            dynamic_keyframes = f'''
            <style>
            @keyframes heroCarousel {{
                0% {{ opacity: 0; transform: scale(1.05) rotate(-2deg); }}
                10% {{ opacity: 1; transform: scale(1) rotate(0deg); }}
                {(100/total_images)}% {{ opacity: 1; transform: scale(1) rotate(0deg); }}
                {((100/total_images) + 10)}% {{ opacity: 0; transform: scale(1.05) rotate(2deg); }}
                100% {{ opacity: 0; }}
            }}
            </style>
            '''
        else:
            img_b64 = get_base64_image(images[0])
            img_tags = f'<img src="data:image/png;base64,{img_b64}" class="hero-center-img" style="opacity:1;">'
    else:
        img_tags = '<div style="font-size: 10rem;">🍔</div>'

    st.markdown(dynamic_keyframes, unsafe_allow_html=True)

    # FULL SCREEN YUMMY HERO LAYOUT
    st.markdown(
        f"""
        <div class="hero-wrapper">
            <div class="fake-topnav">
                <div class="topnav-logo">🍔 RECIPEGPT</div>
                <div class="topnav-links">
                    <span>INICIO</span>
                    <span>MENU</span>
                    <span>DISCOVER</span>
                    <span>BLOG</span>
                    <span>CONTACTO</span>
                </div>
                <div class="topnav-icon">🛒</div>
            </div>
            
            <div class="yummy-container">
                <div class="yummy-small-text-1">GIGANTE</div>
                <div class="yummy-bg-text">R E C I P E</div>
                <div class="yummy-small-text-2">ESPECIAL</div>
                
                <div class="yummy-img-wrapper">
                    {img_tags}
                </div>
            </div>
            
            <div class="fake-bottom-btn">
                <button>ORDENAR</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    # Minimal top header when chatting
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem; animation: fadeInUp 0.5s ease forwards;">
            <h2 style="color: #FFFFFF; font-weight: 800; margin: 0; text-shadow: 0 4px 12px rgba(0,0,0,0.15); font-size: 2rem; letter-spacing: 2px;">
                🍽️ RecipeGPT AI
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# Render Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Generate new response if the last message is from user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Cooking up the best answer..."): 
            try:
                result = st.session_state.qa_chain.invoke(
                    {"question": st.session_state.messages[-1]["content"]}
                )
                answer = result.get("answer", "No response generated.")
            except Exception as e:
                answer = f"Error: {e}"

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    save_current_conversation()