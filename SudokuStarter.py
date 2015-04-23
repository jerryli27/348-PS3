#!/usr/bin/env python
import struct, string, math

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
                return False
            # Change BoardConstraintsNum
            self.BoardConstraintsNum[i][col]-=1
            if value in self.PossibleNum[row][i]:
                self.PossibleNum[row][i].remove(value)
            if self.PossibleNum[row][i]==[] and self.CurrentGameBoard[row][i]==0:
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


def solve(initial_board, forward_checking = False, MRV = False, MCV = False,
    LCV = False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """
    print "Your code will solve the initial_board here!"
    print "Remember to return the final board (the SudokuBoard object)."
    print "I'm simply returning initial_board for demonstration purposes."




