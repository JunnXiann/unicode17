import os
from PIL import Image
from tqdm import tqdm


def resize_images_to_new_folder(
    base_dir="./unicode", output_dir="./unicode_150", target_height=150
):
    """
    Finds all JPG images in base_dir, scales them proportionally to target_height,
    and saves them in output_dir while maintaining the original folder structure.
    """
    # 1. Collect all image paths recursively
    image_paths = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg")):
                image_paths.append(os.path.join(root, file))

    if not image_paths:
        print(f"No JPG images found in '{base_dir}'. Please check the path.")
        return

    print(
        f"Found {len(image_paths)} images. Saving resized images to '{output_dir}'..."
    )

    # 2. Iterate and resize with a progress bar
    for img_path in tqdm(image_paths, desc="Resizing images"):
        try:
            # Calculate the relative path to maintain folder structure
            # e.g., if img_path is "./unicode/U4E00/1/char.jpg"
            # rel_path becomes "U4E00/1/char.jpg"
            rel_path = os.path.relpath(img_path, base_dir)

            # Construct the exact new path inside the output directory
            out_path = os.path.join(output_dir, rel_path)

            # Ensure the specific destination sub-folder exists before saving
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            # Open the original image
            with Image.open(img_path) as img:
                w, h = img.size

                # Calculate the new width to maintain aspect ratio (按比例缩放)
                ratio = target_height / float(h)
                new_w = int(float(w) * float(ratio))

                # Resize using high-quality LANCZOS filter
                resized_img = img.resize(
                    (new_w, target_height), Image.Resampling.LANCZOS
                )

                # Save to the NEW folder (leaves original untouched)
                resized_img.save(out_path)

        except Exception as e:
            print(f"\nFailed to process {img_path}: {e}")

    print(f"Done! All resized images are safely stored in '{output_dir}'.")


if __name__ == "__main__":
    # You can change these paths if your folders are located elsewhere
    resize_images_to_new_folder(
        base_dir="./unicode", output_dir="./unicode_150", target_height=150
    )
