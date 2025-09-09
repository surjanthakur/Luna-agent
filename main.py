import streamlit as st
from PIL import Image
from chat_functions import (
    init_session_state,
    create_new_chat,
    load_chat,
    save_current_chat,
)
from compile_graph import graph
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
import time


# Page config
st.set_page_config(
    page_title="Luna Ai",
    page_icon="🤖",
    layout="wide",  # "centered" se "wide" kar diya
    initial_sidebar_state="expanded",
)

# Styling of page
st.markdown(
    """
<style>
/* Primary color (button, highlight) */
.st-emotion-cache-ocqkz7 {
  background-color: #3c3d37 !important;
  color: #ffd700 !important;
}

/* Page background */
.stApp {
  background-color: #0e1117;
}

/* Sidebar background */
section[data-testid="stSidebar"] {
  background-color: #262730;
}

/* Text color */
.stMarkdown,
.stText,
.css-10trblm {
  color: white !important;
}

.main-header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 3px solid white;
    margin-bottom: 2rem;
    background-color: #3c3d37;
    border-radius: 20px;
    margin-top: 1rem;
}

.main-header h3 {
    color: #ffd700;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 4px 4px 10px rgba(255, 215, 0, 0.3);
}

.main-header p {
    color: #ffff;
    font-size: 1.1rem;
    font-weight: 400;
}
</style>
""",
    unsafe_allow_html=True,
)


# Display UI
def main():
    init_session_state()

    # Sidebar UI
    with st.sidebar:
        image = Image.open("images/luna_ai_logo_color_of_yellow.jpeg")
        st.image(image, caption="luna ai", width=50)

        if st.button("➕ New Chat", use_container_width=True):
            create_new_chat()
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.session_state.chat_history:
            st.markdown("Chats")

            for chat_id, chat_data in reversed(
                list(st.session_state.chat_history.items())
            ):
                is_current = chat_id == st.session_state.current_chat_id

                st.markdown('<div class="chat-item">', unsafe_allow_html=True)
                col1, col2 = st.columns([4, 1])

                with col1:
                    if st.button(
                        f"💭 {chat_data['title']}",
                        key=f"chat_{chat_id}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary",
                    ):
                        load_chat(chat_id)
                        st.rerun()

                with col2:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("🧹", key=f"delete_{chat_id}", help="Delete chat"):
                        del st.session_state.chat_history[chat_id]
                        if chat_id == st.session_state.current_chat_id:
                            st.session_state.current_chat_id = None
                            st.session_state.messages = []
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("🎯 No chat history yet. Start a new conversation!")

        # Sidebar footer
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            """
        <div style="text-align: center; color: #ffff; font-size: 0.8rem; margin-top: 2rem;">
            <p>⚙️ available Tools</p>
            <p>✅ weather_info ✅ web_search ✅ general_info ✅ wikipidia search</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if st.session_state.messages == []:
        st.markdown(
            """
        <div class="main-header">
            <h3>👋 I'm Luna Your Ai Agent!</h3>
            <p>I use tools to do cool things.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Create new chat if none exists
    if not st.session_state.current_chat_id:
        create_new_chat()

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.text(message["content"])

    # Chat input
    if prompt := st.chat_input("luna tell me.."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.text(prompt)

        with st.spinner("🤔 Thinking...", show_time=True):
            config = RunnableConfig(
                configurable={"thread_id": st.session_state.current_chat_id},
            )
            # Use a mutable holder so the generator can set/modify it
            status_holder = {"box": None}

            def ai_only_stream():
                for message_chunk, metadata in graph.stream(
                    {"messages": [HumanMessage(content=prompt)]},
                    config=config,
                    stream_mode="messages",
                ):
                    if isinstance(message_chunk, ToolMessage):
                        tool_name = getattr(message_chunk, "name", "tool")
                        if status_holder["box"] is None:
                            status_holder["box"] = st.status(  # type: ignore
                                f"🔧 tool calling :   {tool_name}"
                            )
                        else:
                            status_holder["box"].update(
                                label=f"🔧 Using `{tool_name}` …",
                                state="running",
                                expanded=True,
                            )
                    # Stream ONLY assistant tokens
                    if isinstance(message_chunk, AIMessage):
                        yield message_chunk.content

            ai_message = st.write_stream(ai_only_stream())

            # Finalize only if a tool was actually used
            if status_holder["box"] is not None:
                status_holder["box"].update(
                    label="✅ Tool finished", state="complete", expanded=False
                )

        st.session_state.messages.append({"role": "assistant", "content": ai_message})

        # Save current chat
        save_current_chat()
        st.rerun()


if __name__ == "__main__":
    main()
