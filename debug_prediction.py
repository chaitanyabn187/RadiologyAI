import os

import torch
import torchxrayvision as xrv


def main() -> int:
    image_path = input(
        "Enter the full path of your chest X-ray: "
    ).strip().strip('"')

    if not os.path.isfile(image_path):
        print(f"ERROR: Image file not found: {image_path}")
        return 1

    try:
        model = xrv.models.DenseNet(weights="densenet121-res224-all")
        model.eval()

        image = xrv.utils.load_image(image_path)
        image = xrv.datasets.XRayCenterCrop()(image)
        image = xrv.datasets.XRayResizer(224)(image)
        image_tensor = torch.from_numpy(image).unsqueeze(0).float()

        with torch.no_grad():
            features = model.features2(image_tensor)
            raw_outputs = model.classifier(features)
            sigmoid_outputs = torch.sigmoid(raw_outputs)
            final_outputs = model(image_tensor)

        print("\nFinding                 Raw logit   Sigmoid   Final output")
        print("-" * 65)

        for name, raw, sigmoid, final in zip(
            model.pathologies,
            raw_outputs[0],
            sigmoid_outputs[0],
            final_outputs[0],
        ):
            print(
                f"{name:25} "
                f"{raw.item():9.4f} "
                f"{sigmoid.item():9.4f} "
                f"{final.item():12.4f}"
            )

        print("\nThese outputs are experimental, not medical diagnoses.")
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"\nERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())