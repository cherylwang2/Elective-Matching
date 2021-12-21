#need to import numpy
from scipy.optimize import linprog
import numpy as np
import cs304dbi as dbi
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)

def create_Ineq(chooses, students, length):
    #assumes each student chooses 5 classes
    '''chooses is curs object being returned, students is num students, length is length of array'''
    print(chooses)
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
            if chooses[index]['courseWeight'] == 'None' or chooses[index]['courseWeight'] == None:
                emptyList[index] = 0
            else:
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
    for k in indexDict: #this makes sure capacity is not exceeded
        emptyList = [0 for i in range(length)]
        for i in indexDict[k]:
            emptyList[i] = 1
            temp = i
        A_ineq.append(emptyList)
        B_ineq.append(chooses[i]['capacity'])
    return [A_ineq, B_ineq]

def LP_det_avg(chooses, students, length):
    print("students", students)
    ineq = create_Ineq(chooses, students, length)
    A_ineq = ineq[0]
    print(A_ineq)
    B_ineq = ineq[1]
    print(B_ineq)
    c = [0. for i in range(students * 5)]
    index = 0
    for i in range(students):
        print(c)
        x = 1
        for j in range(5):
            print(index)
            c[index] = x
            x += 0.25 #incentivizes algorithm to give students their top choice by making latter choices weigh more (minimization problem)
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
    curs.execute('''delete from assignments''')
    conn.commit()
    for i in solSet:
        if i[2] == 1:
            uid = i[0]
            course = i[1]
            curs.execute('''insert into assignments (uid, course) values (%s, %s)''', [uid, course])
            conn.commit()
    flash('Students assigned successfully!')