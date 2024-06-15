
import os
import requests
import tinify
import logging
from PIL import Image

# Set your API keys
from apis import my_rmbg_key, tinify_key
tinify.key = tinify_key

# Configure logging
logging.basicConfig(filename='image_optimization.log', level=logging.INFO, format='%(message)s')

# Define the directories
input_directory = "collections"
output_directory = "New Collections"

# Create the output directory if it does not exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Function to get image size
def get_image_size(filepath):
    return os.path.getsize(filepath)

# Function to get image dimensions
def get_image_dimensions(filepath):
    with Image.open(filepath) as img:
        return img.size  # returns (width, height)

# Function to format the size
def format_size(size_in_bytes):
    if size_in_bytes < 1024 * 1024:  # Less than 1 MB
        return f"{size_in_bytes / 1024:.2f} KB"
    else:  # 1 MB or larger
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

# Initialize total sizes
total_original_size = 0
total_new_size = 0

# Iterate over all files in the input directory
total_images_optimized = 0

for filename in os.listdir(input_directory):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        input_filepath = os.path.join(input_directory, filename)

        # Remove background using remove.bg API
        with open(input_filepath, 'rb') as img_file:
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': img_file},
                data={'size': 'auto'},
                headers={'X-Api-Key': my_rmbg_key},
            )

        if response.status_code == requests.codes.ok:
            with open(input_filepath, 'wb') as out_file:
                out_file.write(response.content)
        else:
            logging.error(f"Error: {response.status_code}, {response.text}")
            continue
    elif filename.lower().endswith('.webp'):
        logging.info("=======================================================================================")
        logging.info(f'The image in a web format that is not acceptable by removing background API: {filename}')
        logging.info("=======================================================================================\n")
        continue

    # Compress, crop, and resize using TinyPNG API
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        input_filepath = os.path.join(input_directory, filename)

        # Get original image dimensions and size
        original_size = get_image_size(input_filepath)
        original_dimensions = get_image_dimensions(input_filepath)

        # Load the image file from disk and compress
        source = tinify.from_file(input_filepath)

        # Resize the image to 500x500 pixels
        resized = source.resize(
            method="thumb",
            width=500,
            height=500
        )

        # Convert the image to WebP format if not already
        if not filename.lower().endswith('.webp'):
            converted = resized.convert(type=["image/webp"])
            filename = os.path.splitext(filename)[0] + ".webp"
            output_filepath = os.path.join(output_directory, filename)
            converted.to_file(output_filepath)
        else:
            output_filepath = os.path.join(output_directory, filename)
            resized.to_file(output_filepath)

        # Get new image dimensions and size
        new_size = get_image_size(output_filepath)
        new_dimensions = get_image_dimensions(output_filepath)

        # Accumulate the sizes
        total_original_size += original_size
        total_new_size += new_size

        # Log the details with formatted size
        logging.info("=======================================================================================")
        logging.info(f'Image: {filename}')
        logging.info(f'Original Dimensions: {original_dimensions}')
        logging.info(f'New Dimensions: {new_dimensions}')
        logging.info(f'Original Size: {format_size(original_size)}')
        logging.info(f'New Size: {format_size(new_size)}')
        logging.info("=======================================================================================\n")

        total_images_optimized += 1

# Log total number of images optimized
logging.info(f'Total images optimized: {total_images_optimized}')
logging.info(f'Total size of all images: {format_size(total_original_size)}')
logging.info(f'Compressed size of all images: {format_size(total_new_size)}')

