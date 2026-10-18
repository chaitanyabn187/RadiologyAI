import torch
import torchxrayvision as xrv

print("Loading model...")

model = xrv.models.DenseNet(weights="densenet121-res224-all")
model.eval()

print("\nModel loaded successfully!")
print("Number of findings:", len(model.pathologies))

print("\nTesting model output type...")

print("Output activation:", model.op_threshs if hasattr(model, "op_threshs") else "Not available")

print("\nChecking model output for a sample image...")

print("We need a real chest X-ray image to test the predictions.")
print("Use an existing sample X-ray from your project for the next test.")