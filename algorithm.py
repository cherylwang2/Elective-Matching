#need to import numpy
from scipy.optimize import linprog
import numpy as np

#created from inner join chooses with courses on chooses.course = courses.courseid
def create_Ineq(chooses, students, length): #make sure chooses sorts students by ASC
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
            emptyList[index2] = 1
            index2 += 1
        A_ineq.append(emptyList)
        B_ineq.append(1)
    for k in indexDict:
        emptyList = [0 for i in range(length)]
        for i in indexDict[k]:
            emptyList[i] = 1
            temp = i
        A_ineq.append(emptyList)
        B_ineq.append(chooses[i]['capacity'])
    #print(A_ineq)
    #print(B_ineq)
    lenA = len(A_ineq)
    ineq = [lenA]
    ineq += A_ineq
    ineq += B_ineq
    return ineq

#A_ineq = [1:ineq[0]]
#B_ineq = [ineq[0]:]