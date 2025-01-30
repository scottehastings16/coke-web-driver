


from your_scraping_script import run_scraper

app = Flask(__name__)

# Route for the homepage (to show the URL input form)
@app.route('/')
def index():
    return render_template('index.html')  # This is a template for your form (create this file)

# Route to handle the URL submission
@app.route('/scrape', methods=['POST'])
def scrape():
    # Get the URLs from the form submission
    urls = request.form.getlist('urls')  # Get the list of URLs

    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    # You can run the scraping function here (replace with your own logic)
    try:
        result = run_scraper(urls)  # Assuming this function scrapes URLs
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
