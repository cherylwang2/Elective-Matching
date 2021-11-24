from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi
import course

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
    return render_template('signup.html',title='Welcome!')

@app.route('/view/')
def view():
    return
    #classlist = courses.getallcourses()
    #selects coursename, courseprofessor, coursedescription... SHOULD BE LINKS
    #return render_template('view.html', classes = classlist)

@app.route('/dashboard/<status>/', methods=["GET", "POST"])
def dashboard(status):
<<<<<<< HEAD
    if status == 'STUDENT':

        return render_template('dashboard.html')
        if request.method == 'GET':
            return render_template('dashboard.html')
        try:
            #the form will have their top 5 courses 
            #request.form etc etc etc (see next 2 comments for Q about this)
            #dashboard assumes returning user, as in they've already ranked their top 5 -->
            #so we should pull the info for top 5 out of the DATABASE, not the form
            class1 = request.form.get('class1')
            class2 = request.form.get('class2')
            class3 = request.form.get('class3')
            class4 = request.form.get('class4')
            class5 = request.form.get('class5')
            return render_template('dashboard.html', class1=class1, class2=class2, class3=class3, class4=class4, class5=class5)
            )
        except:
            flash('invalid entry: please enter all 5 courses')
            #i think all of us have different ideas of where/when exactly the user
            #would enter their 5 courses; lets decide on 1 concrete vision before implementing this route
            return render_template('dashboard.html')
    if status == 'PROFESSOR':
        return render_template('prof_dashboard.html')
        if request.method == 'GET':
            return render_template('prof_dashboard.html')
        #add a course/edit an existing course
        #will it ever be POST for professors?
=======
    if request.method == 'GET':
        print(status)
        if status == 'STUDENT':
            return render_template('dashboard.html', status='STUDENT')
        if status == 'PROFESSOR':
            return render_template('prof_dashboard.html', status='PROFESSOR')
>>>>>>> a5c4578dd1e30a07ef4a82594e8dbebc3015f2c6
    else:
        return
    #     else:
    #         try:
    #             #the form will have their top 5 courses 
    #             #request.form etc etc etc (see next 2 comments for Q about this)
    #             #dashboard assumes returning user, as in they've already ranked their top 5 -->
    #             #so we should pull the info for top 5 out of the DATABASE, not the form
    #             return render_template('dashboard.html', #class1=, class2=, etc.
    #             )
    #         except:
    #             flash('invalid entry: please enter 5 courses')
    #             #i think all of us have different ideas of where/when exactly the user
    #             #would enter their 5 courses; lets decide on 1 concrete vision before implementing this route
    #             return render_template('dashboard.html')
    # if status == 'PROFESSOR':
    #     if request.method == 'GET':
    #         return render_template('prof_dashboard.html')
    #     #add a course/edit an existing course
    #     #will it ever be POST for professors?
    # else:
    #     flash('Please log in!')
    #     return redirect(url_for(index))

@app.route('/course/<courseid>')
def course():
    return
    #courseInfo = courses.getCourseInfo(courseid)
    #select course info
    #return render_template('prof_courseDetail.html', courseInfo=courseInfo)

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('prof_addCourseForm.html')
    else:
        try:
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            print(curs)
            print(request.form['number'])
            curs.execute('''insert into courses (courseid, name, capacity, waitlistCap)
                            values (%s, %s, %s, %s)''', [request.form['number'], 
                                                        request.form['title'], 
                                                        int(request.form['capacity']), 
                                                        int(request.form['waitlistCap'])])
            conn.commit()
            return render_template('prof_addCourseForm.html')
        except:
            flash('Oh no! That course already exists. Enter a different one:') #TODO: change error message
            return render_template('prof_addCourseForm.html')

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'electivematching_db' 
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
