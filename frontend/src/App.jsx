import { useState, useRef, useCallback, useEffect } from 'react';
import {
  Upload,
  Search,
  X,
  AlertCircle,
  Info,
  ShieldCheck,
  ShieldAlert,
  HelpCircle,
  RotateCcw,
  FileImage,
} from 'lucide-react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const ALLOWED_EXTENSIONS = '.jpg, .jpeg, .png, .webp';

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function VerdictIcon({ verdict }) {
  if (verdict === 'Likely AI-generated') return <ShieldAlert size={20} />;
  if (verdict === 'Likely real') return <ShieldCheck size={20} />;
  return <HelpCircle size={20} />;
}

function verdictClass(verdict) {
  if (verdict === 'Likely AI-generated') return 'verdict-ai';
  if (verdict === 'Likely real') return 'verdict-real';
  return 'verdict-uncertain';
}

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const inputRef = useRef(null);

  // Clean up object URL on unmount or file change
  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const validateFile = useCallback((f) => {
    if (!f) return 'No file selected.';
    if (!ALLOWED_TYPES.includes(f.type)) {
      return `Unsupported format. Please upload a JPG, PNG, or WebP image.`;
    }
    if (f.size > MAX_SIZE_BYTES) {
      return `File is too large (${formatFileSize(f.size)}). Maximum size is ${MAX_SIZE_MB} MB.`;
    }
    return null;
  }, []);

  const handleFile = useCallback(
    (f) => {
      setError(null);
      setResult(null);

      const validationError = validateFile(f);
      if (validationError) {
        setError(validationError);
        setFile(null);
        if (preview) URL.revokeObjectURL(preview);
        setPreview(null);
        return;
      }

      if (preview) URL.revokeObjectURL(preview);
      setFile(f);
      setPreview(URL.createObjectURL(f));
    },
    [preview, validateFile],
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      const dropped = e.dataTransfer?.files?.[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile],
  );

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleInputChange = useCallback(
    (e) => {
      const selected = e.target.files?.[0];
      if (selected) handleFile(selected);
      // Reset input value so re-selecting the same file triggers onChange
      e.target.value = '';
    },
    [handleFile],
  );

  const handleClear = useCallback(() => {
    setFile(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    setError(null);
    setResult(null);
    setLoading(false);
  }, [preview]);

  const handleAnalyze = useCallback(async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => null);
        const message =
          errBody?.detail || `Server error (${response.status}). Please try again.`;
        throw new Error(message);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  }, [file]);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <div className="header-wordmark">Verisight</div>
          <div className="header-label">Experimental Image Forensics</div>
        </div>
        <div className="header-badge">
          <Search size={14} />
          Research Preview
        </div>
      </header>

      {/* Hero */}
      <section className="hero">
        <h1>Can you trust what you see?</h1>
        <p>
          Upload an image and Verisight will estimate whether it may be
          AI-generated, using a pretrained deep-learning classifier. Results are
          model predictions, not definitive proof.
        </p>
      </section>

      {/* Upload */}
      {!file && !result && (
        <section className="upload-section">
          <div
            className={`upload-zone ${dragActive ? 'drag-active' : ''} ${error ? 'has-error' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            aria-label="Upload image for analysis"
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                inputRef.current?.click();
              }
            }}
          >
            <input
              ref={inputRef}
              type="file"
              accept={ALLOWED_EXTENSIONS}
              onChange={handleInputChange}
              aria-hidden="true"
              tabIndex={-1}
            />
            <div className="upload-icon-wrapper">
              <Upload />
            </div>
            <p className="upload-text-primary">
              Drag and drop an image, or <span>browse files</span>
            </p>
            <p className="upload-text-secondary">
              JPG, PNG, or WebP up to {MAX_SIZE_MB} MB
            </p>
          </div>

          {error && (
            <div className="error-banner" role="alert">
              <AlertCircle />
              <p>{error}</p>
            </div>
          )}
        </section>
      )}

      {/* Preview */}
      {file && preview && !loading && !result && (
        <>
          <section className="preview-section">
            <div className="preview-card">
              <div className="preview-image-wrapper">
                <img src={preview} alt="Selected image preview" />
              </div>
              <div className="preview-info">
                <div>
                  <span className="preview-filename">{file.name}</span>
                  <span className="preview-filesize">
                    {formatFileSize(file.size)}
                  </span>
                </div>
                <div className="preview-actions">
                  <button
                    className="btn-icon"
                    onClick={handleClear}
                    title="Remove image"
                    aria-label="Remove image"
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>
            </div>
          </section>

          <div className="actions-bar">
            <button
              className="btn btn-primary btn-lg"
              onClick={handleAnalyze}
              id="analyze-button"
            >
              <Search size={18} />
              Analyze Image
            </button>
            <button className="btn btn-secondary btn-lg" onClick={handleClear}>
              <RotateCcw size={16} />
              Clear
            </button>
          </div>

          {error && (
            <div className="error-banner" role="alert">
              <AlertCircle />
              <p>{error}</p>
            </div>
          )}
        </>
      )}

      {/* Loading */}
      {loading && (
        <section className="loading-section">
          <div className="loading-card">
            <div className="loading-spinner" />
            <p className="loading-text">Analyzing image</p>
            <p className="loading-subtext">
              Running inference through the detector model...
            </p>
          </div>
        </section>
      )}

      {/* Results */}
      {result && (
        <section className="results-section">
          {/* Keep the preview visible */}
          {preview && (
            <div className="preview-card" style={{ marginBottom: 20 }}>
              <div className="preview-image-wrapper">
                <img src={preview} alt="Analyzed image" />
              </div>
            </div>
          )}

          <div className="results-card">
            <div className="results-header">
              <FileImage size={20} />
              <h3>Analysis Results</h3>
            </div>

            {/* Verdict */}
            <div className="verdict-section">
              <div className={`verdict-badge ${verdictClass(result.verdict)}`}>
                <VerdictIcon verdict={result.verdict} />
                {result.verdict}
              </div>
            </div>

            {/* Probabilities */}
            <div className="probabilities">
              <div className="prob-row">
                <div className="prob-label-row">
                  <span className="prob-label">AI-Generated Probability</span>
                  <span className="prob-value ai">
                    {(result.ai_probability * 100).toFixed(1)}%
                  </span>
                </div>
                <div
                  className="prob-bar-track"
                  role="progressbar"
                  aria-valuenow={Math.round(result.ai_probability * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label="AI-generated probability"
                >
                  <div
                    className="prob-bar-fill ai"
                    style={{ width: `${result.ai_probability * 100}%` }}
                  />
                </div>
              </div>

              <div className="prob-row">
                <div className="prob-label-row">
                  <span className="prob-label">Real Probability</span>
                  <span className="prob-value real">
                    {(result.real_probability * 100).toFixed(1)}%
                  </span>
                </div>
                <div
                  className="prob-bar-track"
                  role="progressbar"
                  aria-valuenow={Math.round(result.real_probability * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label="Real probability"
                >
                  <div
                    className="prob-bar-fill real"
                    style={{ width: `${result.real_probability * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="disclaimer">
              <Info size={16} />
              <p>{result.disclaimer}</p>
            </div>

            {/* Model meta */}
            <div className="model-meta">
              <div className="meta-item">
                <span className="meta-label">Model</span>
                <span className="meta-value">{result.model}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Device</span>
                <span className="meta-value">{result.device}</span>
              </div>
            </div>
          </div>

          {/* Reset */}
          <div className="actions-bar">
            <button
              className="btn btn-primary btn-lg"
              onClick={handleClear}
              id="reset-button"
            >
              <RotateCcw size={16} />
              Analyze Another Image
            </button>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="footer">
        <p>Verisight — See beyond the pixels.</p>
        <p>AI-powered image authenticity analysis. Research preview.</p>
      </footer>
    </div>
  );
}

export default App;
