import sys, os
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

#importing algorithm module
import algorithm as alg
import random

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

#index/signup route opens for users before they go to dashboard
@app.route('/')
def index():
    return render_template('signup.html',title='Welcome!')

#pull account name out of CAS for unique uid and store in session
#pull given name (first name) out of CAS and store in database, + greet user
#depending on CAS attributes, redirect to either student dashboard or faculty dashboard
@app.route('/logged_in/') 
def logged_in():
    uid = session['CAS_ATTRIBUTES']['cas:sAMAccountName']
    session['uid'] = uid
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into user (uid, name) values (%s, %s) on duplicate key update uid=uid''', [uid, session['CAS_ATTRIBUTES']['cas:givenName']])
    conn.commit()
    #NO MATTER WHAT the user clicks, redirect them to page based off of CAS attributes 
    #safety measure, don't want students to be signing in as professors and having extra permissions
    if session['CAS_ATTRIBUTES']['cas:isStudent'] and uid != 'tg2': #to test for professor pages, add a statement saying 'and uid != youruidhere'
        session['status'] = 'STUDENT'
    elif session['CAS_ATTRIBUTES']['cas:isFaculty']:
        session['status'] = 'PROFESSOR'
    return redirect(url_for('dashboard', status=session['status']))

    if 'CAS_USERNAME' in session:
        is_logged_in = True
        username = session['CAS_USERNAME']
        print(('CAS_USERNAME is: ',username))
    else:
        is_logged_in = False
        username = None
        print('CAS_USERNAME is not in the session')

#route to view list of all available courses
#nav bar changes based on status so you can't change between student and professor permissions
@app.route('/view/<status>')
def view(status):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses''')
    rows = curs.fetchall()
    return render_template('view_all.html', rows=rows, status=session['status'])

@app.route('/form-process/')
def formProcess():
    error_msg = ""

    query = request.args.get('query')
    kind = request.args.get('kind')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    if kind == 'number':
        curs.execute('''select * from courses where courseid like %s''', "%" + query+ "%")
        rows=curs.fetchall()
        print(rows)
        if len(rows) == 1:
            return redirect(url_for('course', courseid=rows[0]['courseid']))
    elif kind == 'name':
        curs.execute('''select * from courses where name like %s''', "%" + query + "%")
        rows=curs.fetchall()
        print(rows)
        if len(rows) == 1:
            return redirect(url_for('course', courseid=rows[0]['courseid']))
    if len(rows) == 0:
        flash("Sorry, no {} found".format(kind))

    return render_template("view_all.html", rows=rows, status=session['status'])


#route to render dashboard for students and professors
@app.route('/dashboard/', methods=["GET", "POST"])
def dashboard():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    if request.method == 'GET':
        print(session['uid'])
        print(session['status'])
        if session['status'] == 'STUDENT':
            #query to fetch course assignments/match suggestions
            curs.execute('''select course, name from assignments inner join courses where course=courses.courseid and uid=%s''',
                        [session['uid']])
            matches = curs.fetchall()

            #query to fetch student's top choices
            curs.execute('''select course, courseRank, name from chooses inner join courses where student=%s and course=courseid''', [session['uid']])
            choices = curs.fetchall()
            print(matches)
            print(choices)
            #render dashboard for student with all 5 top courses displayed in order
            try:
                return render_template('dashboard.html', name=session['CAS_ATTRIBUTES']['cas:givenName'], 
                                        course1 = choices[0]['course'], course2 = choices[1]['course'], course3=choices[2]['course'], 
                                        course4=choices[3]['course'], course5=choices[4]['course'], course1name=choices[0]['name'],
                                        course2name=choices[1]['name'], course3name=choices[2]['name'], course4name=choices[3]['name'],
                                        course5name=choices[4]['name'], matches=matches)
            #if no courses have been chosen yet, will display empty set of 5 cards with 'CS'
            except:
                return render_template('dashboard.html', name=session['CAS_ATTRIBUTES']['cas:givenName'])
        if session['status'] == 'PROFESSOR':
            #query to fetch dictionary of courses this professor teaches (ie courses they added to the database)
            curs.execute('''select courseid, name from courses inner join teaches where courses.courseid=teaches.course and professor=%s''',
                        [session['uid']])
            teaches = curs.fetchall()
            print(teaches)
            return render_template('prof_dashboard.html', name=session['CAS_ATTRIBUTES']['cas:givenName'],
                                    teaches=teaches)
    else:
        return

#route to either get preference information from users on get, or add it to the database on post
@app.route('/preferences/', methods=['GET', 'POST'])
def preferences():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    uid = session['uid']
    if request.method == 'GET':
        print(session['uid'])
        #query to get all courses and display as options for preferences form
        curs.execute('''select * from courses''')
        rows = curs.fetchall()
        return render_template('course_preferences.html', rows=rows)
    else:
        #query to input rank info into database
        yearDict = {'2022':500, '2023':400, '2024':300, '2025':200} #update each year
        curs.execute('''update user set classYear = %s where uid = %s''', [request.form['classYear'], uid])
        conn.commit()
        #query to fetch student class years
        curs.execute('''select classYear from user where uid = %s''', [uid])
        tokens = yearDict[curs.fetchone()['classYear']]
        course1= int(request.form['course1'])
        course2= int(request.form['course2'])
        course3= int(request.form['course3'])
        course4= int(request.form['course4'])
        course5= int(request.form['course5'])
        weight1= int(request.form['weight1'])
        weight2= int(request.form['weight2'])
        weight3= int(request.form['weight3'])
        weight4= int(request.form['weight4'])
        weight5= int(request.form['weight5'])
        weights = [weight1,weight2,weight3,weight4,weight5]
        #make sure that student has put their course weights in descending order (gave rank 1 the most points, didn't give 2 the same weight)
        courseSet = {course1, course2, course3, course4, course5}
        for i in range(4):
            if weights[i] < weights[i+1]:
                inOrder= False
                break
            else: 
                inOrder= True
        #check to make sure course weights add up to 500
        sum500 = weight1 + weight2 + weight3 + weight4 + weight5
        if inOrder == False or sum500 != 500 or len(courseSet) != 5:
            if not inOrder: 
                flash("Courses must be ranked in descending order!")
            elif sum500 != 500:
                flash("Courses must sum up to 500!")
            else:
                flash("Courses must be distinct!")
            curs.execute('''select * from courses''')
            rows = curs.fetchall()
            return render_template('course_preferences.html', rows=rows)

        #queries to insert student preference information into chooses table in database
        curs.execute('''insert into chooses (student, course, courseRank, courseWeight, tokens)
                        values (%s, %s, %s, %s, %s) on duplicate key update course = %s, courseWeight = %s, tokens = %s''', 
                        [uid, course1, 1, weight1, tokens, course1, weight1, tokens])
        curs.execute('''insert into chooses (student, course, courseRank, courseWeight, tokens)
                        values (%s, %s, %s, %s, %s) on duplicate key update course = %s, courseWeight = %s, tokens = %s''', 
                        [uid, course2, 2, weight2, tokens, course2, weight2, tokens])
        curs.execute('''insert into chooses (student, course, courseRank, courseWeight, tokens)
                        values (%s, %s, %s, %s, %s) on duplicate key update course = %s, courseWeight = %s, tokens = %s''', 
                        [uid, course3, 3, weight3, tokens, course3, weight3, tokens])
        curs.execute('''insert into chooses (student, course, courseRank, courseWeight, tokens)
                        values (%s, %s, %s, %s, %s) on duplicate key update course = %s, courseWeight = %s, tokens = %s''', 
                        [uid, course4, 4, weight4, tokens, course4, weight4, tokens])
        curs.execute('''insert into chooses (student, course, courseRank, courseWeight, tokens)
                        values (%s, %s, %s, %s, %s) on duplicate key update course = %s, courseWeight = %s, tokens = %s''', 
                        [uid, course5, 5, weight5, tokens, course5, weight5, tokens])
        conn.commit()
        #query to get the average course weight for each course and store it in the courses table
        for i in courseSet:
            curs.execute('''select avg(courseWeight) as average from chooses where course = %s''', i)
            cursor = curs.fetchone()
            print(cursor)
            avg = int(cursor['average'])
            curs.execute('''update courses set weight = %s where courseid = %s''', [avg, i])
        conn.commit()
        return redirect(url_for('dashboard', status='STUDENT'))

#route to display the detail course page for user, depending on student or professor (professors can add courses)
@app.route('/course/<courseid>/', methods=['GET', 'POST'])
def course(courseid):
    print(session['uid'])
    print(session['status'])
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    #query to select course information for the course in question
    curs.execute('''select * from courses where courseid = %s''',[courseid])
    courseInfo = curs.fetchone()
    print(courseInfo)

    #query to select all students that have been matched to this course
    curs.execute('''select * from user where uid in (select uid from assignments where course=%s)''',[courseid])
    students = curs.fetchall()

    #query for fileupload, get the file that has been uploaded for the course and assign url to src for template
    curs.execute('''select filename from courses where courseid=%s''', [courseid])
    syllabus = curs.fetchone()
    syllabus_src = url_for('syllabus', courseid=courseid)

    if session['status'] == 'STUDENT':
        return render_template('courseDetail.html', courseInfo=courseInfo, syllabus_src=syllabus_src)
    elif session['status'] == 'PROFESSOR':
        return render_template('prof_courseDetail.html', courseInfo=courseInfo, students=students, syllabus_src=syllabus_src)

#function for file upload, process courseid and return the url for the syllabus/materials uploaded for it
@app.route('/syllabus/<courseid>')
def syllabus(courseid):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute(
        '''select filename from courses where courseid = %s''',
        [courseid])
    if numrows == 0:
        flash('No syllabus uploaded yet for {}'.format(courseid))
        return redirect(url_for('/add/'))
    row = curs.fetchone()
    try:
        return send_from_directory(app.config['UPLOADS'],row['filename'])
    except:
        return ("No syllabus yet. Sorry about that!")

#route for professors to add a new course, on get render form and on post store info in database
@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        print(session['uid'])
        print(session['status'])
        return render_template('prof_addCourseForm.html')
    else:
        try:
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            #get inputs from the form
            number = request.form['number']
            title = request.form['title']
            capacity = int(request.form['capacity'])
            waitlistCap = int(request.form['waitlistCap'])
            description = request.form['description']
            profID = session['uid']
            #query to insert form inputs into the database, we will ignore duplicate entries and instead show update
            curs.execute('''insert ignore into courses (courseid, name, capacity, waitlistCap, description) values (%s, %s, %s, %s, %s)''',
                            [number, title, capacity, waitlistCap, description])
            
            #caveat: here we will assume that if a professor is adding a course to the database, they themselves teach it
            curs.execute('''select courseid from courses''')
            allCourses = curs.fetchall()['courseid']

            if number not in allCourses:
                curs.execute('''insert into teaches (professor, course) values (%s, %s)''',[profID, number])
                conn.commit()
            else:
                flash('Oh no! That course already exists. Alter the existing course listing:')
                return redirect (url_for('update', courseid=number))
            #file upload: if the course has a file attached, upload it to the uploads folder 
            if request.files['courseFile']:
                try:
                    #create an additional random seq to add to filename so users can upload multiple files
                    addon = [ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ]
                    f = request.files['courseFile']
                    user_filename = f.filename
                    ext = user_filename.split('.')[-1]
                    filename = secure_filename('{}{}.{}'.format(session['uid'], addon, ext))
                    pathname = os.path.join(app.config['UPLOADS'],filename)
                    f.save(pathname)
                    conn = dbi.connect()
                    curs = dbi.dict_cursor(conn)
                    curs.execute('''update courses set filename = %s where courseid= %s''', 
                                [filename, number])
                    conn.commit()
                except Exception as err:
                    flash('Upload failed {why}'.format(why=err))
            return redirect(url_for('course', courseid=number))
        except:
            flash('Oh no! That course already exists. Alter the existing course listing:')
            return redirect(url_for('update', courseid=number))

@app.route('/update/<courseid>', methods=['GET', 'POST'])
def update(courseid):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    if request.method == 'GET':
        curs.execute('''select * from courses where courseid=%s''', [courseid])
        row = curs.fetchone()
        return render_template('prof_updateCourseForm.html', row=row)
    if request.method == 'POST':
        number = request.form['number']
        title = request.form['title']
        capacity = int(request.form['capacity'])
        waitlistCap = int(request.form['waitlistCap'])
        description = request.form['description']
        profID = session['uid']
        if request.files['courseFile']:
                try:
                    #create an additional random seq to add to filename so users can upload multiple files
                    addon = [ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ]
                    f = request.files['courseFile']
                    user_filename = f.filename
                    ext = user_filename.split('.')[-1]
                    filename = secure_filename('{}{}.{}'.format(session['uid'], addon, ext))
                    pathname = os.path.join(app.config['UPLOADS'],filename)
                    f.save(pathname)
                    conn = dbi.connect()
                    curs = dbi.dict_cursor(conn)
                    curs.execute('''update courses set filename = %s where courseid= %s''', 
                                [filename, number])
                    conn.commit()
                except Exception as err:
                    flash('Upload failed {why}'.format(why=err))
        curs.execute('''update courses set name=%s, capacity=%s, waitlistCap=%s, description=%s, filename=%s where courseid=%s''',
                    [title, capacity, waitlistCap, description, filename, number])
        conn.commit()
    return redirect(url_for('course', courseid=number))

#route to connect algorithm in algorithm.py with application
@app.route('/algorithm/', methods=['GET'])
def algorithm():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select c.student, c.course, c.courseRank, c.courseWeight, c.tokens, courses.capacity from chooses c inner join courses on (c.course = courses.courseid)
    order by c.student, courseRank''')
    chooses = curs.fetchall()
    curs.execute('''select count(student)/5 as count from chooses''')
    students = int(curs.fetchone()['count'])
    length = students * 5
    lists = alg.create_Ineq(chooses, students, length)
    solSet = alg.LP_det_avg(chooses, students, length)
    alg.readSolutionSet(solSet, conn)
    print(solSet)
    conn.commit()
    return redirect(url_for('dashboard', status=session['status']))

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
