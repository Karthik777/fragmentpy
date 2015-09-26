#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
import create_pics_from_facebook as cf
from flask import request
app = Flask(__name__)



@app.route('/fbimages/post/images', methods=['POST'])
def store_image():
    if not request.json or not 'image' in request.json or not 'name' in request.json:
        abort(400)
    cf.save_profile_photos(request.json.get('images'),request.json.get('name'))

# @app.route('/todo/api/v1.0/tasks', methods=['POST'])
# def create_task():
#     if not request.json or not 'title' in request.json:
#         abort(400)
#     print(request.json)
#     # cf.save_profile_photos()
#     task = {
#         'id': tasks[-1]['id'] + 1,
#         'title': request.json['title'],
#         'description': request.json.get('description', ""),
#         'done': False
#     }
#     tasks.append(task)
#     return jsonify({'task': task}), 201

@app.route('/screenshots/post/images', methods=['POST'])
def pipe_images():
    # if not request.json or not 'data' in request.json:
    #     abort(400)
    print(request.json)
    # cf.save_profile_photos()
    # task = {
    #     'id': tasks[-1]['id'] + 1,
    #     'title': request.json['title'],
    #     'description': request.json.get('description', ""),
    #     'done': False
    # }
    # tasks.append(task)
    return jsonify({'success': True}), 201


if __name__ == '__main__':
    app.run(debug=True)