from flask import Flask, jsonify
from flask_cors import CORS
from entities.HomeDoc import HomeDoc
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    try:
        return "Welcome to the HomeDoc API!" 
    except Exception as e:
        print(f"Error was found: {e}")


@app.route('/fuse')
def get_users():
    return jsonify([{"id": 1, "name": "Itsik"}])

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
