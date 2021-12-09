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

#file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024

@app.route('/')
def index():
    return render_template('signup.html',title='Welcome!')

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
    if request.method == 'GET':
        print(status)
        if status == 'STUDENT':
            #query to fetch course assignments/match suggestions
            #query to fetch top 5 courses from database
            return render_template('dashboard.html', status='STUDENT')
        if status == 'PROFESSOR':
            return render_template('prof_dashboard.html', status='PROFESSOR')
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
    #     return

@app.route('/preferences/', methods=['GET', 'POST'])
def preferences():
    if request.method == 'GET':
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''select * from courses''')
        rows = curs.fetchall()
        #rows = course.viewCourses(conn) --> same issue as above
        return render_template('course_preferences.html', rows=rows)
    else:
        #insert query to input rank info into database
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
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
