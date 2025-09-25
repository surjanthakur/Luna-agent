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
    layout="centered",
    initial_sidebar_state="expanded",
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def refresh():
    st.rerun()


def render_messages(role, content):
    css_class = "user-message" if role == "user" else "assistant-message"
    name = "You" if role == "user" else "luna"
    st.markdown(
        f"""
            <div class="{css_class}">
                <strong>{name}: </strong>{content}
            </div>
            """,
        unsafe_allow_html=True,
    )


def render_chat_item(chat_id, chat_data, is_current):
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button(
            f"💭 {chat_data['title']}",
            key=f"chat_{chat_id}",
            use_container_width=True,
            type="primary" if is_current else "secondary",
        ):
            load_chat(chat_id)
            refresh()
    with col2:
        if st.button("🧹", key=f"delete_{chat_id}", help="Delete chat"):
            del st.session_state.chat_history[chat_id]
            if chat_id == st.session_state.current_chat_id:
                st.session_state.current_chat_id = None
                st.session_state.messages = []
            refresh()


# Display UI
def main():
    init_session_state()

    # Sidebar UI
    with st.sidebar:
        image = Image.open("images/luna_ai_logo_color_of_yellow.jpeg")
        st.image(image, caption="luna ai", width=50)

        if st.button("➕ New Chat", use_container_width=True):
            create_new_chat()
            refresh()

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.session_state.chat_history:
            st.markdown("Chats")

            for chat_id, chat_data in reversed(
                list(st.session_state.chat_history.items())
            ):
                render_chat_item(
                    chat_id, chat_data, chat_id == st.session_state.current_chat_id
                )
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

        # render existing messages
    for msg in st.session_state.messages:
        render_messages(msg["role"], msg["content"])

    # Chat input
    if prompt := st.chat_input("luna tell me.."):
        st.session_state.messages.append({"role": "user", "content": prompt})

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
        refresh()


if __name__ == "__main__":
    main()
