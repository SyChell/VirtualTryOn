# Virtual Try-On with Azure OpenAI GPT-Image-1

Generate professional fashion photography by combining multiple clothing items using Azure OpenAI's GPT-Image-1 model.

## Features

- **Dynamic Image Loading**: Automatically discovers all clothing item images in a folder
- **Smart Prompt Generation**: Creates prompts based on image filenames (e.g., `skirt.jpg` → extracts only the skirt)
- **Professional Output**: Generates high-quality e-commerce style fashion photos
- **Multiple Input Support**: Combines multiple clothing items into a single outfit

## Prerequisites

- Azure subscription with access to Azure OpenAI
- GPT-Image-1 model deployed in Azure AI Foundry
- Python 3.8+
- Azure CLI authenticated (`az login`)

## Quick Start with GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SyChell/VirtualTryOn)

1. Click the button above to open in Codespaces
2. Wait for the environment to build
3. Authenticate to Azure: `az login --use-device-code`
4. Update the `AOAI_API_BASE` in the notebook with your Azure OpenAI endpoint
5. Run the notebook!

## Local Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Place your clothing item images in the `images/` folder
2. Name each image after the clothing item (e.g., `pullover.jpg`, `skirt.jpg`, `boots.jpg`)
3. Run the Jupyter notebook `Main.ipynb`

## Configuration

Update the following variables in the notebook:

```python
IMAGES_FOLDER = "./images"  # Folder containing clothing item images
AOAI_API_BASE = "https://your-resource.cognitiveservices.azure.com"
AOAI_DEPLOYMENT_NAME = "gpt-image-1"
```

## How It Works

1. Scans the images folder for clothing item images
2. Builds a dynamic prompt based on filenames
3. Sends all images to Azure OpenAI GPT-Image-1 API
4. Generates a combined outfit image with a model wearing all items

## Example

Input images:
- `pullover.jpg` - A sweater/top
- `skirt.jpg` - A skirt
- `boots.jpg` - Boots

Output: Professional fashion photo of a model wearing all three items together.

## License

MIT
