# Deployment Guide

This guide covers multiple deployment options for the FLUD project.

## Table of Contents
1. [Docker Deployment](#docker-deployment)
2. [Railway](#railway)
3. [Render](#render)
4. [Vercel (Frontend) + Railway/Render (Backend)](#vercel-frontend--railwayrender-backend)
5. [Traditional VPS](#traditional-vps)

---

## Docker Deployment

### Prerequisites
- Docker and Docker Compose installed

### Steps

1. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

2. **Access the application:**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

### Environment Variables
Create a `.env` file for environment variables:
```env
CDS_API_URL=https://cds.climate.copernicus.eu/api/v2
CDS_API_KEY=your_uid:your_api_key
```

**Note:** For production, configure CDS API credentials as environment variables or use a secrets manager.

---

## Railway

Railway is excellent for full-stack deployments with automatic deployments from Git.

### Backend Deployment

1. **Sign up at [railway.app](https://railway.app)**

2. **Create a new project** and connect your GitHub repository

3. **Add a new service** and select your repository

4. **Configure the service:**
   - Root Directory: `/flood_model`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

5. **Add environment variables:**
   - `CDS_API_URL`: `https://cds.climate.copernicus.eu/api/v2`
   - `CDS_API_KEY`: Your CDS API key (format: `uid:key`)

6. **Deploy** - Railway will automatically deploy on push

### Frontend Deployment

1. **Add another service** in the same project

2. **Configure:**
   - Root Directory: `/frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview` (or use static hosting)

3. **Add environment variable:**
   - `VITE_API_URL`: Your backend Railway URL (e.g., `https://flud-backend.railway.app`)

4. **Deploy**

### Using railway.json
The project includes a `railway.json` file for easier configuration.

---

## Render

Render offers free tier hosting with automatic SSL.

### Backend Deployment

1. **Sign up at [render.com](https://render.com)**

2. **Create a new Web Service**

3. **Connect your repository**

4. **Configure:**
   - **Name:** `flud-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd flood_model && uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** Leave empty (or set to project root)

5. **Add Environment Variables:**
   - `CDS_API_URL`: `https://cds.climate.copernicus.eu/api/v2`
   - `CDS_API_KEY`: Your CDS API key

6. **Deploy**

### Frontend Deployment

1. **Create a new Static Site**

2. **Configure:**
   - **Name:** `flud-frontend`
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`

3. **Add Environment Variable:**
   - `VITE_API_URL`: Your backend Render URL (e.g., `https://flud-backend.onrender.com`)

4. **Add Rewrite Rule** (in Advanced settings):
   - Source: `/api/*`
   - Destination: `https://flud-backend.onrender.com/api/*`

5. **Deploy**

### Using render.yaml
The project includes a `render.yaml` file for infrastructure-as-code deployment.

---

## Vercel (Frontend) + Railway/Render (Backend)

This is a popular pattern: deploy frontend on Vercel and backend separately.

### Backend
Deploy backend using Railway or Render (see above).

### Frontend on Vercel

1. **Sign up at [vercel.com](https://vercel.com)**

2. **Import your GitHub repository**

3. **Configure:**
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

4. **Add Environment Variable:**
   - `VITE_API_URL`: Your backend URL

5. **Deploy**

6. **Configure API Proxy** (optional):
   - In `vercel.json`, add rewrites to proxy `/api/*` to your backend

Create `vercel.json` in project root:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.com/api/:path*"
    }
  ]
}
```

---

## Traditional VPS

Deploy on a VPS like DigitalOcean, AWS EC2, or Linode.

### Prerequisites
- Ubuntu 20.04+ server
- Domain name (optional but recommended)
- SSH access

### Backend Setup

1. **SSH into your server:**
```bash
ssh user@your-server-ip
```

2. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. **Clone repository:**
```bash
git clone your-repo-url
cd Flud
```

4. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configure CDS API:**
```bash
nano ~/.cdsapirc
# Add your CDS API credentials
```

6. **Create systemd service:**
```bash
sudo nano /etc/systemd/system/flud-backend.service
```

Add:
```ini
[Unit]
Description=FLUD Backend API
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/Flud/flood_model
Environment="PATH=/path/to/Flud/venv/bin"
ExecStart=/path/to/Flud/venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable flud-backend
sudo systemctl start flud-backend
```

8. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/flud-backend
```

Add:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

9. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/flud-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Frontend Setup

1. **Build frontend:**
```bash
cd frontend
npm install
npm run build
```

2. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/flud-frontend
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /path/to/Flud/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/flud-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Setup SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

---

## Environment Variables Summary

### Backend
- `CDS_API_URL`: CDS API endpoint (usually `https://cds.climate.copernicus.eu/api/v2`)
- `CDS_API_KEY`: Your CDS API key (format: `uid:key`)
- `PORT`: Server port (usually set by platform)

### Frontend
- `VITE_API_URL`: Backend API URL (e.g., `https://api.yourdomain.com`)

---

## Recommended Deployment Strategy

**For Quick Start:**
- **Railway** or **Render** (easiest, free tier available)

**For Production:**
- **Frontend:** Vercel or Netlify (excellent CDN, free SSL)
- **Backend:** Railway, Render, or DigitalOcean App Platform
- **Database (if needed later):** Supabase or Railway PostgreSQL

**For Full Control:**
- **VPS:** DigitalOcean, Linode, or AWS EC2
- **Container:** Docker on VPS or AWS ECS

---

## Troubleshooting

### Backend won't start
- Check CDS API credentials are set correctly
- Verify all dependencies are installed
- Check logs: `docker-compose logs backend` or platform logs

### Frontend can't connect to backend
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in `api_server.py`
- Ensure backend URL is accessible

### CDS API errors
- Verify `.cdsapirc` file exists (VPS) or environment variables are set (cloud)
- Check API key format: `uid:key`
- Ensure you've accepted terms on CDS website

---

## Security Notes

1. **Never commit API keys** to Git
2. **Use environment variables** for all secrets
3. **Enable HTTPS** in production
4. **Set up rate limiting** for API endpoints
5. **Use CORS** properly (already configured)
6. **Keep dependencies updated**

---

## LLM Integration (Optional)

### Current Status
The main application (`flood_predictor.py`) does **NOT** use Ollama or any LLM. The project will run normally when deployed to cloud platforms.

### If You Want to Add LLM Features

**Ollama won't work in cloud hosting** because:
- It requires local installation and runs on `localhost:11434`
- Most cloud platforms don't support local services
- It needs significant GPU/CPU resources

### Cloud-Based LLM Alternatives

If you want to add AI explanations or analysis, use cloud-based APIs:

#### Option 1: OpenAI API
```python
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)
```

#### Option 2: Anthropic (Claude) API
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": prompt}]
)
```

#### Option 3: Hugging Face Inference API
```python
import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}
response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
```

#### Option 4: Groq API (Fast & Free Tier)
```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)
```

### Environment Variables for LLM APIs
Add to your deployment platform:
- `OPENAI_API_KEY` (for OpenAI)
- `ANTHROPIC_API_KEY` (for Claude)
- `HF_API_KEY` (for Hugging Face)
- `GROQ_API_KEY` (for Groq)

### Recommendation
- **For production:** Use OpenAI or Anthropic (reliable, well-documented)
- **For cost-effective:** Use Groq or Hugging Face (free tiers available)
- **For local development:** Ollama is fine, but switch to cloud APIs for deployment
