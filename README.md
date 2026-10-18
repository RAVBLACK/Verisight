# Verisight

**See beyond the pixels.**

AI-powered image authenticity analysis. Verisight estimates whether an uploaded image may be AI-generated, using a pretrained deep-learning classifier.

> **Note:** This is a research preview. Model predictions are estimates, not definitive proof of an image's origin.

---

## Current Capabilities

- Upload JPG, PNG, or WebP images (up to 10 MB)
- Analyze images using a pretrained EfficientNet-B0 classifier
- View AI-generated vs. real probability scores
- Verdict categories: Likely AI-generated, Likely real, Uncertain
- Drag-and-drop or file-browse upload
- Clear error messages for invalid files

## Technology Stack

| Layer      | Technologies                                      |
| ---------- | ------------------------------------------------- |
| Frontend   | React, Vite, JavaScript, CSS, lucide-react        |
| Backend    | Python, FastAPI, Uvicorn, Pillow, PyTorch          |
| Model      | EfficientNet-B0 via Hugging Face Hub               |
| Research   | Google Colab, scikit-learn, NumPy, SciPy, pandas   |

## Project Structure

```
real-or-ai/
├── frontend/          # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx    # Main application component
│   │   ├── App.css    # Component styles
│   │   ├── index.css  # Design system
│   │   └── main.jsx   # Entry point
│   ├── .env           # Local environment variables
│   └── index.html     # HTML shell
├── backend/
│   ├── main.py        # FastAPI application
│   ├── detector.py    # Model loading and inference
│   └── requirements.txt
├── notebooks/         # Research notebooks
├── experiments/       # Experiment results
├── artifacts/         # Model artifacts
├── .gitignore
└── README.md
```

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The first request will download the model checkpoint from Hugging Face (~50 MB).

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend runs at `http://localhost:5173` by default.

## Environment Variables

### Frontend

| Variable             | Default                     | Description            |
| -------------------- | --------------------------- | ---------------------- |
| `VITE_API_BASE_URL`  | `http://127.0.0.1:8000`    | Backend API base URL   |

### Backend

| Variable           | Default                    | Description                  |
| ------------------ | -------------------------- | ---------------------------- |
| `FRONTEND_ORIGIN`  | `http://localhost:5173`    | Allowed CORS origin          |

## API Endpoints

| Method | Path       | Description                    |
| ------ | ---------- | ------------------------------ |
| GET    | `/`        | Service status                 |
| GET    | `/health`  | Health check                   |
| POST   | `/analyze` | Analyze an uploaded image      |

### POST /analyze

**Request:** `multipart/form-data` with field `file` (JPG, PNG, or WebP, max 10 MB)

**Response:**
```json
{
  "verdict": "Likely AI-generated",
  "ai_probability": 0.78,
  "real_probability": 0.22,
  "model": "bsgcasa/ai-vs-real-image-detector",
  "device": "cpu",
  "disclaimer": "This is a model prediction, not proof of an image's origin."
}
```

**Interactive docs:** `http://127.0.0.1:8000/docs`

## Research Roadmap

1. **Baseline evaluation** — Measure pretrained model performance on a held-out dataset
2. **Frequency-domain features** — Extract radial FFT features for complementary analysis
3. **Hybrid fusion** — Combine visual and frequency features via a lightweight classifier
4. **Robustness testing** — Evaluate under JPEG compression, resizing, and unseen generators
5. **Ablation studies** — Compare visual-only, frequency-only, and hybrid approaches

## Known Limitations

- The pretrained model may not generalize to all AI generators
- Predictions can be affected by JPEG compression, resizing, and image editing
- The model has not been independently calibrated or evaluated on a held-out test set
- Results should not be treated as forensic proof

## Deployment Notes

- Frontend and backend are independently deployable
- API URLs are configured via environment variables
- CORS origins must be updated for production domains
- Model checkpoint is downloaded at startup; ensure network access or pre-cache the file
- Do not commit `.env` files, model weights, or datasets to Git

---

**Verisight** — Experimental image forensics research project.
