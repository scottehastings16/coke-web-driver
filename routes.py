import subprocess
from flask import Blueprint, request, jsonify
import json
import time
import logging

# Define the blueprint
scrape_bp = Blueprint('scrape', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Route to start the scraping process
@scrape_bp.route('/scrape', methods=['POST'])
def scrape_urls():
    try:
        # Get URLs from the POST request
        data = request.get_json()  # Expecting JSON payload
        urls = data.get('urls', [])

        if not urls:
            return jsonify({"error": "No URLs provided"}), 400

        # Validate the URLs (simple check)
        for url in urls:
            if not url.startswith("http"):
                return jsonify({"error": f"Invalid URL format: {url}"}), 400

        # Call the python scraping script (coke-driver.py)
        result = subprocess.run(['python', 'coke-driver.py', *urls], capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Scraping failed: {result.stderr}")
            return jsonify({"error": f"Scraping failed: {result.stderr}"}), 500

        # If the scraping is successful, return success message
        return jsonify({
            "message": "Scraping completed successfully",
            "output": result.stdout
        })

    except Exception as e:
        logging.exception("Error occurred during scraping process")
        return jsonify({"error": str(e)}), 500
