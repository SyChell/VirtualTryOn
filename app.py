"""
Virtual Try-On Web Application
Flask backend serving the frontend and API endpoints.
"""

import os
import json
import uuid
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from agent import generate_outfit_image
from fabric_client import get_fabric_client

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
PRODUCTS_FOLDER = './static/products'
GENERATED_FOLDER = './static/generated'
CATALOG_FILE = './data/catalog.json'

# Ensure folders exist
os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs(PRODUCTS_FOLDER, exist_ok=True)

# Category display names
CATEGORY_NAMES = {
    "hosen": "Hosen",
    "jacken": "Jacken", 
    "pullover": "Pullover",
    "schuhe": "Schuhe",
    "roecke": "Röcke",
    "kleider": "Kleider"
}


def load_catalog():
    """Load product catalog from JSON file."""
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
            raw_catalog = json.load(f)
            # Transform to include category metadata
            catalog = {}
            for category_id, products in raw_catalog.items():
                # Calculate discount percentage if originalPrice exists
                for product in products:
                    if product.get('originalPrice') and product['originalPrice'] > product['price']:
                        product['discount'] = round((1 - product['price'] / product['originalPrice']) * 100)
                    else:
                        product['discount'] = None
                
                catalog[category_id] = {
                    "name": CATEGORY_NAMES.get(category_id, category_id.capitalize()),
                    "products": products
                }
            return catalog
    return {}


# Load catalog on startup
CATALOG = load_catalog()


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/categories')
def get_categories():
    """Get all categories."""
    categories = [{"id": key, "name": val["name"]} for key, val in CATALOG.items()]
    return jsonify(categories)


@app.route('/api/products/<category>')
def get_products(category):
    """Get products for a category."""
    if category not in CATALOG:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(CATALOG[category]["products"])


@app.route('/api/product/<product_id>')
def get_product(product_id):
    """Get a single product by ID."""
    for category_id, category in CATALOG.items():
        for product in category["products"]:
            if product["id"] == product_id:
                return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@app.route('/api/generate', methods=['POST'])
def generate_look():
    """Generate outfit image from selected products."""
    data = request.json
    selected_items = data.get('items', [])
    
    if not selected_items:
        return jsonify({"error": "No items selected"}), 400
    
    # Map product IDs to image paths
    image_paths = []
    products_info = []
    
    for item_id in selected_items:
        for category_id, category in CATALOG.items():
            for product in category["products"]:
                if product["id"] == item_id:
                    # Check if product image exists in category subfolder
                    img_path = os.path.join(PRODUCTS_FOLDER, category_id, product["image"])
                    if os.path.exists(img_path):
                        image_paths.append(img_path)
                        products_info.append(product)
                    break
    
    if not image_paths:
        return jsonify({"error": "No images available for selected products"}), 400
    
    # Generate unique output filename
    output_filename = f"generated_{uuid.uuid4().hex[:8]}.jpeg"
    output_path = os.path.join(GENERATED_FOLDER, output_filename)
    
    try:
        print(f"🔄 Generating look with {len(image_paths)} images...")
        generate_outfit_image(image_paths, output_path)
        
        # Return the generated image info
        return jsonify({
            "success": True,
            "image": f"/static/generated/{output_filename}",
            "products": products_info
        })
    except Exception as e:
        print(f"❌ Error generating look: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/products/<category>/<filename>')
def serve_product_image(category, filename):
    """Serve product images from category subfolders."""
    category_path = os.path.join(PRODUCTS_FOLDER, category)
    return send_from_directory(category_path, filename)


@app.route('/api/combination', methods=['POST'])
def save_combination():
    """
    Save a combination (outfit) to Fabric Event Hub.
    Called when a user generates a look.
    """
    data = request.json
    user_id = data.get('user_id', f'anonymous-{uuid.uuid4().hex[:8]}')
    items = data.get('items', [])
    
    if not items:
        return jsonify({"error": "No items provided"}), 400
    
    try:
        fabric_client = get_fabric_client()
        combination_id = fabric_client.send_combination(user_id, items)
        
        return jsonify({
            "success": True,
            "combination_id": combination_id,
            "message": "Combination saved to Fabric"
        })
    except Exception as e:
        print(f"❌ Error saving combination: {e}")
        # Don't fail the request if Fabric is unavailable
        return jsonify({
            "success": False,
            "combination_id": None,
            "error": str(e)
        }), 200  # Return 200 so the app continues to work


@app.route('/api/order', methods=['POST'])
def place_order():
    """
    Place an order and send to Fabric Event Hub (Sales stream).
    """
    data = request.json
    user_id = data.get('user_id', f'anonymous-{uuid.uuid4().hex[:8]}')
    combination_id = data.get('combination_id')
    items = data.get('items', [])
    
    if not items:
        return jsonify({"error": "No items provided"}), 400
    
    try:
        fabric_client = get_fabric_client()
        
        # If no combination_id provided, create one first
        if not combination_id:
            combination_id = fabric_client.send_combination(user_id, items)
        
        # Send the order
        order_id = fabric_client.send_order(user_id, combination_id, items)
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "combination_id": combination_id,
            "message": "Order placed successfully"
        })
    except Exception as e:
        print(f"❌ Error placing order: {e}")
        # Return success anyway so the user sees the confirmation
        return jsonify({
            "success": False,
            "order_id": str(uuid.uuid4()),  # Generate a local order ID
            "error": str(e)
        }), 200


if __name__ == '__main__':
    print("🚀 Starting Virtual Try-On Web Server...")
    print("📍 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
