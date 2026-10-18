import json
import os
import numpy as np
from PIL import Image
import onnxruntime as ort

_session = None
_config = None

def get_config():
    global _config
    if _config is not None:
        return _config
        
    candidates = [
        os.path.join(os.path.dirname(__file__), "model_config.json"),
        os.path.join(os.path.dirname(__file__), "..", "artifacts", "model_config.json"),
    ]
    
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _config = json.load(f)
            return _config
            
    raise FileNotFoundError("Could not find model_config.json in api/ or artifacts/")

def get_session():
    global _session
    if _session is not None:
        return _session
        
    candidates = [
        os.path.join(os.path.dirname(__file__), "model.onnx"),
        os.path.join(os.path.dirname(__file__), "..", "artifacts", "model.onnx"),
    ]
    
    model_path = None
    for path in candidates:
        if os.path.exists(path):
            model_path = path
            break
            
    if model_path is None:
        raise FileNotFoundError("Could not find model.onnx in api/ or artifacts/")
        
    # Set thread options for serverless efficiency
    sess_options = ort.SessionOptions()
    sess_options.intra_op_num_threads = 1
    sess_options.inter_op_num_threads = 1
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    
    _session = ort.InferenceSession(
        model_path,
        sess_options=sess_options,
        providers=["CPUExecutionProvider"]
    )
    return _session

def analyze_image_onnx(image: Image.Image) -> dict:
    config = get_config()
    session = get_session()
    
    img_size = config["img_size"]
    mean = np.array(config["normalize_mean"], dtype=np.float32).reshape(1, 3, 1, 1)
    std = np.array(config["normalize_std"], dtype=np.float32).reshape(1, 3, 1, 1)
    ai_index = config["ai_index"]
    
    # 1. Convert to RGB and resize using bilinear filter matching PyTorch torchvision
    image = image.convert("RGB")
    resized = image.resize((img_size, img_size), Image.Resampling.BILINEAR)
    
    # 2. Convert to float tensor and normalize
    arr = np.array(resized, dtype=np.float32) / 255.0  # (H, W, C)
    arr = np.transpose(arr, (2, 0, 1))  # (C, H, W)
    tensor = np.expand_dims(arr, 0)  # (1, C, H, W)
    tensor = (tensor - mean) / std
    
    # 3. Run ONNX inference
    logits = session.run(["output"], {"input": tensor})[0]
    
    # 4. Numerically stable softmax
    exp = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probabilities = exp / np.sum(exp, axis=1, keepdims=True)
    ai_score = float(probabilities[0, ai_index])
    
    # 5. Verdict thresholds matching original detector
    if ai_score >= 0.60:
        verdict = "Likely AI-generated"
    elif ai_score <= 0.40:
        verdict = "Likely real"
    else:
        verdict = "Uncertain"
        
    return {
        "verdict": verdict,
        "ai_probability": round(ai_score, 4),
        "real_probability": round(1.0 - ai_score, 4),
        "model": config.get("model_id", "bsgcasa/ai-vs-real-image-detector"),
        "device": "cpu (onnx)",
        "disclaimer": "This is a model prediction, not proof of an image's origin."
    }
