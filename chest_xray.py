import os
import torch
import torchxrayvision as xrv


def main() -> int:
    print("Loading RadiologyAI model...")

    try:
        model = xrv.models.DenseNet(weights="densenet121-res224-all")
        model.eval()

        image_path = input(
            "\nEnter the full path of your chest X-ray image: "
        ).strip().strip('"')

        if not os.path.isfile(image_path):
            print(f"ERROR: Image file not found: {image_path}")
            return 1

        image = xrv.utils.load_image(image_path)

        print("\nImage loaded successfully.")
        print("Image shape before preprocessing:", image.shape)
        print("Image minimum:", float(image.min()))
        print("Image maximum:", float(image.max()))

        image = xrv.datasets.XRayCenterCrop()(image)
        image = xrv.datasets.XRayResizer(224)(image)

        image_tensor = torch.from_numpy(image).unsqueeze(0).float()
        print("Input tensor shape:", tuple(image_tensor.shape))

        with torch.no_grad():
            output = model(image_tensor)

        print("\nMODEL OUTPUTS")
        print("-" * 50)

        for name, score in zip(model.pathologies, output[0]):
            print(f"{name}: {float(score):.6f}")

        print("\nTest completed.")
        print("These outputs are experimental and are not diagnoses.")
        return 0

    except (EOFError, OSError, RuntimeError, ValueError) as error:
        print(f"\nERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())