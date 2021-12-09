import cs304dbi as dbi

def viewCourses(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from courses''')
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
