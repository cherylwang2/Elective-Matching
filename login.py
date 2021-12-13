from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)
import cs304dbi as dbi
import bcrypt
import random
# import fetch

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# Shows log in page
@app.route('/')
def page():
    return render_template("cloud.html")

@app.route('/signUp/', methods = ["POST"])
def signUp():
    conn = dbi.connect()

    # get user input
    newUsername = request.form["username"]
    newPassword = request.form["password"]

    # hash new password
    hashed = bcrypt.hashpw(newPassword.encode('utf-8'), bcrypt.gensalt())
    stored = hashed.decode('utf-8')

    try: # insert new username and password
        sql = '''INSERT INTO user (uid) 
        VALUES (%s)'''
        curs = dbi.dict_cursor(conn)
        curs.execute(sql,[newUsername])
        conn.commit()
        return # redirect to dashboard for status S or P 
    except Exception as err: # error if username already exists
        msg = 'Sorry! That username is taken'
        return # render template again  
    
@app.route('/login/', methods = ["POST"])
def login():
    conn = dbi.connect()
    
    # get user input
    Username = request.form["username"]
    Password = request.form["password"]
    curs = dbi.dict_cursor(conn)
    sql = '''select uid,
        from user
        where uid = %s 
        '''
    curs.execute(sql,[Username])
    sql = curs.fetchone()
    
    # check if username exists
    if sql is None:
        msg = "Sorry; that username does not exist"
        return #render to sign up or change log in info
    # check if password matches using hashed and bcrypt  
    stored = sql['password']
    hashed2 = bcrypt.hashpw(Password.encode('utf-8'), stored.encode('utf-8'))
    hashed2_str = hashed2.decode('utf-8')
    if hashed2_str == stored:
        print("the passwords match")
        #session['username'] = Username
        session['uid'] = sql['username']
        return # redirect to dashboard acc to the users dashboard ( S or P)
    else:
        msg = "Sorry; that Password does not match the exsiting one in our system"
        return #render to change log in info


""" 
@app.route('/<username>/<key>', methods = ['GET','PUT','DELETE'])
def user_key(username = None, key = None):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    # getItem()
    if request.method == 'GET':
        sql = '''select itemValue
        from userItems
        where username = %s and itemKey= %s
        '''
        curs.execute(sql,[username, key])
        val = curs.fetchone()['itemValue']
        return jsonify({'error': False, 'value': val})

    # setItem()
    if request.method == 'PUT' :
        newVal = request.form['value']
        sql = '''INSERT INTO userItems(username, itemKey, itemValue) 
        VALUES (%s, %s, %s)'''
        curs.execute(sql,[username, key, newVal])
        conn.commit()	
        return jsonify({'error': False})

    # deleteItem() 
    if request.method == 'DELETE':
        sql = '''Delete 
        from userItems 
        where username = %s and itemKey= %s
        '''
        curs.execute(sql,[username, key])
        conn.commit()	
        return jsonify({'error': False})

    return render_template("cloud.html")
 """

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'rw1_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
