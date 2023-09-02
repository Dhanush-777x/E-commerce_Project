from flask import Flask, request, session, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from datetime import timedelta
import os
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'smd@2004'
app.config['MYSQL_DB'] = 'ecommerce'
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.config['ADMIN_EMAIL'] = 'admin@gmail.com'
app.config['UPLOAD_FOLDER'] = 'E:/TATA Internship/[02] Frontend/reg-log/src/assets'

bcrypt = Bcrypt(app)
mysql = MySQL(app)
Session(app)
CORS(app)

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM registration WHERE email = %s", (email,))
    user = cur.fetchone()

    if user is None:
        cur.execute("INSERT INTO registration (email, password) VALUES (%s , %s)", (email, hashed_password))
        mysql.connection.commit()
        session['email'] = email
        session['password'] = password
        print("Session email:", session['email'])

        return jsonify({'message': 'Registration Successful'}), 200
    if user:
        return jsonify({'message': 'Already u have an account'}), 400
    else:
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM registration WHERE email= %s", (email,))
    user = cur.fetchone()

    if user is None:
        return jsonify({'message': 'User not found Please Register'})
    else:
        stored_pass = user[1]
        if bcrypt.check_password_hash(stored_pass, password):
            session.permanent = True
            session.modified = True
            session['email'] = email
            if email == app.config['ADMIN_EMAIL']:
                return jsonify({'message': 'Login Successful', 'admin': True}), 200
            else:
                return jsonify({'message': 'Login Successful', 'admin': False}), 200
        else:
            return jsonify({'message': 'Invalid Credentials'})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": 'Logged out successfully'}), 200

@app.route('/addproducts', methods=['POST'])
def addproducts():
    productname = request.form.get('productname')
    description = request.form.get('description')
    brand = request.form.get('brand')
    price = request.form.get('price')
    image_file = request.files.get('image')
    if image_file:
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        image_file = os.path.join('/assets/'+filename)
    else:
        image_file = None

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO products (name, description, brand, price, image) VALUES (%s , %s, %s , %s, %s)", (productname, description, brand, float(price),image_file))
    mysql.connection.commit()
    return jsonify({'message': 'Product added successfully'}), 200

@app.route('/getproducts', methods=['GET'])
def getproducts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    data = cur.fetchall()
    cur.close()
    products = [{'id':row[0], 'image':row[1],'name':row[2], 'description':row[3],'brand':row[4], 'price':row[5],} for row in data]
    return jsonify(products)

@app.route('/delete', methods=['POST'])
def delete():
    product_id = request.json.get('id')
    print(product_id)
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message' : 'product deleted successfully'}) ,200

@app.route('/getproduct', methods=['GET'])
def getproduct():
    product_id = request.args.get('id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()

    if product:
        product_data = {
            'id': product[0],
            'name': product[2],
            'description': product[3],
            'brand': product[4],
            'price': product[5],
            'image' : product[1]
        }
        return jsonify(product_data), 200
    else:
        return jsonify({'message': 'Product not found'}), 404


@app.route('/update', methods=['POST'])
def update():
    product_id = request.json.get('id')
    productname = request.json.get('productname')
    description = request.json.get('description')
    brand = request.json.get('brand')
    price = request.json.get('price')
    image = request.json.get('image')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET name=%s, description=%s, brand=%s, price=%s, image=%s WHERE id=%s",(productname, description, brand, float(price),image, product_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message':'product updated successfully'}),200

@app.route('/cart', methods=['POST'])
def cart():
    item = request.json.get('item')
    email = request.json.get('email')

    if not item:
        return jsonify({'message': 'item data not provided'}), 400

    if not email:
        return jsonify({'message': 'user not logged in!'}), 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT cart_id, quantity FROM CART WHERE user_id = %s AND product_id = %s", (email, item['id']))
    cart_item = cur.fetchone()

    if cart_item is None:
        cur.execute("INSERT INTO CART (user_id, product_id, quantity) VALUES (%s, %s, %s)", (email, item['id'], 1))
        
    else:
        cart_id, current_quantity = cart_item
        new_quantity = current_quantity + 1
        cur.execute("UPDATE CART SET quantity = %s WHERE cart_id = %s AND user_id=%s", (new_quantity, cart_id, email))

    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'item added to cart successfully'}), 200  

if __name__ == '__main__':
    app.run(debug=True)