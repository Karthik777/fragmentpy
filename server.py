#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
import process_images as cf
from flask import request
from StringIO import StringIO
import base64
from PIL import Image

app = Flask(__name__)

@app.route('/images/post/images', methods=['POST'])
def store_image():
    if not request.json or not 'image' in request.json or not 'name' in request.json:
        abort(400)
    cf.save_profile_photos(request.json.get('images'),request.json.get('name'))

@app.route('/screenshots/post/images', methods=['POST'])
def pipe_images():
    # if not request.json or not 'data' in request.json:
    #     abort(400)
    print(request.json)
    result =cf.process_image(request.json.get('data'))
    return jsonify({'status': result[0],'name': result[1]}), 201

if __name__ == '__main__':
    app.run(debug=True)