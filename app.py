from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('signup.html',title='Hello')

@app.route('/view/')
def view():
    pass
    #classlist = courses.getallcourses()
    #selects coursename, courseprofessor, coursedescription... SHOULD BE LINKS
    #return render_template('view.html', classes = classlist)

@app.route('/dashboard/', methods=["GET", "POST"])
def dashboard():
    if user['status'] == 'STUDENT':
        if request.method == 'GET':
            return render_template('dashboard.html')
        else:
            try:
                #the form will have their top 5 courses 
                #request.form etc etc etc
                return render_template('dashboard.html', class1=, class2=, etc.)
            except:
                flash('invalid entry: please enter 5 courses')
                return render_template('dashboard.html')
    if user['status'] == 'PROFESSOR':
        if request.method == 'GET':
            return render_template('prof_courseDetail.html')
        #add a course/edit an existing course
        #will it ever be POST for professors?
    else:
        flash('Please log in!')
        return redirect(url_for(index))

@app.route('/course/<varchar:courseid>')
    pass
    #courseInfo = courses.getCourseInfo(courseid)
    #select course info
    #return render_template('course.html', courseInfo=courseInfo)


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'put_database_name_here_db' 
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
