import os
import warnings

import numpy as np
import torch
import torchxrayvision as xrv


# ------------------------------------------
# 1. LOAD THE PRETRAINED CHEST X-RAY MODEL
# ------------------------------------------

print("Loading RadiologyAI chest X-ray model...")

chest_model = xrv.models.DenseNet(
    weights="densenet121-res224-all"
)

chest_model.eval()

# Use the same device as the model.
device = next(chest_model.parameters()).device

print("Chest X-ray model loaded successfully!")


# ------------------------------------------
# 2. IMAGE PREPROCESSING
# ------------------------------------------

center_crop = xrv.datasets.XRayCenterCrop()
resize = xrv.datasets.XRayResizer(224)


# ------------------------------------------
# 3. ANALYZE CHEST X-RAY
# ------------------------------------------

def analyze_xray(image_path, body_part="chest"):

    """
    Experimental chest X-ray analysis for an academic project.

    The model returns scores for its supported categories.
    These scores are not confirmed diagnoses or calibrated
    disease probabilities.

    This function must not be used for clinical decisions.
    """

    # Check whether the image exists.
    if not os.path.isfile(image_path):
        return {
            "success": False,
            "message": "The selected X-ray image could not be found.",
            "findings": []
        }

    # This model supports chest X-rays only.
    if not isinstance(body_part, str) or body_part.lower() != "chest":
        return {
            "success": False,
            "message": (
                "This model supports experimental chest X-ray "
                "analysis only. Other body parts are not supported."
            ),
            "findings": []
        }

    try:
        # ----------------------------------
        # Load the X-ray image.
        # ----------------------------------

        image = xrv.utils.load_image(image_path)

        if image is None or image.size == 0:
            raise ValueError("The image is empty or could not be loaded.")

        # ----------------------------------
        # Apply model preprocessing.
        # ----------------------------------

        image = center_crop(image)
        image = resize(image)

        # Convert the NumPy array to a PyTorch tensor.
        # Expected shape: (batch, channel, height, width).
        image_tensor = torch.from_numpy(
            np.asarray(image, dtype=np.float32)
        ).unsqueeze(0)

        image_tensor = image_tensor.to(device)

        # ----------------------------------
        # Run the model's standard inference.
        # ----------------------------------

        with torch.no_grad():
            predictions = chest_model(image_tensor)

        # Convert predictions to a NumPy array.
        scores = predictions[0].detach().cpu().numpy()

        # Verify that the model returned the expected output.
        if len(scores) != len(chest_model.pathologies):
            raise ValueError(
                "The number of predictions does not match "
                "the model's supported categories."
            )

        if not np.all(np.isfinite(scores)):
            raise ValueError(
                "The model returned invalid numerical scores."
            )

        # ----------------------------------
        # Prepare the findings.
        # ----------------------------------

        findings = []

        for name, score in zip(chest_model.pathologies, scores):
            findings.append({
                "name": str(name),
                "score": round(float(score), 6)
            })

        # Sort by model score, highest first.
        findings.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # ----------------------------------
        # Return the analysis.
        # ----------------------------------

        return {
            "success": True,
            "message": (
                "Experimental chest X-ray model output. "
                "Scores are model outputs, not confirmed diagnoses "
                "or calibrated disease probabilities. "
                "Professional medical interpretation is required."
            ),
            "findings": findings
        }

    except Exception as error:

        warnings.warn(
            f"Chest X-ray analysis failed: {error}"
        )

        return {
            "success": False,
            "message": (
                "X-ray analysis failed. Please check the image, "
                "preprocessing, and model configuration."
            ),
            "findings": []
        }


# ------------------------------------------
# 4. TEST THE MODEL
# ------------------------------------------

if __name__ == "__main__":

    print("\nRadiologyAI model information")
    print("--------------------------------")

    print("Model: DenseNet121")
    print("Weights: densenet121-res224-all")
    print("Number of output categories:", len(chest_model.pathologies))

    print("\nSupported categories:")

    for pathology in chest_model.pathologies:
        print("-", pathology)

    print("\nImportant:")
    print("These experimental outputs are not medical diagnoses.")
    print("The model has not been validated for clinical decisions.")