from flask import Flask, jsonify
from flask_cors import CORS
from entities.HomeDoc import HomeDoc
app = Flask(__name__)
CORS(app)

doc = HomeDoc(
    id=1,
    fatherId=2,
    fatherInteriorEntityKey="abc123",
    interiorEntityKey="xyz456",
    createdAt="2023-01-01",
    updatedAt="2023-01-02",
    category="General",
    type="Report",
    description="Some description",
    extraData=[{"key": "value"}]
)

print(doc.description)  # Some description


@app.route('/')
def home():
    return "Welcome to the HomeDoc API!" + " " + str(doc)  

@app.route('/users')
def get_users():
    return jsonify([{"id": 1, "name": "Itsik"}])

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
