# Virtual Try-On with Azure OpenAI GPT-Image-1

Generate professional fashion photography by combining multiple clothing items using Azure OpenAI's GPT-Image-1 Image Edit API.

## Features

- **Dynamic Image Loading**: Automatically discovers all clothing item images in a folder
- **Smart Prompt Generation**: Creates prompts based on image filenames (e.g., `skirt.jpg` → extracts only the skirt)
- **Professional Output**: Generates high-quality e-commerce style fashion photos
- **Multiple Input Support**: Combines multiple clothing items into a single outfit using the Image Edit API

## Prerequisites

### Azure Resources
- Azure subscription
- **Azure OpenAI resource** with GPT-Image-1 model deployed

### Local Environment
- Python 3.10+
- Azure CLI installed and authenticated (`az login`)

### Required Python Packages
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/SyChell/VirtualTryOn.git
cd VirtualTryOn
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and fill in your Azure details:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Azure OpenAI Configuration
AOAI_API_BASE=https://your-resource.cognitiveservices.azure.com
AOAI_DEPLOYMENT_NAME=gpt-image-1
AOAI_API_VERSION=2025-04-01-preview

# Image Configuration
IMAGES_FOLDER=./images
```

### 3. Authenticate to Azure

```bash
az login
```

### 4. Add Clothing Images

Place your clothing item images in the `images/` folder (or your configured `IMAGES_FOLDER`):
- Name each image after the clothing item: `cap.jpg`, `jeans.jpg`, `sneakers.jpg`, `t-shirt.png`
- Supported formats: `.jpg`, `.jpeg`, `.png`

### 5. Run

```bash
python agent.py
```

## How It Works

The agent uses Azure OpenAI's **Image Edit API** (`/images/edits`) which accepts multiple input images. The API combines the clothing items from each input image into a single generated outfit.

**Pipeline:**
1. Scans `IMAGES_FOLDER` for clothing images
2. Sends all images to the Image Edit API with a prompt
3. Saves the generated outfit to `generated_images/generated_outfit.jpeg`

## Project Structure

```
VirtualTryOn/
├── Main.ipynb          # Jupyter notebook for interactive development
├── agent.py            # Image processing pipeline
├── .env                # Environment configuration (not committed)
├── .env.example        # Example environment file
├── requirements.txt    # Python dependencies
├── images/             # Input clothing images
│   ├── cap.jpg
│   ├── jeans.jpg
│   ├── sneakers.jpg
│   └── t-shirt.jpg
├── generated_images/   # Output folder
│   └── generated_outfit.jpeg
└── README.md
```

## Example

**Input images:**
- `cap.jpg` - A baseball cap
- `jeans.jpg` - Blue jeans
- `sneakers.jpg` - White sneakers
- `t-shirt.jpg` - A casual t-shirt

**Output:** Professional fashion photo of a model wearing all four items as a complete outfit.

## Troubleshooting

### "AOAI_API_BASE environment variable is required"
Make sure your `.env` file has the correct Azure OpenAI endpoint.

### Authentication errors
Run `az login` and ensure you're signed into the correct Azure subscription.

### Image generation fails
- Verify GPT-Image-1 is deployed in your Azure OpenAI resource
- Check that `AOAI_API_BASE` points to your Azure OpenAI endpoint

## License

MIT
