import streamlit as st
import uuid
from datetime import datetime


# session state
def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


# create new chat
def create_new_chat():
    chat_id = str(uuid.uuid4().hex[:5])
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    chat_title = f"chat at: {date_time}"

    st.session_state.chat_history[chat_id] = {
        "title": chat_title,
        "messages": [],
        "created_at": date_time,
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []


# load chat based on id
def load_chat(chat_id):
    chat_history = st.session_state.get("chat_history", {})
    if not chat_history:
        st.warning("⚠️ No  Chat History Found !")
        return

    chat_data = chat_history.get(chat_id)

    if chat_data:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = chat_data.get("messages", [])
    else:
        st.error(f"❌ Chat ID '{chat_id}' not found.")


# save current chat with unique id
def save_current_chat():
    if st.session_state.current_chat_id:
        st.session_state.chat_history[st.session_state.current_chat_id][
            "messages"
        ] = st.session_state.messages
