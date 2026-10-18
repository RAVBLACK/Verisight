import json
import os
import torch
import numpy as np
import onnxruntime as ort
import detector
from huggingface_hub import hf_hub_download

def export():
    print("Loading PyTorch model...")
    detector.load_detector()
    
    checkpoint_path = hf_hub_download(repo_id=detector.MODEL_ID, filename="checkpoint_full.pth")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    
    img_size = checkpoint["img_size"]
    class_names = checkpoint["class_names"]
    normalize_mean = checkpoint["normalize_mean"]
    normalize_std = checkpoint["normalize_std"]
    
    artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "artifacts"))
    os.makedirs(artifacts_dir, exist_ok=True)
    
    onnx_path = os.path.join(artifacts_dir, "model.onnx")
    config_path = os.path.join(artifacts_dir, "model_config.json")
    
    print(f"Exporting to ONNX at: {onnx_path}")
    dummy_input = torch.randn(1, 3, img_size, img_size, dtype=torch.float32)
    
    model = detector._model
    model.eval()
    
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        dynamo=False
    )
    
    size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    print(f"ONNX export completed! File size: {size_mb:.2f} MB")
    
    config = {
        "model_id": detector.MODEL_ID,
        "img_size": img_size,
        "class_names": class_names,
        "ai_index": detector._ai_index,
        "normalize_mean": normalize_mean,
        "normalize_std": normalize_std,
    }
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"Saved config to {config_path}")
    
    # Verification: Compare PyTorch vs ONNX Runtime output
    print("Verifying ONNX vs PyTorch output...")
    test_tensor = torch.randn(1, 3, img_size, img_size)
    with torch.no_grad():
        pytorch_out = model(test_tensor).numpy()
        
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    onnx_out = session.run(["output"], {"input": test_tensor.numpy()})[0]
    
    max_diff = np.max(np.abs(pytorch_out - onnx_out))
    print(f"Maximum absolute difference between PyTorch and ONNX: {max_diff:.6f}")
    assert max_diff < 1e-4, f"Difference {max_diff} is too large!"
    print("Verification SUCCESSFUL! ONNX predictions match PyTorch perfectly.")

if __name__ == "__main__":
    export()
