# Deployment Guide for RAG App

This guide explains how to deploy your "Government-Grade RAG Assistant" so it runs 24/7 and can be shared via a link.

We will deploy in two parts:
1.  **Backend (API)**: Deployed on **Render** (Free Tier).
2.  **Frontend (UI)**: Deployed on **Streamlit Cloud** (Free).

## Prerequisites
- A GitHub account.
- Your code pushed to a GitHub repository.
- Accounts on [Render.com](https://render.com) and [Streamlit Cloud](https://streamlit.io/cloud).

---

## Part 1: Deploy Backend to Render

1.  **Log in to Render** and click **"New +"** -> **"Web Service"**.
2.  **Connect your GitHub repo**.
3.  **Configure the service**:
    - **Name**: `my-rag-backend` (or similar)
    - **Runtime**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables** (Click "Advanced" or "Environment"):
    - `PYTHON_VERSION`: `3.11.0` (Recommended)
    - `OPENAI_API_KEY`: (If you use it)
    - `GROQ_API_KEY`: (Your Groq Key)
    - `VECTOR_DB_URL`: (Use Qdrant Cloud URL or keep empty if using ephemeral local storage, *see note below*)
    - `VECTOR_DB_API_KEY`: (If using Qdrant Cloud)
5.  **Click "Create Web Service"**.
6.  **Wait for deployment**. Once live, copy the **Service URL** (e.g., `https://my-rag-backend.onrender.com`).

> **Note on Database**: By default, this app uses a local file-based Qdrant. On Render's free tier, *files are not persistent* (data is lost on restart). For permanent storage, sign up for [Qdrant Cloud](https://qdrant.tech/) (free tier available) and set the `VECTOR_DB_URL` and `VECTOR_DB_API_KEY` environment variables in Render.

---

## Part 2: Deploy Frontend to Streamlit Cloud

1.  **Log in to Streamlit Cloud**.
2.  **Click "New app"**.
3.  **Select your repo**, branch (usually `main`), and file path (`streamlit_app.py`).
4.  **Click "Advanced settings"** -> **"Secrets"** (or Environment Variables).
5.  **Add the Backend URL**:
    ```toml
    API_URL = "https://your-backend-name.onrender.com/api/v1"
    CHECK_URL = "https://your-backend-name.onrender.com/health"
    ```
    *(Replace `https://your-backend-name.onrender.com` with the URL you copied from Render)*.
6.  **Click "Deploy"**.

## Status
Once both are active, you can share the Streamlit App link with anyone!

**Troubleshooting**:
- If the app says "Backend seems unstable", check the Render logs to ensure the backend is running.
- If data disappears after a while, it's because the Render free tier spins down after inactivity. It will wake up when you try to access it (might take 50s). To fix data loss, use Qdrant Cloud.
