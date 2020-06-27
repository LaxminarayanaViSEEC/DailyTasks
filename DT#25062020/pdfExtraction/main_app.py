from pdf_extractor import extract_data
import argparse
import json
import sys
from flask import Flask,request,jsonify

app = Flask(__name__)

@app.route('/',methods=['POST'])
def home():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        json_data = extract_data(file_path=data['file_path'],
                                    pages=data['pages'],
                                    password=data['password'],
                                    exclude_type=data['exclude_type'])
        return jsonify(json_data)

if __name__=='__main__':
    app.run(debug=True)