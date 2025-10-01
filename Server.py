from socket import gethostname
import sqlite3
import random
import json
from time import time
from random import random
from flask import Flask, render_template, make_response, request, jsonify
# Initialize Flask app
app = Flask(__name__)

def initDB():
    # Initialize database and create table if it doesn't exist
    conn = sqlite3.connect('LD.db')  # this will create 'items.db' if it doesn't exist
    cursor = conn.cursor()
    #TODO; create connection to measuring unit so it can send data to maalinger table
    cursor.execute("CREATE TABLE IF NOT EXISTS maalinger (id INTEGER PRIMARY KEY AUTOINCREMENT, lokale TEXT, sensorID TEXT, dB FLOAT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS thresholds (lokale INTEGER PRIMARY KEY, maxDB FLOAT)")
    # Insert some sample data if the table is empty
    cursor.execute("SELECT COUNT(*) FROM thresholds")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("INSERT INTO thresholds (lokale, maxDB) VALUES (?, ?)", (221, 60.0))
        conn.commit()
    conn.close()


@app.route('/')
def home():
    return "Hello, this is the Sound Level Monitoring API!"

@app.route('/arduino', methods=['POST'])
def receive_from_arduino():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({'error': 'No JSON received'}), 400
    # Process the data as needed
    return jsonify({'status': 'success', 'received': data}), 200
# Ved ikke hvad det gør, men det skal hvist være her...
if __name__ == '__main__':
    initDB()
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/graf', methods=["GET", "POST"])
def main():
    return render_template('index.html')

@app.route('/data', methods=["GET", "POST"])
def data():
    data = [time() * 1000, random() * 100]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()

    # Validate input
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing "name" in request data'}), 400

    name = data['name']

    # Insert into database
    conn = sqlite3.connect('items.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (MaxDB) VALUES (?)", (name,))
    conn.commit()

    # Get the ID of the new item
    item_id = cursor.lastrowid
    conn.close()

    new_item = {'id': item_id, 'name': name}
    return jsonify(new_item), 201

# Define the GET /items endpoint
@app.route('/items', methods=['GET'])
def get_items():
    # Connect to the database and fetch all items
    conn = sqlite3.connect('LD.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM thresholds")
    rows = cursor.fetchall()
    conn.close()
    # Convert the query result into a list of dictionaries
    items = []
    for row in rows:
        items.append({"Lokale": row[0], "MaxDB": row[1]})
    # Return the list of items as JSON
    return jsonify(items)

if __name__ == '__main__':
    initDB()
    if 'liveconsole' not in gethostname():
        app.run()