from flask import Flask, render_template, redirect, request, abort, jsonify
import os
import requests
from pymongo import MongoClient
# __name__ is a special variable in Python that refers to the name of the module
# if we execute this Python file directly, __name__ == "__main__"
app = Flask(__name__)
DEBUG = 1
mongo_uri = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/'
domain = 'http://localhost:5000/' if DEBUG else 'https://simple-flask-app-tutorial.herokuapp.com'
client = MongoClient(mongo_uri)

# A single instance of MongoDB can support multiple independent databases.
db = client.test

# A collection is a group of documents stored in MongoDB. Here, we are creating a new collection called exp.
projects = db.projects

@app.route('/')
def hello():
    all_projects = list(projects.find())
    return render_template('home.html', projects=all_projects, active='home')

@app.route('/about')
def about():
    return render_template('about.html', active='about')

@app.route('/contact')
def contact():
    return render_template('contact.html', active='contact')

@app.route('/admin')
def admin():
    return render_template('admin.html', active='')

@app.route('/add_project', methods=['POST'])
def add_project():
    post_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description')
    }
    projects.insert_one(post_data)
    return redirect("/")

@app.route('/del_project/<title>', methods=['DELETE'])
def del_project(title):
    projects.delete_one({'title': title})
    return jsonify(success=True)

@app.route('/update_project/<title>/<description>', methods=['PATCH'])
def update_project(title, description):
    query = {"title": title}
    projects.find_one_and_update(query,
                                 {"$set":
                                     {"title": title,
                                      "description": description}
                                  })

    return jsonify(success=True)

@app.route('/get_project', methods=['GET'])
def get_project():
    title = request.args.get('title')
    project = projects.find_one({'title': title})
    if not project:
        abort(404)

    description = request.args.get('description')
    if not description:
        requests.delete(domain + '/del_project/' + title)
    else:
        requests.patch(domain + '/update_project/' + title + '/' + description)
    return redirect('/')


if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))

