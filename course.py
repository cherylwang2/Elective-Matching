def inDescOrder(courses):
    for i in range(len(courses) - 1):
        if courses[i] > courses[i+1]:
            return False
    return True