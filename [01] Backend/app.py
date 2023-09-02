from flask import Flask, render_template, request
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'smd@2004'
app.config['MYSQL_DB'] = 'user'

bcrypt= Bcrypt(app)
mysql = MySQL(app)

@app.route('/')
def webcall():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def index():
        email = request.form['email']
        password = request.form['password']
        if not email and not password:
            return '<h1>Please enter both email and password.</h1>'
        elif not email:
            return '<h1>enter email</h1>'
        elif not password:
            return '<h1>enter password</h1>'

        cur = mysql.connection.cursor()
        mysql.connection.commit()
        cur.execute("SELECT * FROM registration WHERE email= %s",(email,))
        user=cur.fetchone()
            
        if user is None:
            return 'user not found'
            
        else:
            stored_pass=user[1]
            if bcrypt.check_password_hash(stored_pass, password):
                return 'login successful'
            else:
                return 'invalid credentials'
            
            


if __name__ == '__main__':
    app.run(debug=True)