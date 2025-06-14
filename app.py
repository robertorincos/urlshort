from flask import Flask, request, jsonify, redirect, render_template
from datetime import datetime
import random
import string
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_HOST = os.getenv('MONGO_HOST', 'mongodb')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))

client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client.flask_database # creating your flask database using your mongo client 
url_database = db.url_database # creating a collection called "todos"
def base62_encode(num):
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    base = len(characters)
    encoded = ""
    while num > 0:
        num, rem = divmod(num, base)  
        encoded = characters[rem] + encoded 
    return encoded or characters[0] 

def urlShortener():
    now = datetime.now()
    ts = int(now.timestamp())
    last_6 = ts % 1000000
    time62 = base62_encode(last_6)
    length = 3
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    combine = random_string+time62
    return combine

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    original_url = data['url']
    code = urlShortener()
    
    url_database.insert_one({'short_code': code, "original_url":original_url})
   
    
    return jsonify({
        'original_url': original_url,
        'short_code': code,
        'short_url': f'http://localhost:5000/{code}'
    })

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url_doc = url_database.find_one({'short_code': short_code})
    
    if url_doc:
        return redirect(url_doc['original_url'])
    else:
        return "URL not found", 404

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)