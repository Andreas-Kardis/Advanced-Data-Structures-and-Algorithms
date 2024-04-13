import sys
import numpy as np
import copy

def readInformation(inputFile: str):
    """
    This function reads the information from the input file in the expected formation. 
    It converts the information into matrix and vector representations to later be used 
    in the tableau simplex function.
    """
    file = open(inputFile, 'r')
    # read number of decision variables
    next(file)
    numDecisionVariables = int(file.readline())

    # read number of constraints
    next(file)
    numConstraints = int(file.readline())

    # read objective returns
    next(file)
    objective = np.zeros(numDecisionVariables + numConstraints)
    readObjectives = file.readline().split(',')
    for i in range(numDecisionVariables):
        objective[i] = int(readObjectives[i])

    # read constraints LHS matrix
    next(file)
        # create a list to hold all non-basic and basic variables
    constraintsLHS = np.zeros((numConstraints, numDecisionVariables + numConstraints))

    row = 0
    for col in range(numDecisionVariables, numDecisionVariables + numConstraints):
        constraintsLHS[row][col] = 1
        row += 1
    
    for i in range(numConstraints):
        cLHS = file.readline().split(',')
        for j in range(numDecisionVariables):
            constraintsLHS[i][j] = int(cLHS[j])

    # read constraints RHS vector
    next(file)
    constraintsRHS = np.zeros(numConstraints)
    for i in range(numConstraints):
        constraintsRHS[i] = int(file.readline())

    file.close()

    return numDecisionVariables, numConstraints, objective, constraintsLHS, constraintsRHS

def tableauSimplex(numDecisionVariables, numConstraints, objective, constraintsLHS, constraintsRHS):
    """
    This function uses the tableau simplex algorithm to solve a linear program in its standard form.
    objective is the values to maximise.
    constraintsLHS is the left hand side of the constraints
    constraintsRHS is the ≤ number of the right hand side of the constraints
    """
    # list of the indexes of the basic variable for each constraint
    basicVariables = np.arange(numDecisionVariables, numConstraints + numDecisionVariables)

    # find the index of the max positive value in objective 
    maxObjective = np.argmax(objective)

    original_objective = copy.deepcopy(objective)
    maxVal = 0

    # perform the body of the algorithm until the max value has been found
    while objective[maxObjective] > 0:     
        # select variable to enter the basis
        theta = np.zeros(numConstraints)
        for constraint in range(numConstraints):
            theta[constraint] = constraintsRHS[constraint] / constraintsLHS[constraint][maxObjective]

        # choose the minimum positive value of theta as the new basic variable for that constraint
        minTheta = np.where(theta > 0, theta, np.inf).argmin()

        # update list of basic variables
        basicVariables[minTheta] = maxObjective

        # re-write the constraints in terms of the new non-basic variables
        coeff_to_divide = constraintsLHS[minTheta][maxObjective]
        constraintsRHS[minTheta] = constraintsRHS[minTheta] / coeff_to_divide
        for variable in range(constraintsLHS.shape[1]):
            constraintsLHS[minTheta][variable] = constraintsLHS[minTheta][variable] / coeff_to_divide

        # for all other constraints containing the new basic variable
        for constraint in range(numConstraints):
            if constraint == minTheta:
                continue

            constraintsRHS[constraint] -= constraintsLHS[constraint][basicVariables[minTheta]] * constraintsRHS[minTheta]

        # update all variables on each constraint line
        for constraint in range(numConstraints):
            if constraint == minTheta:
                continue

            # coefficient of the max variable in other constraint lines
            coeff = constraintsLHS[constraint][maxObjective]

            # calculate new value for each variable in the constraint line
            for variable in range(constraintsLHS.shape[1]):
                constraintsLHS[constraint][variable] -= coeff * constraintsLHS[minTheta][variable]
                
        # update objective
        for variable in range(constraintsLHS.shape[1]):
            sum = 0
            for constraint in range(numConstraints):
                sum += original_objective[basicVariables[constraint]] * constraintsLHS[constraint][variable]

            objective[variable] = original_objective[variable] - sum

        # update new max return
        tmpMaxVal = 0
        for constraint in range(constraintsRHS.shape[0]):
            tmpMaxVal += original_objective[basicVariables[constraint]] * constraintsRHS[constraint]

        maxVal = tmpMaxVal
        print(maxVal)

        # find the new index of the max positive value in objective 
        maxObjective = np.argmax(objective)

    # save optimal values for decision variables
    optDecValues = np.zeros(numDecisionVariables)
    for i in range(basicVariables.shape[0]):
        if basicVariables[i] < numDecisionVariables:
            print(i)
            optDecValues[basicVariables[i]] = constraintsRHS[i]

    return optDecValues, maxVal


if __name__ == "__main__":
    _, inputFile = sys.argv

    # read the input file
    numDecisionVariables, numConstraints, objective, constraintsLHS, constraintsRHS = readInformation(inputFile)

    # run tableau simplex
    optDecValues, maxVal = tableauSimplex(numDecisionVariables, numConstraints, objective, constraintsLHS, constraintsRHS)

    # convert the optimal value of the decision variables found into the output string format
    output_decValues = "{:.1f}".format(optDecValues[0])
    for i in range(1, optDecValues.shape[0]):
        output_decValues += ', ' + "{:.1f}".format(optDecValues[i])

    # write soltuion to lpsolution.txt
    file = open('lpsolution.txt', 'w')
    file.write('# optimalDecisions\n')
    file.write(output_decValues + '\n')
    file.write('# optimalObjective\n{:.1f}'.format(maxVal))
    file.close()



