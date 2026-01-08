"""
Virtual Try-On Agent
Simple image-in/image-out pipeline: takes clothing images, outputs combined outfit image.

Uses Azure OpenAI Image Edit API with multi-image support (REST API).

TODO: Transition to hosted agent in next iteration.
"""

import os
import base64
import glob
import requests
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()


def generate_outfit_image(image_paths: list[str], output_path: str) -> str:
    """
    Generates a combined outfit image from multiple clothing item images.
    
    Args:
        image_paths: List of paths to clothing item images
        output_path: Path to save the generated image
        
    Returns:
        Path to the generated image
    """
    if not image_paths:
        raise ValueError("No images provided")
    
    # Config
    api_base = os.environ.get("AOAI_API_BASE")
    deployment = os.environ.get("AOAI_DEPLOYMENT_NAME", "gpt-image-1")
    api_version = os.environ.get("AOAI_API_VERSION", "2025-04-01-preview")
    
    if not api_base:
        raise ValueError("AOAI_API_BASE environment variable is required")
    
    url = f"{api_base}/openai/deployments/{deployment}/images/edits?api-version={api_version}"
    
    # Auth
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default").token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Build prompt
    item_names = [os.path.splitext(os.path.basename(p))[0] for p in image_paths]
    prompt = f"""Create a professional fashion photo of a female model wearing: {", ".join(item_names)}

- Use ONLY the clothing items from the provided images
- Do not add any other items
- Clean white background, full body shot
"""
    
    print(f"🎨 Calling Image Edit API with {len(image_paths)} images...")
    
    # Multi-image upload
    files = []
    file_handles = []
    try:
        for img_path in image_paths:
            fh = open(img_path, "rb")
            file_handles.append(fh)
            files.append(("image[]", (os.path.basename(img_path), fh, "image/jpeg")))
        
        data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1536",
            "quality": "high"
        }
        
        response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        if result.get("data") and result["data"][0].get("b64_json"):
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(result["data"][0]["b64_json"]))
            return output_path
        
        raise ValueError("No image in response")
    finally:
        for fh in file_handles:
            fh.close()


def get_clothing_images(images_folder: str) -> list[str]:
    """
    Get all clothing images from the folder.
    
    Args:
        images_folder: Path to the folder containing clothing images
        
    Returns:
        List of image file paths
    """
    image_files = sorted(
        glob.glob(f"{images_folder}/*.jpg") + 
        glob.glob(f"{images_folder}/*.jpeg") + 
        glob.glob(f"{images_folder}/*.png")
    )
    # Filter out output/generated images
    image_files = [f for f in image_files if 'output' not in os.path.basename(f).lower() 
                   and 'generated' not in os.path.basename(f).lower()]
    
    return image_files


def run_virtual_tryon():
    """
    Run the Virtual Try-On pipeline.
    
    Input: Images from IMAGES_FOLDER
    Output: Generated outfit image saved to generated_images folder
    
    Returns:
        Path to the generated image
    """
    images_folder = os.environ.get("IMAGES_FOLDER", "./images")
    output_folder = "./generated_images"
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get input images
    print(f"📂 Input folder: {images_folder}")
    image_paths = get_clothing_images(images_folder)
    
    if not image_paths:
        print(f"❌ No clothing images found in {images_folder}")
        return None
    
    item_names = [os.path.splitext(os.path.basename(f))[0] for f in image_paths]
    print(f"📸 Input images: {', '.join(item_names)}")
    
    # Generate output
    output_path = os.path.join(output_folder, "generated_outfit.jpeg")
    
    print(f"\n🔄 Generating outfit...")
    result_path = generate_outfit_image(image_paths, output_path)
    
    print(f"\n✅ Output image: {os.path.abspath(result_path)}")
    return result_path


def main():
    """Main function - Run the Virtual Try-On pipeline"""
    print("="*60)
    print("👗 VIRTUAL TRY-ON AGENT")
    print("="*60 + "\n")
    run_virtual_tryon()


if __name__ == "__main__":
    main()
