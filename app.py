from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb+srv://vega:vega2003@assignment.hiocmf1.mongodb.net/?retryWrites=true&w=majority&appName=assignment')
db = client.post
users = db.users
posts = db.posts

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        user_data = users.find_one({"email": email, "password": password})
        if user_data:
            return redirect(url_for('index', user_id=str(user_data['_id']), username=user_data['name']))
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        return render_template("signin.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']

        if users.find_one({"email": email}):
            return jsonify({'error': 'User already exists'}), 400
        else:
            user_data = {'name': name, 'email': email, 'password': password}
            users.insert_one(user_data)
            return jsonify({'message': 'User registered successfully'})
    else:
        return render_template("signup.html")

@app.route('/index/<user_id>', methods=['GET'])
def index(user_id):
    user_data = users.find_one({"_id": ObjectId(user_id)})
    all_posts = posts.find()
    return render_template('index.html', user=user_data, posts=all_posts)

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['pass']

    user_data = users.find_one({"email": email, "password": password})
    if user_data:
        return jsonify({'status': True, 'user_id': str(user_data['_id'])})
    else:
        return jsonify({'status': False})

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['pass']

    if users.find_one({"email": email}):
        return jsonify({'status': False})
    else:
        user_data = {'name': name, 'email': email, 'password': password}
        users.insert_one(user_data)
        return jsonify({'status': True})

@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.json
    title = data['title']
    content = data['content']
    username = data['username']  # Get username from the request data
    timestamp = datetime.now().strftime('%I:%M %p · %b %d, %Y')
    post_id = posts.insert_one({'title': title, 'content': content, 'username': username, 'timestamp': timestamp}).inserted_id
    new_post = {'_id': str(post_id), 'title': title, 'content': content, 'username': username, 'timestamp': timestamp}
    return jsonify(new_post)

@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    data = request.json
    comment = data['comment']
    username = data['username']
    timestamp = data['timestamp']
    posts.update_one({'_id': ObjectId(post_id)}, {'$push': {'comments': {'username': username, 'content': comment, 'timestamp': timestamp}}})
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)