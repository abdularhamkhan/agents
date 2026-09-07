import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("📚 AI Study Planner")
st.caption("Turn your learning goals into structured, practical steps.")

# Sidebar setup
with st.sidebar:
    st.header("Settings & Tips")

    # Backend status check
    try:
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if health_resp.status_code == 200:
            st.success("Connected to Backend")
        else:
            st.warning("Backend degraded")
    except requests.RequestException:
        st.error("Cannot reach Backend")

    st.markdown("---")
    st.markdown(
        "**💡 Pro Tip:**\n"
        "Need fresh info from the web?\n"
        "Start your query with `search:` or `/search`.\n\n"
        "*Example:* `search: latest python 3.12 features`"
    )

    if st.button("Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! What topic would you like to study today?",
            }
        ]
        st.rerun()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! What topic would you like to study today?",
        }
    ]

# Render existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("What would you like to study?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Planning your study path..."):
            try:
                # Correct API path endpoint
                api_response = requests.post(
                    f"{BACKEND_URL}/api/v1/chat",
                    json={"message": prompt},
                    timeout=120,
                )
                if api_response.ok:
                    data = api_response.json()
                    response = data.get("response", "No response content returned.")
                else:
                    try:
                        err_detail = api_response.json().get("detail")
                    except Exception:
                        err_detail = None
                    response = (
                        f"Error {api_response.status_code}: "
                        f"{err_detail or 'The backend encountered an issue.'}"
                    )
            except requests.RequestException:
                response = (
                    "Could not connect to the backend server. "
                    f"Ensure FastAPI is running at `{BACKEND_URL}`."
                )

        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})




# import os

# import requests
# import streamlit as st

# BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

# st.set_page_config(page_title="AI Study Planner", page_icon="📚", layout="centered")

# st.title("AI Study Planner")
# st.caption("Turn a study goal into a practical next step.")

# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {
#             "role": "assistant",
#             "content": "Hello! What topic would you like to study today?",
#         }
#     ]

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("What would you like to study?"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         with st.spinner("Planning..."):
#             try:
#                 api_response = requests.post(
#                     f"{BACKEND_URL}/api/chat",
#                     json={"message": prompt},
#                     timeout=120,
#                 )
#                 data = api_response.json()
#                 if api_response.ok and data.get("response"):
#                     response = data["response"]
#                 else:
#                     response = data.get("error", "The backend returned an unexpected response.")
#             except requests.RequestException:
#                 response = (
#                     "I could not reach the backend. Start FastAPI and confirm "
#                     f"BACKEND_URL is correct: {BACKEND_URL}"
#                 )
#         st.markdown(response)

#     st.session_state.messages.append({"role": "assistant", "content": response})
