from flask import Flask
from routes import scrape_bp  # Import the blueprint from routes.py

# Initialize the Flask app
app = Flask(__name__)

# Register the blueprint for scraping
app.register_blueprint(scrape_bp)

# Ensure the app runs when executed directly
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Running on port 5000 for Heroku
