import cs304dbi as dbi

def viewCourses(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses''')
    rows = curs.fetchall()
    return rows
