# Deployment Plan: Nutrition-RAG

This document outlines the strategy for deploying the complete Nutrition-RAG application, splitting the architecture into a scalable backend hosted on Railway and a high-performance static frontend hosted on Vercel.

## 1. Architecture Overview
- **Backend (Railway)**: The FastAPI server (`src/api/main.py`) will be deployed as a standalone web service. It will handle the RAG pipeline, Pinecone vector database interactions, and Gemini LLM calls.
- **Frontend (Vercel)**: The static files in the `ui/` directory (`index.html` and any assets) will be deployed to Vercel. Vercel will be configured to serve the frontend and seamlessly proxy API requests to the Railway backend.

## 2. Backend Deployment (Railway)

Railway is ideal for our Python/FastAPI backend because it automatically builds from our `requirements.txt` and runs the web service effortlessly.

### Steps to Deploy:
1. **Initialize Railway**:
   - Create a new project on [Railway](https://railway.app/).
   - Connect it to your GitHub repository.
2. **Configure Build & Start Commands**:
   - Railway will automatically detect Python based on `requirements.txt`.
   - **Start Command**: Set the custom start command to:
     ```bash
     uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
     ```
3. **Environment Variables**:
   Configure the following environment variables in the Railway dashboard:
   - `GEMINI_API_KEY` (Your Google Gemini key)
   - `PINECONE_API_KEY` (Your Pinecone API key)
   - `PINECONE_ENV` (if applicable)
   - `PINECONE_INDEX_NAME`
4. **Deploy**:
   - Railway will trigger a deployment. Once complete, it will provide a public URL (e.g., `https://nutrition-api.up.railway.app`). Note this URL for the Vercel setup.

## 3. Frontend Deployment (Vercel)

Vercel is optimized for static sites and frontend frameworks. Since our frontend is currently a single `ui/index.html` file that makes relative API calls (e.g., `/api/v1/chat`), we can use a `vercel.json` file to configure a proxy rewrite. This means we don't have to rewrite our Javascript code to hardcode the Railway URL or deal with complex CORS errors in the browser.

### Steps to Deploy:
1. **Add `vercel.json`**:
   Create a `vercel.json` file in the root of your repository to configure the API rewrites:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/(.*)",
         "destination": "https://<YOUR_RAILWAY_URL>.up.railway.app/api/$1"
       },
       {
         "source": "/(.*)",
         "destination": "/ui/$1"
       }
     ]
   }
   ```
   *Note: Replace `<YOUR_RAILWAY_URL>` with the actual URL provided by Railway in the previous step.*

2. **Initialize Vercel**:
   - Import your GitHub repository into [Vercel](https://vercel.com/).
   - **Framework Preset**: Leave as "Other".
   - **Root Directory**: Leave as the root directory (`/`), so Vercel can read `vercel.json`.
3. **Deploy**:
   - Click "Deploy". Vercel will instantly publish your site. 
   - When a user visits your Vercel URL, it will serve `ui/index.html`.
   - When the frontend JS makes a `fetch('/api/v1/chat')` request, Vercel will invisibly proxy that request to your Railway backend!

## 4. Post-Deployment Checklist
- [ ] **Test Backend Health**: Visit the Railway URL to ensure the FastAPI server is running without crashing.
- [ ] **Test Frontend Load**: Visit the Vercel URL and ensure the beautiful Dietary Guidance UI renders correctly.
- [ ] **Test Integration**: Ask a question in the chatbot on the Vercel URL and ensure it successfully fetches documents and streams the response from the Railway backend.
- [ ] **Continuous Integration**: Ensure that pushing to the `main` branch automatically triggers seamless builds on both Vercel and Railway.
