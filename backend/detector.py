import torch
import torch.nn as nn
import torch.nn.functional as F

from PIL import Image
from torchvision import models, transforms
from huggingface_hub import hf_hub_download

MODEL_ID = "bsgcasa/ai-vs-real-image-detector"

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = None
_preprocess = None
_ai_index = None


def load_detector():
    global _model, _preprocess, _ai_index

    if _model is not None:
        return

    checkpoint_path = hf_hub_download(
        repo_id=MODEL_ID,
        filename="checkpoint_full.pth",
    )

    # Only load checkpoints from a repository you trust.
    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    class_names = checkpoint["class_names"]
    image_size = checkpoint["img_size"]

    ai_indices = [
        i for i, name in enumerate(class_names)
        if "ai" in name.lower() or "generated" in name.lower()
    ]

    if len(ai_indices) != 1:
        raise RuntimeError(
            f"Could not identify the AI class in: {class_names}"
        )

    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features

    model.classifier = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(in_features, len(class_names)),
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(_device)
    model.eval()

    _preprocess = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            checkpoint["normalize_mean"],
            checkpoint["normalize_std"],
        ),
    ])

    _model = model
    _ai_index = ai_indices[0]


@torch.inference_mode()
def analyze_image(image: Image.Image) -> dict:
    load_detector()

    image = image.convert("RGB")
    tensor = _preprocess(image).unsqueeze(0).to(_device)

    probabilities = F.softmax(_model(tensor), dim=1)[0]
    ai_score = float(probabilities[_ai_index].cpu().item())

    if ai_score >= 0.60:
        verdict = "Likely AI-generated"
    elif ai_score <= 0.40:
        verdict = "Likely real"
    else:
        verdict = "Uncertain"

    return {
        "verdict": verdict,
        "ai_probability": round(ai_score, 4),
        "real_probability": round(1 - ai_score, 4),
        "model": MODEL_ID,
        "device": _device,
        "disclaimer": (
            "This is a model prediction, not proof of an image's origin."
        ),
    }
