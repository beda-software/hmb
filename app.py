import os
import json

import streamlit as st
import openai
from dotenv import load_dotenv
import streamlit_authenticator as stauth

load_dotenv()

# System prompt for the agent. Edit in place.
INSTRUCTIONS = """
HMB is heavy menstrual bleeding, also known as abnormal Abnormal uterine bleeding.
You have access to documents that contains all required information.
You SHALL only use this documents to answer questions.
YOU SHALL use education language that person without medical background can easily understand.
""".strip()


def str_to_bool(str_input):
    if not isinstance(str_input, str):
        return False
    return str_input.lower() == "true"


def parse_list(value):
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


# Load environment variables
openai_api_key = os.environ.get("OPENAI_API_KEY")
azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.environ.get("AZURE_OPENAI_KEY")
authentication_required = str_to_bool(os.environ.get("AUTHENTICATION_REQUIRED", False))

# Load authentication configuration
authenticator = None
if authentication_required and "credentials" in st.secrets:
    authenticator = stauth.Authenticate(
        st.secrets["credentials"].to_dict(),
        st.secrets["cookie"]["name"],
        st.secrets["cookie"]["key"],
        st.secrets["cookie"]["expiry_days"],
    )

if azure_openai_endpoint and azure_openai_key:
    client = openai.AzureOpenAI(
        api_key=azure_openai_key,
        api_version="2025-04-01-preview",
        azure_endpoint=azure_openai_endpoint,
    )
else:
    client = openai.OpenAI(api_key=openai_api_key)


def load_agent_profiles():
    """Each profile: {title, model, vector_store_ids, instructions?}."""
    multi_agents = os.environ.get("OPENAI_AGENTS")
    if multi_agents:
        return [
            {"instructions": INSTRUCTIONS, **profile}
            for profile in json.loads(multi_agents)
        ]

    model = os.environ.get("MODEL")
    if not model:
        return []
    return [
        {
            "title": os.environ.get("AGENT_TITLE", "Chat"),
            "model": model,
            "instructions": INSTRUCTIONS,
            "vector_store_ids": parse_list(os.environ.get("VECTOR_STORE_IDS")),
        }
    ]


def build_tools(profile):
    vector_store_ids = profile.get("vector_store_ids") or []
    if not vector_store_ids:
        return []
    return [{"type": "file_search", "vector_store_ids": vector_store_ids}]


def format_citations(response):
    filenames = []
    for item in response.output:
        if item.type != "message":
            continue
        for content in item.content:
            if content.type != "output_text":
                continue
            for annotation in content.annotations:
                if annotation.type == "file_citation" and annotation.filename not in filenames:
                    filenames.append(annotation.filename)
    if not filenames:
        return ""
    return "\n\n**Sources:**\n" + "\n".join(f"- {name}" for name in filenames)


def run_stream(user_input, profile):
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = client.conversations.create().id

    stream = client.responses.create(
        model=profile["model"],
        instructions=profile.get("instructions") or None,
        tools=build_tools(profile),
        conversation=st.session_state.conversation_id,
        input=user_input,
        stream=True,
    )

    with st.chat_message("assistant"):
        placeholder = st.empty()
        text = ""
        for event in stream:
            if event.type == "response.output_text.delta":
                text += event.delta
                placeholder.markdown(text, True)
            elif event.type == "response.completed":
                text += format_citations(event.response)
                placeholder.markdown(text, True)
            elif event.type in ("response.failed", "error"):
                st.error("The assistant failed to respond. Please try again.")
                return

    st.session_state.chat_log.append({"name": "assistant", "msg": text})


def render_chat():
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["name"]):
            st.markdown(chat["msg"], True)


if "chat_log" not in st.session_state:
    st.session_state.chat_log = []


def login():
    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")


def reset_chat():
    st.session_state.chat_log = []
    st.session_state.pop("conversation_id", None)


def load_chat_screen(profile):
    st.title(profile.get("title", ""))
    # Disables the input while the response streams.
    user_msg = st.chat_input("Message", submit_mode="disable")
    if user_msg:
        render_chat()
        with st.chat_message("user"):
            st.markdown(user_msg, True)
        st.session_state.chat_log.append({"name": "user", "msg": user_msg})

        run_stream(user_msg, profile)
        st.rerun()

    render_chat()


def main():
    if authenticator is not None:
        authenticator.login()
        if not st.session_state["authentication_status"]:
            login()
            return
        authenticator.logout(location="sidebar")

    profiles = load_agent_profiles()
    if not profiles:
        st.error("No agent configuration defined in environment variables (set MODEL).")
        return

    if len(profiles) == 1:
        load_chat_screen(profiles[0])
        return

    profiles_by_title = {p["title"]: p for p in profiles}
    selected = st.sidebar.selectbox(
        "Select an assistant profile?",
        list(profiles_by_title.keys()),
        index=None,
        placeholder="Select an assistant profile...",
        on_change=reset_chat,
    )
    if selected:
        load_chat_screen(profiles_by_title[selected])


if __name__ == "__main__":
    main()
