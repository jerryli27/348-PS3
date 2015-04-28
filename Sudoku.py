__author__ = 'Alan and Jerry'
import SudokuStarter

# board=SudokuStarter.init_board("input_puzzles/easy/16_16.sudoku")
board=SudokuStarter.init_board("input_puzzles/more/25x25/25x25.1.sudoku")
board.print_board()
# print board.PossibleNum[0][1]
# board.set_value(0,1,6)
# print board.PossibleNum[0][1]
# board.reset_value(0,1,6)
# print board.PossibleNum[0][1]

# board.reAddPossibleNum(0,1,1)
# print board.BoardConstraintsNum[1][0]
# board.set_value(0,0,1)
# board.print_board()

a = SudokuStarter.solve(board, False, True, False, True)
a.print_board()
# a.print_board()
# board.set_value(3,3,1)
# print board.CurrentGameBoard[3][3]