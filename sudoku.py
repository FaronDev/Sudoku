from random import choice, shuffle, randint
from time import sleep

#┏━━━┓╋╋╋╋┏┓╋╋┏┓
#┃┏━┓┃╋╋╋╋┃┃╋╋┃┃
#┃┗━━┳┓┏┳━┛┣━━┫┃┏┳┓┏┓
#┗━━┓┃┃┃┃┏┓┃┏┓┃┗┛┫┃┃┃
#┃┗━┛┃┗┛┃┗┛┃┗┛┃┏┓┫┗┛┃
#┗━━━┻━━┻━━┻━━┻┛┗┻━━┛

class Sudoku:

  possible_values = [1,2,3,4,5,6,7,8,9]
  
  def __init__(self): #Initializes the sudoku by creating a blank one
    self.grid = [[0 for j in range(9)] for i in range(9)] #Sudoku grid

  ##################
  #  GRID METHODS  #
  ##################

  def clear(self): #Clears the sudoku
    self.grid = [[0 for j in range(9)] for i in range(9)]

  def get_row(self, row, grid=None): #Gets the values present in the requested row (list)[0-8]
    if grid == None:
      grid = self.grid
    return grid[row]

  def get_col(self, col, grid=None): #Gets the values present in the requested column (list)[0-8]
    if grid == None:
      grid = self.grid
    return [x[col] for x in grid]

  def get_box(self, box, grid=None): #Gets the values present in the requested 3x3 box (list)[0-2][0-2]
    if grid == None:
      grid = self.grid

    vals = []
    for i in range(3):
      for j in range(3):
        vals.append(grid[(box[0]*3)+i][(box[1]*3)+j])

    return vals

  def set_cell(self, cell, value): #Sets the value of the cell
    if len(cell) == 2:
      if cell[0] >= 0 and cell[0] <= 8 and cell[1] >= 0 and cell[1] <= 8:
        if value >= 0 and value <= 9:
          if self.grid[cell[0]][cell[1]] == 0:
            self.grid[cell[0]][cell[1]] = value
          else:
            print('Already filled')
        else:
          print('Incorrect value')
      else:
        print('Cell values not possible')
    else :
      print('Incorrect cell location')

  def set_box(self, box, loc):

    for i in range(3):
      for j in range(3):
        self.grid[(loc[0]*3)+i][(loc[1]*3)+j] = box[i*3 + j] 

  def check_errors(self):

    errors = []

    for row in range(9):
      res_row = self.get_row(row)
      res_row = [i for i in res_row if i != 0]

      if len(res_row) != len(set(res_row)):
        errors.append(("row", row))

    for col in range(9):
      res_col = self.get_col(col)
      res_col = [i for i in res_col if i != 0]

      if len(res_col) != len(set(res_col)):
        errors.append(("col", col))

    for box_row in range(3):
      for box_col in range(3):
        res_box = self.get_box((box_row, box_col))
        res_box = [i for i in res_box if i != 0]

        if len(res_box) != len(set(res_box)):
          errors.append(("box", (box_row, box_col)))


    return errors

  def verify(self):

    for row in range(9):
      res_row = list(set(self.get_row(row)))
      if res_row != self.possible_values:
        print(f'Doesnt follow rules in row {row+1}')
        return False, ("row", row+1)

    for col in range(9):
      res_col = list(set(self.get_col(col)))
      if res_col != self.possible_values:
        print(f'Doesnt follow rules in col {col+1}')
        return False, ("col", col+1)

    for i in range(3):
      for j in range(3):
        res_box = list(set(self.get_box([i,j])))
        if res_box != self.possible_values:
          print(f'Doesnt follow rules in box {i*3 + j}')
          return False, ("box", i*3 + 1)

    return True, ()

  def get_grid(self):
    return [[self.grid[i][j] for j in range(len(self.grid[i]))] for i in range(len(self.grid))]

  def set_grid(self, grid):

    self.clear()
    for row in range(9):
      for col in range(9):
        self.grid[row][col] = grid[row][col]

  ###################
  #    GENERATOR    #
  ###################
      
  def generate(self, cell = (0,0)): #Generates a valid sudoku with all cells filled
    row = cell[0]
    col = cell[1]
    res_row = set(self.get_row(row))
    res_col = set(self.get_col(col))
    res_box = set(self.get_box((row//3, col//3)))

    not_pos_vals = res_row.union(res_col.union(res_box))
    pos_vals = set(self.possible_values) - not_pos_vals
    
    
    if len(pos_vals) != 0:
      pos_vals = list(pos_vals)
      shuffle(pos_vals)
      for num in pos_vals:      
        self.grid[row][col] = num

        new_cell = cell

        if new_cell == (8,8):
          return True
        else:
          if col == 8:
            new_cell = (row + 1, 0)
          else:
            new_cell = (row, col + 1)
            
        if self.generate(new_cell):
          return True
      self.grid[row][col] = 0 #The line that changed my day
      return False

  ##################
  #     SOLVER     #
  ##################

  def solve(self, grid=None): #Solves the sudoku for you | Solution: Use the algorithm of the sudoku generator and modify it to use only the blank cells
    
    if grid == None:
      grid = self.grid

    new_cell = (0,0)
    
    while True:
      
      n_row = new_cell[0]
      n_col = new_cell[1]

      if grid[n_row][n_col] == 0:
        break

      if new_cell == (8,8):
        return True
      else:
        if n_col == 8:
          new_cell = (n_row + 1, 0)
        else:
          new_cell = (n_row, n_col + 1)

    solved, grid = self.__solve(grid, new_cell)
    if solved:
      return True, grid
    else:
      return False, None

  def __solve(self, grid, cell):

    row = cell[0]
    col = cell[1]
    res_row = set(self.get_row(row, grid))
    res_col = set(self.get_col(col, grid))
    res_box = set(self.get_box((row//3, col//3), grid))

    not_pos_vals = res_row.union(res_col.union(res_box))
    pos_vals = set(self.possible_values) - not_pos_vals
    
    if len(pos_vals) != 0:
      pos_vals = list(pos_vals)
      shuffle(pos_vals)
      for num in pos_vals:      
        grid[row][col] = num

        # self.display_console() # Too see how to algorithm works
        # sleep(0.05)

        new_cell = cell

        while True:
          
          n_row = new_cell[0]
          n_col = new_cell[1]

          if new_cell == (8,8):
            return True, grid
          else:
            if n_col == 8:
              new_cell = (n_row + 1, 0)
            else:
              new_cell = (n_row, n_col + 1)

          if grid[new_cell[0]][new_cell[1]] == 0:
            break
           
        solved, grid = self.__solve(grid, new_cell)
        if solved:
          return True, grid

      grid[row][col] = 0 #The line that changed my day
      return False, grid

    return False, grid

  def setDifficulty(self, hardness = 1): #Create a sudoku with many solutions | Hardness from 1 - 4

    if hardness > 4 or hardness < 1:
      return "Only accept hardness values from 1 - 4"

    box_locations = [[i, j] for i in range(3) for j in range(3)]
    
    for loc in box_locations: # Taking each box
      box = self.get_box(loc)
      indexes = [i for i in range(9)]

      for i in range(randint(hardness + 1, hardness + 4)): # Removing a set no of elements from the box
        index = choice(indexes)                            # Based on hardness
        del indexes[indexes.index(index)]

        box[index] = 0

      self.set_box(box, loc) # Setting the values into the sudoku


  ###################
  # DISPLAY METHODS #
  ###################

  def display_console(self, board = None): #Displays the sudoku

    if board is None:
      board = self.grid[:]
    
    for i in range(9):
      for j in range(9):
        if board[i][j] == 0:
          board[i][j] = '-' 

    print('┏━━━━━━━┳━━━━━━━┳━━━━━━━┓')
    for i in range(9):
      print(f'┃ {board[i][0]} {board[i][1]} {board[i][2]} ┃ {board[i][3]} {board[i][4]} {board[i][5]} ┃ {board[i][6]} {board[i][7]} {board[i][8]} ┃')
      if i%3 == 2 and i != 8:
        print('┣━━━━━━━╋━━━━━━━╋━━━━━━━┫')
    print('┗━━━━━━━┻━━━━━━━┻━━━━━━━┛')

    for i in range(9):
      for j in range(9):
        if board[i][j] == '-':
          board[i][j] = 0


if __name__ == '__main__':
  game = Sudoku()
  game.generate()
  game.setDifficulty(3)
  game.display_console()
  sleep(5)
  game.solve()
  game.display_console()
  print('Done')