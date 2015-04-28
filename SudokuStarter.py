#!/usr/bin/env python
import struct, string, math, copy

class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""

    def __init__(self, size, board):
        """the constructor for the SudokuBoard"""
        self.BoardSize = size #the size of the board
        self.squareSize=int(math.sqrt(self.BoardSize))
        self.CurrentGameBoard= board #the current state of the game board
        # The number of new constraints that will be created IF a new number is being added to this tile.
        # The number will be negative if the tile already has a number.
        self.BoardConstraintsNum=[ [ ((self.BoardSize-1)*2+(self.squareSize-1)**2) for i in range(self.BoardSize) ] for j in range(self.BoardSize) ]
        # The list of possible numbers that can go into this tile
        self.PossibleNum=[ [ [ (i+1) for i in range(self.BoardSize) ] for j in range(self.BoardSize) ] for k in range(self.BoardSize) ]

    def set_value(self, row, col, value):
        """This function will CHANGE the sudoku board object with the input
        value placed on the GameBoard row and col are both zero-indexed"""
        # It will return true if successfully set the value, false if there's a tile that has no possible values after setting the new value.
        # If the tile is already occupied with another value, return false
        if (not self.CurrentGameBoard[row][col]==0):
            return False
        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        # Change the constraint number for this tile to -1 to indicate that this tile has already been filled
        self.BoardConstraintsNum[row][col]=-1
        # Change the possible numbers of the tiles that are in the same row/column/square as the tile.
        # Also change the BoardConstraintsNum of all tiles affected by the newly added tile
        for i in range(0,self.BoardSize):
            if value in self.PossibleNum[i][col]:
                self.PossibleNum[i][col].remove(value)
            #if one of the tile in the same column no longer have any possible values.
            # Note: I did not choose to reverse the changes here. I think I could create a copy of the sudoku every time I call set_value to avoid reversing changes.
            if self.PossibleNum[i][col]==[] and self.CurrentGameBoard[i][col]==0:
                # print "can't set "+str(value)+" in "+str([row,col])+" because "+str([i,col])+"has no other option then"
                return False
            # Change BoardConstraintsNum
            self.BoardConstraintsNum[i][col]-=1
            if value in self.PossibleNum[row][i]:
                self.PossibleNum[row][i].remove(value)
            if self.PossibleNum[row][i]==[] and self.CurrentGameBoard[row][i]==0:
                # print "can't set "+str(value)+" in "+str([row,col])+" because "+str([row,i])+"has no other option then"
                return False
            # Change BoardConstraintsNum
            self.BoardConstraintsNum[row][i]-=1
        #set the top-left corner of the square the new value fall in
        blockTopLeftCorner=((row/self.squareSize)*self.squareSize,(col/self.squareSize)*self.squareSize)
        for i in range(blockTopLeftCorner[0],blockTopLeftCorner[0]+self.squareSize):
            for j in range(blockTopLeftCorner[1],blockTopLeftCorner[1]+self.squareSize):
                if value in self.PossibleNum[i][j]:
                    self.PossibleNum[i][j].remove(value)
                if self.PossibleNum[i][j]==[] and self.CurrentGameBoard[i][j]==0:
                    return False
                # Change BoardConstraintsNum if it has not been changed yet.
                # That is, if it's not in the same column or row
                if i!=row and j!=col:
                    self.BoardConstraintsNum[i][j]-=1
        #remove all possible values from the tile that we are setting value for
        self.PossibleNum[row][col]=[]

        #Now we will check whether a tile has only one possible value. If so, set that value and return false if we can't set that value
        for i in range(0,self.BoardSize):
            if len(self.PossibleNum[i][col])==1:
                if (not self.set_value(i,col,self.PossibleNum[i][col][0])):
                    return False
            if len(self.PossibleNum[row][i])==1:
                if (not self.set_value(row,i,self.PossibleNum[row][i][0])):
                    return False
        for i in range(blockTopLeftCorner[0],blockTopLeftCorner[0]+self.squareSize):
            for j in range(blockTopLeftCorner[1],blockTopLeftCorner[1]+self.squareSize):
                if len(self.PossibleNum[i][j])==1:
                    if (not self.set_value(i,j,self.PossibleNum[i][j][0])):
                        return False

        #return true if the sudoku is still solvable after we added all the values.
        return True


    def print_board(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for i in range(div):
            dash += "----"
            space += "    "
        for i in range(div):
            line += dash + "+"
            sep += space + "|"
        for i in range(-1, self.BoardSize):
            if i != -1:
                print "|",
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] > 9:
                        print self.CurrentGameBoard[i][j],
                    elif self.CurrentGameBoard[i][j] > 0:
                        print "", self.CurrentGameBoard[i][j],
                    else:
                        print "  ",
                    if (j+1 != self.BoardSize):
                        if ((j+1)//div != j/div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((i+1)//div != i/div):
                print line
            else:
                print sep


def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
    the value of each cell. Array elements holding a 0 are considered to be
    empty."""

    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]
    #initialize a blank sudoku
    sudoku=SudokuBoard(len(board), board)

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        if not val==0:
            sudoku.set_value(row-1,col-1,val)

    return sudoku

def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
    correctly."""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    #check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if BoardArray[row][col]==0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
                            == BoardArray[row][col])
                       and (SquareRow*subsquare + i != row)
                       and (SquareCol*subsquare + j != col)):
                        return False
    return True


def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    return parse_file(file_name)


def solve(initial_board, forward_checking, MRV, MCV, LCV):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """

    # MRV and MCV cannot be used simultaneously
    if MRV == True and MCV == True:
        print "Error! MRV and MCV cannot be used simultaneously."
        return

    return backTrack(initial_board, forward_checking, MRV, MCV, LCV)


def backTrack(initial_board, forward_checking, MRV, MCV, LCV):
    # print "one call"
    if is_complete(initial_board):
        return initial_board
    size = initial_board.BoardSize  # length of the board

    if forward_checking == False:
        nextRow = -1    # nextRow and nextCol hold the index of the next tile to be assigned
        nextCol = -1

        # if neither MRV nor MCV is used, use the first empty tile as next assignment
        if not (MRV or MCV):
            for row in range(size):
                for col in range(size):
                    if initial_board.CurrentGameBoard[row][col] == 0:
                        if not initial_board.PossibleNum[row][col]:
                            return False
                        else:
                            nextRow, nextCol = row, col

        # else if MRV is used, use the tile that has minimum remaining value as the next assignment
        elif MRV:
            currentMin = size   # the number of least remaining values seen so far
            for row in range(size):
                for col in range(size):
                    if initial_board.CurrentGameBoard[row][col] == 0 and len(initial_board.PossibleNum[row][col]) < currentMin:
                        if not initial_board.PossibleNum[row][col]:
                            return False
                        else:
                            nextRow, nextCol = row, col

        # else if MCV is used, use the tile that is is involved in the largest number of constraints with other unassigned variables as the next assignment
        elif MCV:
            currentMax = size   # the number of most constraints seen so far
            for row in range(size):
                for col in range(size):
                    if initial_board.CurrentGameBoard[row][col] == 0 and initial_board.BoardConstraintsNum[row][col] > currentMax:
                        if not initial_board.PossibleNum[row][col]:
                            return False
                        else:
                            nextRow, nextCol = row, col

        valueToAssignList = []

        # if LCV is used, choose the value to that rules out the fewest choices for the neighboring values to assign
        if LCV:
            valueToAssignList = orderDomainValues(initial_board, [nextRow, nextCol])
        # if LCV is not used,choose the first possible value to assign
        else:
            valueToAssignList = initial_board.PossibleNum[nextRow][nextCol]

        # print "nextRow, nextCol, val: " + str(nextRow)+" "+str(nextCol)+" "+str(valueToAssignList)

        for val in valueToAssignList:
            boardCopy = copy.deepcopy(initial_board)
            boardCopy.set_value(nextRow, nextCol, val)
            # print "nextRow, nextCol, val: " + str(nextRow)+" "+str(nextCol)+" "+str(val)
            result = backTrack(boardCopy, forward_checking, MRV, MCV, LCV)
            if result != False:
                return result
            # else:
            #     initial_board.PossibleNum[nextRow][nextCol].remove(val)
        return False

    else:
        print "forward_checking not implemented yet"


# helper function for backtrack, returns the list of values to assign for a tile in the order of LCV
def orderDomainValues(board, rowAndColList):
    size = board.BoardSize
    nextRow = rowAndColList[0]
    nextCol = rowAndColList[1]
    result = []
    valueDic = {}   # {value: constrainedNum}
    for value in board.PossibleNum[nextRow][nextCol]:
        currentConstrained = 0  # ruled-out by the current value
        for i in range(0, size):
            # count the ruled-out in the respective column
            if value in board.PossibleNum[i][nextCol]:
                currentConstrained += 1
            # count the ruled-out in the respective row
            if value in board.PossibleNum[nextRow][i]:
                currentConstrained += 1

        topLeftRow = int(nextRow - nextRow % math.sqrt(size))    # row index of the top left tile of the sub-box
        topLeftCol = int(nextCol - nextCol % math.sqrt(size))    # colomn index of the top left tile of the sub-box
        # count the ruled-out in the respective sub-box
        for i in range(topLeftRow, int(topLeftRow + math.sqrt(size))):
            for j in range(topLeftCol, int(topLeftCol + math.sqrt(size))):
                if value in board.PossibleNum[i][j]:
                    currentConstrained += 1
        valueDic[value] = currentConstrained

    #sort valueDic based on constrainedNum
    result = sorted(valueDic.keys(), key=valueDic.__getitem__)
    return result

















# def solve(initial_board, forward_checking, MRV, MCV,
#           LCV):
#     """Takes an initial SudokuBoard and solves it using back tracking, and zero
#     or more of the heuristics and constraint propagation methods (determined by
#     arguments). Returns the resulting board solution. """
#     # print "Your code will solve the initial_board here!"
#     # print "Remember to return the final board (the SudokuBoard object)."
#     # print "I'm simply returning initial_board for demonstration purposes."
#
#     size = initial_board.BoardSize  # length of the board
#
#     # MRV and MCV cannot be used simultaneously
#     if MRV == True and MCV == True:
#         print "Error! MRV and MCV cannot be used simultaneously."
#         return
#
#     if forward_checking == False:
#         nextRow = -1    # nextRow and nextCol hold the index of the next tile to be assigned
#         nextCol = -1
#         assignmentHistory = [0]  # list that contains lists of assignment in the order [row, col, value]
#         # while there is empty tile to fill
#         while not is_complete(initial_board):
#             # if there's no board to backtrack to, this initial board is unsolvable
#             if not assignmentHistory:
#                 return False
#             breakDoubleLoop = False     # indicate whether to break the double loop
#             continueWhileLoop = False      # indicate whether to break the double loop
#             # if neither MRV nor MCV is used, use the first empty tile as next assignment
#             if not (MRV or MCV):
#                 for row in range(size):
#                     for col in range(size):
#                         if initial_board.CurrentGameBoard[row][col] == 0:
#                             print [row, col]
#                             # if there's no possible number left for this tile, need to backtrack
#                             if not initial_board.PossibleNum[row][col]:
#                                 print "backtrack!"
#                                 backTrackStep = assignmentHistory.pop()
#                                 initial_board.reset_value(backTrackStep[0], backTrackStep[1], backTrackStep[2])
#                                 breakDoubleLoop = True
#                                 continueWhileLoop = True
#                                 break
#                             else:
#                                 nextRow, nextCol = row, col
#                                 print "nextRow, nextCol: " + str(nextRow) + " " + str(nextCol)
#                                 breakDoubleLoop = True
#                                 break
#                     if breakDoubleLoop:
#                         break
#
#             # else if MRV is used, use the tile that has minimum remaining value as the next assignment
#             elif MRV:
#                 currentMin = size   # the number of least remaining values seen so far
#                 for row in range(size):
#                     for col in range(size):
#                         if initial_board.CurrentGameBoard[row][col] == 0 and initial_board.PossibleNum[row][col] < currentMin:
#                             # if there's possible number left for this tile, need to backtrack
#                             if not initial_board.PossibleNum[row][col]:
#                                 backTrackStep = assignmentHistory.pop()
#                                 initial_board.reset_value(backTrackStep[0], backTrackStep[1], backTrackStep[2])
#                                 breakDoubleLoop = True
#                                 continueWhileLoop = True
#                                 break
#                             else:
#                                 nextRow, nextCol = row, col
#                                 breakDoubleLoop = True
#                                 break
#                     if breakDoubleLoop:
#                         break
#             # # else if MCV is used, use the tile that is is involved in the largest number of constraints with other unassigned variables as the next assignment
#             # elif MCV:
#             #     currentMax = size   # the number of most constraints seen so far
#             #     for row in range(size):
#             #         for col in range(size):
#             #             if initial_board.CurrentGameBoard[row][col] == 0 and initial_board.BoardConstraintsNum[row][col] > currentMax:
#             #                 # if there's possible number left for this tile, need to backtrack
#             #                 if not initial_board.PossibleNum[row][col]:
#             #                     backTrackStep = assignmentHistory.pop()
#             #                     initial_board.reset_value(backTrackStep[0], backTrackStep[1], backTrackStep[2])
#             #                     continue
#             #                 else:
#             #                     nextRow, nextCol = row, col
#             #                     break
#
#             if continueWhileLoop:
#                 continue
#
#             valueToAssign = -1  # the value to assign eventually
#             # if LCV is used, choose the value to that rules out the fewest choices for the neighboring values to assign
#             if LCV:
#                 leastConstrainedNum = size ^ 2     # number of the least ruled-out seen so far
#                 currentConstrained = 0      # ruled-out by the current value
#                 for value in initial_board.PossibleNum[nextRow][nextCol]:
#                     # count the ruled-out in the respective column
#                     for i in range(0, size):
#                         if value in initial_board.PossibleNum[i][nextCol]:
#                             currentConstrained += 1
#                     # count the ruled-out in the respective row
#                     for j in range(0, size):
#                         if value in initial_board.PossibleNum[row][j]:
#                             currentConstrained += 1
#
#                     topLeftRow = nextRow - nextRow % math.sqrt(size)    # row index of the top left tile of the sub-box
#                     topLeftCol = nextCol - nextCol % math.sqrt(size)    # colomn index of the top left tile of the sub-box
#                     # count the ruled-out in the respective sub-box
#                     for i in range(topLeftRow, topLeftRow + math.sqrt(size) + 1):
#                         for j in range(topLeftCol, topLeftCol + math.sqrt(size) + 1):
#                             if value in initial_board.PossibleNum[i][j] and i != nextRow and j != nextCol:
#                                 currentConstrained += 1
#                     # if the value being tested rules out fewer other number than the least seen so far, use this value for assignment
#                     if currentConstrained < leastConstrainedNum:
#                         valueToAssign = value
#             # if LCV is not used,choose the first possible value to assign
#             else:
#                 print "possibleNum: " + str(initial_board.PossibleNum[nextRow][nextCol])
#                 valueToAssign = initial_board.PossibleNum[nextRow][nextCol][0]
#
#
#             assignmentHistory.append([nextRow, nextCol, valueToAssign])
#             print assignmentHistory
#             initial_board.set_value(nextRow, nextCol, valueToAssign)
#             # initial_board.print_board()
#
#     else:
#         print "forward checking not implemented yet"
#         return initial_board




    #     # helper function for solve: basically the reversal of set_value, but no reversal on removing the appropriate value in possibleNum
    # def reset_value(self, row, col, value):
    #     """This function will CHANGE the sudoku board object with the input
    #     value placed on the GameBoard row and col are both zero-indexed"""
    #     self.CurrentGameBoard[row][col] = 0
    #     self.BoardConstraintsNum[row][col] = 0
    #     # Change the possible numbers of the tiles that are in the same row/column/square as the tile.
    #     # Also change the BoardConstraintsNum of all tiles affected by the newly reset tile
    #     for i in range(0, self.BoardSize):
    #         if i != row:
    #             self.reAddPossibleNum(i, col, value)
    #             # Change BoardConstraintsNum
    #             if self.CurrentGameBoard[i][col] == 0:
    #                 self.BoardConstraintsNum[row][col] += 1
    #                 self.BoardConstraintsNum[i][col] += 1
    #         if i != col:
    #             self.reAddPossibleNum(row, i, value)
    #             # Change BoardConstraintsNum
    #             if self.CurrentGameBoard[row][i] == 0:
    #                 self.BoardConstraintsNum[row][col] += 1
    #                 self.BoardConstraintsNum[row][i] += 1
    #     topLeftRow = row - row % self.squareSize   # row index of the top left tile of the sub-box
    #     topLeftCol = col - col % self.squareSize    # colomn index of the top left tile of the sub-box
    #     for i in range(topLeftRow, topLeftRow + self.squareSize):
    #         for j in range(topLeftCol, topLeftCol + self.squareSize):
    #             if i!=row and j!=col:
    #                 self.reAddPossibleNum(i, j, value)
    #                 if self.CurrentGameBoard[i][j] == 0:
    #                     self.BoardConstraintsNum[i][j] += 1
    #                     self.BoardConstraintsNum[row][col] += 1
    #     #reset the possibleNum for tile [row][col], but with the last tried value removed
    #     # for val in range(1, self.BoardSize + 1):
    #     #     self.reAddPossibleNum(row, col, val)
    #     # if value in self.PossibleNum[row][col]:
    #     #     # print "found it!"
    #     #     self.PossibleNum[row][col].remove(value)
    #
    #     self.noAddToPossibleNum[row][col].append(value)
    #
    # # helper function for reset_value: add the value back to possibleNum of a specific tile when appropriate
    # def reAddPossibleNum(self, row, col, value):
    #     # if PossibleNum already contain value, don't add
    #     if value in self.PossibleNum[row][col]:
    #         return
    #     if value in self.noAddToPossibleNum[row][col]:
    #         return
    #     addValue = True    # whether to add this value back to possibleNum at the end
    #     for i in range(self.BoardSize):
    #         if i != row and value == self.CurrentGameBoard[i][col]:
    #             addValue = False
    #             # print "can't add " + str(value) + " to PossibleNum because it has been found in " + str([i, col])
    #             break
    #         if i != col and value == self.CurrentGameBoard[row][i]:
    #             addValue = False
    #             # print "can't add " + str(value) + " to PossibleNum because it has been found in " + str([row, i])
    #             break
    #     topLeftRow = row - row % self.squareSize   # row index of the top left tile of the sub-box
    #     topLeftCol = col - col % self.squareSize    # colomn index of the top left tile of the sub-box
    #     for i in range(topLeftRow, topLeftRow + self.squareSize):
    #         for j in range(topLeftCol, topLeftCol + self.squareSize):
    #             if value == self.CurrentGameBoard[i][j] and i != row and j != col:
    #                 addValue = False
    #                 break
    #     if addValue:
    #         self.PossibleNum[row][col].append(value)