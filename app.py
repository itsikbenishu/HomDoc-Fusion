from flask import Flask, jsonify
from flask_cors import CORS
from entities.HomeDoc import HomeDoc
from Fusion import RentalListing

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    try:
        print(f"Welcome to the HomeDoc APIֱֱֱ!!!!!!!")
        return "Welcome to the HomeDoc API!" 
    except Exception as e:
        print(f"Error was found: {e}")


@app.route('/fuse')
def run_fusion():
    RentalListing.run_pipeline("Single Family")
    return jsonify([{"id": 1, "name": "Itsik"}])

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
