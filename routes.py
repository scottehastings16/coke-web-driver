import subprocess
from flask import Blueprint, request, jsonify, redirect, url_for
import json

scrape_bp = Blueprint('scrape', __name__)

@scrape_bp.route('/scrape', methods=['POST'])
def scrape_urls():
    try:
        # Get the form data (URLs entered by the user)
        urls = request.form.get('urls', '')
        urls_list = urls.split(',')

        if not urls_list:
            return jsonify({"error": "No URLs provided"}), 400

        # Call the python scraping script (coke-driver.py)
        result = subprocess.run(['python', 'coke-driver.py', *urls_list], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": f"Scraping failed: {result.stderr}"}), 500

        # If scraping is successful, return success message
        return jsonify({
            "message": "Scraping completed successfully",
            "output": result.stdout
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
