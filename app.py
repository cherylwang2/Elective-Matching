import os
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import algorithm

import random

import course

# new for CAS
from flask_cas import CAS

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

#file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024

def set_status_student():
    session['user_status'] = 'student'

@app.route('/')
def index():
    return render_template('signup.html',title='Welcome!')

@app.route('/logged_in/')
def logged_in():
    uid = session['CAS_ATTRIBUTES']['cas:sAMAccountName']
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into user (uid, name) values (%s, %s) on duplicate key update uid=uid''', [uid, session['CAS_ATTRIBUTES']['cas:givenName']])
    conn.commit()
    if session['CAS_ATTRIBUTES']['cas:isStudent']:
        return redirect(url_for('dashboard', status='STUDENT'))
    elif session['CAS_ATTRIBUTES']['cas:isFaculty']:
        return redirect(url_for('dashboard', status='PROFESSOR'))

    if 'CAS_USERNAME' in session:
        is_logged_in = True
        username = session['CAS_USERNAME']
        print(('CAS_USERNAME is: ',username))
    else:
        is_logged_in = False
        username = None
        print('CAS_USERNAME is not in the session')

@app.route('/view/')
def view():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses''')
    rows = curs.fetchall()
    #rows = course.viewCourses(conn)
    return render_template('view_all.html', rows=rows)
    #classlist = courses.getallcourses()
    #selects coursename, courseprofessor, coursedescription... SHOULD BE LINKS
    #return render_template('view.html', classes = classlist)

@app.route('/dashboard/<status>/', methods=["GET", "POST"])
def dashboard(status):
    uid = session['CAS_ATTRIBUTES']['cas:sAMAccountName']
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    if request.method == 'GET':
        print(status)
        if status == 'STUDENT':
            #query to fetch course assignments/match suggestions
            #query to fetch top 5 courses from database
            curs.execute('''select course, courseRank from chooses where student=%s''', [uid])
            choices = curs.fetchall()
            print(choices)
            #STOPPED HERE - AFTER THIS, ADD ENOUGH TEST DATA FOR 5 COURSES
            #USE INFO FROM CURSOR TO RENDER DASHBOARD COMPLETELY
            return render_template('dashboard.html', status='STUDENT', name=session['CAS_ATTRIBUTES']['cas:givenName'], 
                                    course1 = choices[0]['course'], course2 = choices[1]['course'], course3=choices[2]['course'], 
                                    course4=choices[3]['course'], course5=choices[4]['course'])
        if status == 'PROFESSOR':
            return render_template('prof_dashboard.html', status='PROFESSOR', name=session['CAS_ATTRIBUTES']['cas:givenName'])
    else:
        return
        #no post for dashboard, right? now that we've separated out preferences?

@app.route('/preferences/', methods=['GET', 'POST'])
def preferences():
    uid = session['CAS_ATTRIBUTES']['cas:sAMAccountName']
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    if request.method == 'GET':
        curs.execute('''select * from courses''')
        rows = curs.fetchall()
        #rows = course.viewCourses(conn) --> same issue as above
        return render_template('course_preferences.html', rows=rows)
    else:
        #insert query to input rank info into database
        curs.execute('''insert into chooses (course, courseRank, courseWeight, student)
                        values (%s, %s, %s, %s)''', 
                        [int(request.form['course1']), 1, int(request.form['weight1']), uid])
        curs.execute('''insert into chooses (course, courseRank, courseWeight, student)
                        values (%s, %s, %s, %s)''', 
                        [int(request.form['course2']), 2, int(request.form['weight2']), uid])
        curs.execute('''insert into chooses (course, courseRank, courseWeight, student)
                        values (%s, %s, %s, %s)''', 
                        [int(request.form['course3']), 3, int(request.form['weight3']), uid])
        curs.execute('''insert into chooses (course, courseRank, courseWeight, student)
                        values (%s, %s, %s, %s)''', 
                        [int(request.form['course4']), 4, int(request.form['weight4']), uid])
        curs.execute('''insert into chooses (course, courseRank, courseWeight, student)
                        values (%s, %s, %s, %s)''', 
                        [int(request.form['course5']), 5, int(request.form['weight5']), uid])
        conn.commit()
        return redirect(url_for('dashboard', status='STUDENT'))

@app.route('/course/<status>/<courseid>/', methods=['GET', 'POST'])
def course(status, courseid):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses where courseid = %s''',[courseid])
    courseInfo = curs.fetchone()

    curs.execute('''select * from user where uid in (select uid from assignments where course=%s)''',[courseid])
    students = curs.fetchall()
    #courseInfo = course.chooseCourse(conn, courseid) --> same
    #students = course.getStudents(conn, courseid) --> same

    #TODO: if student, render different detail page without buttons to edit
    #if professor, render this
    if status == 'STUDENT':
        return render_template('courseDetail.html', courseInfo=courseInfo, students=students)
    elif status == 'PROFESSOR':
        return render_template('prof_courseDetail.html', courseInfo=courseInfo, students=students)
    #courseInfo = courses.getCourseInfo(courseid)
    #select course info
    #return render_template('prof_courseDetail.html', courseInfo=courseInfo)

#HARDCODING GLOBAL UID VARIABLE FOR TESTING PURPOSES, IGNORE WHEN WE IMPLEMENT LOGINS + SESSIONS
uid = 123

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('prof_addCourseForm.html')
    else:
        try:
            conn = dbi.connect()
            number = request.form['number']
            title = request.form['title']
            capacity = int(request.form['capacity'])
            waitlistCap = int(request.form['waitlistCap'])
            print(number)
            course.insertCourse(conn, number, title, capacity, waitlistCap)

            if request.form['courseFile']:
                try:
                    f = request.files['courseFile']
                    user_filename = f.filename
                    ext = user_filename.split('.')[-1]
                    filename = secure_filename('{}.{}'.format(uid,ext))
                    pathname = os.path.join(app.config['UPLOADS'],filename)
                    f.save(pathname)
                    conn = dbi.connect()
                    curs = dbi.dict_cursor(conn)
                    #curs.execute(query to insert file into the database)
                except Exception as err:
                    flash('Upload failed {why}'.format(why=err))
            return render_template('prof_addCourseForm.html') #prob change this to the detail page of the course they just added
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
        port=int(sys.argv[1])
        if not(1943 <= port <= 1952):
            print('For CAS, choose a port from 1943 to 1952')
            sys.exit()
    else:
        port=os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
