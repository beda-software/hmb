# gpt-assistants-api-ui

* 💬 OpenAI Responses API chat UI (migrated from the Assistants API, which OpenAI shut down on 2026-08-26)
* 📚 File search over OpenAI vector stores, with cited sources
* 🏃 Streaming responses, conversation memory via the Conversations API
* 👥 Supports multiple agent profiles in one place
* 🪟 Azure OpenAI client support (untested with the Responses API)

<img width="1459" alt="スクリーンショット 2023-11-20 2 23 51" src="https://github.com/ryo-ma/gpt-assistants-api-ui/assets/6661165/5c288d51-196a-4919-bc4d-dc508146f58a">

## 🌟 Quick Start

1. 👤 Upload your knowledge files to a vector store on the OpenAI site & get its ID (https://platform.openai.com/storage/vector_stores)
2. 🔑 Get the API key from OpenAI (https://platform.openai.com/api-keys)
3. ⬇️ Clone the repository

    ```bash
    $ git clone https://github.com/ryo-ma/gpt-assistants-api-ui.git
    ```

4. 📦 Install dependencies

    ```bash
    $ poetry install
    ```

5. ✍️ Edit the system prompt in the `INSTRUCTIONS` constant at the top of `app.py`

6. ⚙️ Set environment variables file `.env`

    ```bash
    # OpenAI settings
    OPENAI_API_KEY="sk-xxx"
    AUTHENTICATION_REQUIRED="False" # Must change to True if you require authentication

    # When using a single agent, set the following and unset OPENAI_AGENTS.
    MODEL="gpt-4o"
    VECTOR_STORE_IDS="vs_xxx" # Comma-separated; enables file search over these vector stores
    AGENT_TITLE="Chat" # Page title

    # When using multiple agents, set the following instead.
    OPENAI_AGENTS='[{"title": "Agent X", "model": "gpt-4o", "vector_store_ids": ["vs_xxx"]}]'
    ```
    If you use azure instead, set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY`

7. 🔑 Set Authentication configuration (optional)

    To set up authentication, create a [secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management) file `.streamlit/secrets.toml`  as below:

    ```toml
    [credentials]
    usernames = { jsmith = {failed_login_attempts = 0,  logged_in = false, name = "John Smith", password = "abc"}, rbriggs = {failed_login_attempts = 0,  logged_in = false, name = "R Briggs", password = "abc"}}

    [cookie]
    expiry_days = 30
    key = "some_signature_key"  # Must be string
    name = "some_cookie_name"
    ```
    Reference:  [Deploying Streamlit-Authenticator via Streamlit Community Cloud](https://discuss.streamlit.io/t/deploying-streamlit-authenticator-via-streamlit-community-cloud/39085)

## 🏃‍️ Run the app using Streamlit


```bash
$ poetry shell
$ streamlit run app.py
```

## 🐳 Run the app using Docker

1. 💽 Build image

    ```bash
    $ docker compose build
    ```

2. 🏃‍️ Run the app

    ```bash
    $ docker compose up
    ```
Access to [http://localhost:8501](http://localhost:8501).

## 🌐 Deploy to Streamlit Cloud
You can fork this repository and deploy the app to https://share.streamlit.io/. No need to run the app on your local machine.

> Don't forget to choose 3.10 as the Python version and set environment variables in the "Advanced settings" during deployment.

To use authentication with Streamlit Cloud, please use this TOML format:

```toml
# Environment variables
# OpenAI settings
OPENAI_API_KEY="sk-xxx"
AUTHENTICATION_REQUIRED="False" # Must change to True if you require authentication

# When using a single agent, set the following and unset OPENAI_AGENTS.
MODEL="gpt-4o"
VECTOR_STORE_IDS="vs_xxx" # Comma-separated; enables file search over these vector stores
AGENT_TITLE="Chat" # Page title

# When using multiple agents, set the following instead.
OPENAI_AGENTS='[{"title": "Agent X", "model": "gpt-4o", "vector_store_ids": ["vs_xxx"]}]'

# Authentication secrets
[credentials]
usernames = { jsmith = {failed_login_attempts = 0,  logged_in = false, name = "John Smith", password = "abc"}, rbriggs = {failed_login_attempts = 0,  logged_in = false, name = "R Briggs", password = "abc"}}

[cookie]
expiry_days = 30
key = "some_signature_key"  # Must be string
name = "some_cookie_name"
```
