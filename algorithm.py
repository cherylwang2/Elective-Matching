#need to import numpy
from scipy.optimize import linprog
import numpy as np

test = [{'student': 1, 'course': 304, 'courseRank': 1, 'courseWeight': 300, 'tokens':300, 'capacity':1},
        {'student': 1, 'course': 305, 'courseRank': 2, 'courseWeight': 350, 'tokens':300, 'capacity':2},
        {'student': 1, 'course': 306, 'courseRank': 3, 'courseWeight': 1, 'tokens':300, 'capacity':1},
        {'student': 1, 'course': 330, 'courseRank': 4, 'courseWeight': 10, 'tokens':300, 'capacity':2},
        {'student': 1, 'course': 320, 'courseRank': 5, 'courseWeight': 15, 'tokens':300, 'capacity':1},
        {'student': 2, 'course': 304, 'courseRank': 1, 'courseWeight': 300, 'tokens':400, 'capacity':1},
        {'student': 2, 'course': 306, 'courseRank': 2, 'courseWeight': 1, 'tokens':400, 'capacity':1},
        {'student': 2, 'course': 305, 'courseRank': 3, 'courseWeight': 350, 'tokens':400, 'capacity':2},
        {'student': 2, 'course': 315, 'courseRank': 4, 'courseWeight': 10, 'tokens':400, 'capacity':3},
        {'student': 2, 'course': 320, 'courseRank': 5, 'courseWeight': 15, 'tokens':400, 'capacity':1}]

#created from inner join chooses with courses on chooses.course = courses.courseid
def create_Ineq(chooses, students, length): #make sure chooses sorts students by ASC and rank by ASC
    #assumes each student chooses 5 classes
    '''chooses is curs object being returned, students is num students, length is length of array'''
    index = 0
    indexDict = {}
    A_ineq = []
    B_ineq = []
    for i in range(students): #this appends the courses
        emptyList = [0 for i in range(length)]
        for j in range(5):
            if chooses[index]['course'] in indexDict:
                indexDict[chooses[index]['course']].append(index)
            else:
                indexDict[chooses[index]['course']] = [index]
            emptyList[index] = chooses[index]['courseWeight']
            index += 1
        A_ineq.append(emptyList)
        B_ineq.append(chooses[index - 1]['tokens'])
    index2 = 0
    for j in range(students): #this appends the courses for each student
        emptyList = [0 for i in range(length)]
        for k in range(5):
            emptyList[index2] = -1
            index2 += 1
        A_ineq.append(emptyList)
        B_ineq.append(-1)
    for k in indexDict:
        emptyList = [0 for i in range(length)]
        for i in indexDict[k]:
            emptyList[i] = 1
            temp = i
        A_ineq.append(emptyList)
        B_ineq.append(chooses[i]['capacity'])
    return [A_ineq, B_ineq]

def LP_det_avg(chooses, students, length):
    ineq = create_Ineq(chooses, students, length)
    A_ineq = ineq[0]
    B_ineq = ineq[1]
    c = [0. for i in range(len(A_ineq))]
    index = 0
    for i in range(students):
        x = 1
        for j in range(5):
            c[index] = x
            x += 0.1
            index += 1
    LPSolution = linprog(c, A_ub=A_ineq, b_ub=B_ineq, method='interior-point')
    LPSum = 0
    totalSeatsOffered = 0
    solutionSet = []
    for value in LPSolution['x']: 
        LPSum += value
    LP_avg = LPSum/len(LPSolution['x'])
    counter = 0
    for value in LPSolution['x']:
        if value >= LP_avg:
            value = 1  
            totalSeatsOffered += 1          
        if value < LP_avg:
            value = 0
        decision = [chooses[counter]['student'], chooses[counter]['course'], value]
        solutionSet.append(decision)
        counter += 1
    print("RESULTS FOR DETERMINISTIC ROUNDING (Threshold = Average LP Value): ")
    print("Solution set format: [student, course, assignment status]")
    print("Solution set: ", solutionSet)
    #print("LPSum: ", LPSum)
    print("Total number of seats offered: ", totalSeatsOffered)
    print(" ")
    return solutionSet

def readSolutionSet(solSet, conn):
    curs = dbi.dict_cursor(conn)
    for i in solSet:
        if i[2] == 1:
            uid = i[0]
            course = i[1]
            curs.execute('''insert into assignments (uid, course) values %s, %s''', [uid, course])