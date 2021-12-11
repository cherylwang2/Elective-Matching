import cs304dbi as dbi

def viewCourses(conn):
    '''Selects all courses from the listed directory'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses''')
    return curs.fetchall()

def chooseCourse(conn, courseid):
    '''Selects a course given its courseid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses where courseid = %s''',[courseid])
    return curs.fetchone()

def getStudents(conn, courseid):
    '''selects all students registered in a course'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from user where uid in (select uid from assignments where course=%s)''',[courseid])
    return curs.fetchall()

def insertCourse(conn, number, title, capacity, waitlistCap):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into courses (courseid, name, capacity, waitlistCap)
                            values (%s, %s, %s, %s)''', [number, 
                                                        title, 
                                                        capacity, 
                                                        waitlistCap])
    conn.commit()
    rows = curs.fetchall()
    return rows

def courseGivenProf(conn, name):
    curs = dbi.dict_cursor(conn)
    sql = ''' select * from teaches   
        where name = %s%'''
    curs.execute(sql, [name])
    return curs.fetchall()

def courseChosen(conn, rank):
    curs = dbi.dict_cursor(conn)
    sql = '''select * from chooses   
        where courseRank = %s%'''
    curs.execute(sql, [rank])
    return curs.fetchall()
