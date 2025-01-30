# routes.py
import subprocess
from flask import Blueprint, request, jsonify
import json
import time

# Define the blueprint
scrape_bp = Blueprint('scrape', __name__)

# Route to start the scraping process
@scrape_bp.route('/scrape', methods=['POST'])
def scrape_urls():
    try:
        # Get URLs from the POST request
        data = request.get_json()  # Expecting JSON payload
        urls = data.get('urls', [])

        if not urls:
            return jsonify({"error": "No URLs provided"}), 400

        # Call the python scraping script (coke-driver.py)
        result = subprocess.run(['python', 'coke-driver.py', *urls], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": f"Scraping failed: {result.stderr}"}), 500

        # If the scraping is successful, return success message
        return jsonify({
            "message": "Scraping completed successfully",
            "output": result.stdout
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
