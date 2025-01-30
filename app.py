import os
from flask import Flask, render_template
from routes import scrape_bp

# Initialize Flask app
app = Flask(__name__)

# Register the blueprint
app.register_blueprint(scrape_bp)

# Route to serve index.html
@app.route('/')
def index():
    return render_template('index.html')

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

