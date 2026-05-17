import json
import os

from PIL import Image

ORIGIN_DIR = "images"
DESTINATION_DIR = "public"
IMAGES_JSON = "public\\images.json"


with open(IMAGES_JSON) as f:
    global alt
    alt = json.load(f)


def processImage(filepath, id):

    im = Image.open(filepath)

    print("  opened image")

    IMG_WIDTH, IMG_HEIGHT = im.size

    DESIRED_SIZES = [200, 600, 1200]

    if IMG_WIDTH not in DESIRED_SIZES:
        DESIRED_SIZES.append(IMG_WIDTH)

    # Filter image sizes that are bigger than the original image itself
    DESIRED_SIZES = [size for size in DESIRED_SIZES if size <= IMG_WIDTH]

    DIR, ORIGINAL = os.path.split(filepath)

    for target_width in DESIRED_SIZES:
        print(f"  doing desired size {target_width}")

        # We don't need to make images with sizes bigger than the original image
        if target_width > IMG_WIDTH:
            continue

        print("  downscaling image")

        target_height = round(IMG_HEIGHT * target_width / IMG_WIDTH)
        downscaled = im.resize((target_width, target_height))

        print("  image downscaled, going to save it")

        filename = (
            f"{id}-{target_width}.webp" if target_width != IMG_WIDTH else f"{id}.webp"
        )

        DESTINATION_FILEPATH = os.path.join(os.path.relpath(DIR, ORIGIN_DIR), filename)

        SPEED_TRADEOFF = 6  # see https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp:~:text=method,-Quality
        downscaled.save(
            os.path.join(DESTINATION_DIR, DESTINATION_FILEPATH),
            format="webp",
            quality=80,
            method=SPEED_TRADEOFF,
        )

        print("  image saved! appending alternative...")

    # Add alt text using a simple image recognition model
    # using generateAlttext.py
    alt_text = ""

    # Insert newly converted image to our dictionary of tracked images
    # for the custom front-end image component (images.json)
    global alt
    alt.append(
        {
            "id": id,
            "dir": os.path.relpath(DIR, ORIGIN_DIR),
            "original": ORIGINAL,
            "alt": alt_text,
            "width": IMG_WIDTH,
            "height": IMG_HEIGHT,
            "sizes": DESIRED_SIZES,
        }
    )

    return None


for root, dirs, files in os.walk(ORIGIN_DIR):
    print("Directory:", root)

    for d in dirs:
        print("  Dir :", os.path.join(root, d))
        dest_dir = os.path.join(DESTINATION_DIR, d)
        os.makedirs(dest_dir, exist_ok=True)

    for f in files:
        currentDir = root
        currentFilePath = os.path.join(root, f)

        print(f"Looking at file {currentFilePath}")

        # Check if the file is an image
        if os.path.splitext(currentFilePath)[1] not in [
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        ]:
            print(f"File {currentFilePath} is not an image")
            continue

        # Check if the image has already been processed
        sameFile = f in [img["original"] for img in alt]
        sameDir = currentDir in [img["dir"] for img in alt]
        if sameFile and sameDir:
            print("  skipping file, already converted")
            continue

        print("  file is an image I want to convert! Processing...")

        # Calculate the new img's id
        imgs_in_same_dir = [img for img in alt if img["dir"] == currentDir]
        id = 1 + max([img["id"] for img in imgs_in_same_dir] + [0])

        processImage(currentFilePath, id)
else:
    with open(IMAGES_JSON, mode="w") as f:
        print(f"Going to write to {IMAGES_JSON}")
        json.dump(alt, f, indent=4)
