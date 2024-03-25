# app.py
from flask import Flask, request, render_template, jsonify
from trie import Trie
import csv
import os
app = Flask(__name__)

# Create Trie instance
trie = Trie()

project_dir = os.getcwd()
csv_file_path = os.path.join(project_dir,  'airports_Asia.csv')
# Read airport codes from CSV file and insert into Trie
with open(csv_file_path, 'r',encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        trie.insert(row[3])  # Inserting Airport Code

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/suggest', methods=['GET'])
def suggest():
    prefix = request.args.get('prefix', '')
    suggestions = trie.get_suggestions(prefix)
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)