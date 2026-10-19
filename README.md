# Verisight

**See beyond the pixels.**

Verisight is an AI-powered image authenticity analysis and digital image forensics platform. It estimates whether an uploaded image is likely to be AI-generated or an authentic photograph using deep-learning feature representations.

> **Research Preview & Disclaimer:** Verisight is an experimental research project. Probability scores reflect statistical model inferences and must not be interpreted as definitive or forensic proof of image authenticity.
>
> 📖 **Full System Architecture & Documentation**: See [PROJECT_DOCUMENTATION.md](file:///c:/Users/rakes/Downloads/imgai/PROJECT_DOCUMENTATION.md) for in-depth problem background, neural architecture, security protections, and the complete future research roadmap.

---

## Capabilities & Architecture Overview

Verisight is architected for both **local high-throughput research** and **instant, zero-config serverless cloud deployment**:

- **Dual-Engine Architecture**:
  - **Local Development / Research**: Runs FastAPI with PyTorch & Torchvision (`backend/main.py`), supporting GPU acceleration and research experiments.
  - **Cloud / Vercel Serverless**: Runs FastAPI with ONNX Runtime (`api/index.py`), converting EfficientNet-B0 into an optimized 15.3 MB ONNX model. The entire serverless bundle is under 50 MB (far below Vercel's 250 MB limit) and boots in milliseconds without cold-start timeouts.
- **Image Support**: Accepts JPG, PNG, and WebP images up to 10 MB and 25 million pixels.
- **Categorization**: Classifies images into `Likely AI-generated`, `Likely real`, or `Uncertain` with calibrated probability scores.
- **Research Aesthetic**: Polished, responsive React interface styled with a restrained digital-forensics research aesthetic, accessible progress bars, and transparent model disclaimers.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Vite, JavaScript, CSS Design Tokens, `lucide-react` |
| **Serverless Cloud (Vercel)** | Python 3.10+, FastAPI, ONNX Runtime (`onnxruntime`), NumPy, Pillow |
| **Local Backend & Research** | Python 3.10+, FastAPI, Uvicorn, PyTorch, Torchvision, Hugging Face Hub |
| **Model** | EfficientNet-B0 fine-tuned for AI-vs-Real image classification |
| **Deployment & Hosting** | Vercel (Frontend + Serverless Functions via `vercel.json`) |

---

## Project Structure

```
imgai/ (real-or-ai)
├── api/                       # Vercel Serverless Function Backend
│   ├── index.py               # Serverless ASGI FastAPI entrypoint
│   ├── detector_onnx.py       # Pure ONNX Runtime + Pillow inference engine
│   ├── model.onnx             # Optimized EfficientNet-B0 ONNX model (15.3 MB)
│   ├── model_config.json      # Normalization parameters & class indices
│   └── requirements.txt       # Lightweight serverless dependencies (<50MB)
├── frontend/                  # React + Vite application
│   ├── public/
│   │   └── favicon.svg        # Branded vector favicon
│   ├── src/
│   │   ├── App.jsx            # Core UI, drag-and-drop, API integration
│   │   ├── App.css            # Component styles & animations
│   │   ├── index.css          # Design system & theme tokens
│   │   └── main.jsx           # React DOM root
│   ├── .env.example           # Example frontend environment variables
│   ├── index.html             # HTML5 document shell with SEO meta tags
│   └── package.json           # Frontend dependencies
├── backend/                   # Local PyTorch Backend & Research Services
│   ├── main.py                # Local FastAPI app
│   ├── detector.py            # Local PyTorch inference module
│   ├── export_onnx.py         # Utility to export PyTorch checkpoint to ONNX
│   ├── requirements.txt       # PyTorch & local dependencies
│   └── .env.example           # Example backend environment variables
├── artifacts/                 # Model artifacts & configuration
├── experiments/               # Future research experiment logs & benchmarks
├── notebooks/                 # Google Colab / Jupyter research notebooks
├── .gitignore                 # Comprehensive rules guarding secrets & dependencies
├── package.json               # Root scripts for monorepo build orchestration
├── vercel.json                # Vercel routing & serverless rewrites
└── README.md                  # Project documentation
```

---

## Deployment to Vercel (Serverless)

Verisight is pre-configured for automated deployment to Vercel as a full-stack serverless application:

### Step 1: Push Repository to GitHub
Ensure all changes are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure Verisight full-stack Vercel serverless deployment"
git push origin main
```

### Step 2: Import into Vercel
1. Go to [Vercel Dashboard](https://vercel.com/new).
2. Click **Add New** > **Project** and select your GitHub repository.
3. Keep default settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `./` (leave blank / root)
   - **Build Command**: `cd frontend && npm install && npm run build` (configured automatically via `vercel.json`)
   - **Output Directory**: `frontend/dist`
4. Click **Deploy**.

Vercel will automatically build the React frontend and deploy `api/index.py` as an on-demand serverless function. All `/analyze` and `/health` requests are seamlessly routed to the serverless Python backend.

---

## Local Development Setup

### 1. Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: v3.10, v3.11, or v3.12 (with `venv`)

### 2. Backend (Local PyTorch)
```powershell
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start local backend on port 8000
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- Health Check: `http://127.0.0.1:8000/health`
- Interactive API Docs: `http://127.0.0.1:8000/docs`

### 3. Frontend (React + Vite)
```powershell
cd frontend

# Install dependencies
npm install

# Start local development server
npm run dev
```
The frontend will open at `http://localhost:5173`.

---

## Environment Variables

| Variable | Environment | Default | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | Frontend (`.env`) | `""` (prod) / `http://127.0.0.1:8000` (dev) | Target API URL. On Vercel, defaults to same-origin. |
| `FRONTEND_ORIGIN` | Backend (`.env`) | `http://localhost:5173` | Allowed CORS origin for local development. |

---

## API Specification

### `GET /health`
Returns service availability status.
```json
{
  "status": "ok",
  "engine": "onnxruntime"
}
```

### `POST /analyze`
Accepts multipart form-data image upload.
- **Form Field**: `file`
- **Supported Formats**: `image/jpeg`, `image/png`, `image/webp`
- **Max File Size**: 10 MB

#### Response:
```json
{
  "verdict": "Likely AI-generated",
  "ai_probability": 0.7812,
  "real_probability": 0.2188,
  "model": "bsgcasa/ai-vs-real-image-detector",
  "device": "cpu (onnx)",
  "disclaimer": "This is a model prediction, not proof of an image's origin."
}
```

---

## Security & Git Hygiene

The root `.gitignore` strictly protects the repository against accidental leaks:
- **No secrets or environment files**: `.env`, `.env.*`, `*.pem`, `*.key`, and API tokens are ignored.
- **No package dependencies**: `node_modules/`, `**/.venv/`, and `**/venv/` are excluded.
- **No raw checkpoints or caches**: `*.pth`, `*.pt`, `huggingface/`, and `.cache/` are ignored. Only the optimized production `api/model.onnx` is tracked for serverless execution.

---

## Research Roadmap & Future Directions

1. **Spatial-Frequency Fusion (Radial FFT)**: Integrating frequency domain feature analysis to detect generator-specific high-frequency artifacts under image compression.
2. **Adversarial & Compression Robustness**: Evaluating detection performance across diverse JPEG quality factors (Q=50 to Q=95) and downsampling regimes.
3. **Multi-Generator Benchmark**: Testing out-of-distribution generalization across Midjourney v6, Stable Diffusion 3, Flux, and DALL-E 3.

---

## License & Attribution

Research prototype developed under the Verisight experimental image forensics initiative. Baseline weights derived from `bsgcasa/ai-vs-real-image-detector`.
