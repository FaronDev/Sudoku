from random import choice, shuffle, randint
from time import sleep
import threading
from tkinter import *
from tkinter import ttk

from sudoku import Sudoku

#################
#     CLASS     #
#################

class App(Sudoku):

	# Colors and sizes
	btn_color = "#F0F0F0"
	btn_select_color = "#505050"
	btn_hover_color = "#A0AFAE"
	btn_fixed_color = "#E0E0E0"
	btn_error_color = "#EE7777"
	btn_fixed_error_color = "#CC7777"
	#For show_algorithm function
	btn_solved_color = "#77EE77"
	btn_fixed_solved_color = "#77CC77"
	btn_solving_color = "#77FFFF"

	cell_borderWidth = 1
	box_borderWidth = 3 #+1

	def __init__(self, title, size, bg_color): # Size = (width, height)
		super().__init__()

		# Inititalizes the tkinter window
		self.win = Tk()
		self.win.title(title)
		self.size = size
		self.win.geometry(f'{self.size[0]}x{self.size[1]}+450+100')
		self.win.minsize(self.size[0], self.size[1])
		self.win.maxsize(self.size[0], self.size[1])
		self.win.configure(background = bg_color)
		self.style = ttk.Style()

		self.sudoku_grid = None # The grid that contains all the cells
		self.footer = None # Contains the status label (WIP)
		self.status_label = None # Shows the status while solving sudoku(WIP)
		self.btn_grid = [[None for i in range(9)] for j in range(9)] # Contains all buttons
		self.current_sudoku = [[0 for i in range(9)] for j in range(9)]
		self.current_selection = None # The cell currently editing
		self.previous_selection = None # The cell that was previously edited

	###########INIT FUNCTIONS###########

	def init_styles(self, theme): # Sets styles for each button and frame

		try:
			self.style.theme_use(theme)
		except:
			print("Invalid theme")

		self.style.configure('TFrame', background = "black")
		self.style.configure('notGrid.TFrame', background = "#")
		self.style.configure('cell.TButton',
													foreground = "black",
													background = App.btn_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.configure('cellActive.TButton',
													foreground = App.btn_color,
													background = App.btn_select_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.configure('cellFixed.TButton',
													foreground = "black",
													background = App.btn_fixed_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.configure('cellError.TButton',
													foreground = "black",
													background = App.btn_error_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.configure('cellFixedError.TButton',
													foreground = "black",
													background = App.btn_fixed_error_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.configure('cellSolved.TButton',
													foreground = "black",
													background = App.btn_solved_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.configure('cellFixedSolved.TButton',
													foreground = "black",
													background = App.btn_fixed_solved_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.configure('cellSolving.TButton',
													foreground = "black",
													background = App.btn_solving_color,
													relief = "flat",
													padding = 0,
													font = "Helvetica")
		self.style.map('TButton', background=[('active', App.btn_hover_color)])

	def init_widgets(self): # Initializes all the widgets

		self.sudoku_grid = ttk.Frame(self.win)
		self.sudoku_grid.grid(row=0, column=0)

		self.footer = ttk.Frame(self.win, style = "notGrid.TFrame")
		# self.status_label = ttk.Label(self.footer)
		# self.status_label.pack()
		self.footer.grid(row = 1, column = 0, ipady = App.cell_borderWidth, ipadx = self.size[0]/2)

		for i in range(9):
			for j in range(9):

				frame = ttk.Frame(self.sudoku_grid)
				frame.grid(row = i+((i)//3),
								column = j+((j)//3),
								ipadx = App.cell_borderWidth,
								ipady = App.cell_borderWidth)

				btn = ttk.Button(frame,
												text=f"{randint(1,9)}",
												style="cell.TButton",
												width=5,
												takefocus=False)
				btn.configure(command = lambda button=btn: self.set_selection(button))
				btn.grid(row=0, column=0, ipady=12)

				self.btn_grid[i][j] = btn

		col_count, row_count = self.sudoku_grid.grid_size()

		for col in range(col_count):
			self.sudoku_grid.grid_columnconfigure(col, minsize=App.box_borderWidth-1)

		for row in range(row_count):
			self.sudoku_grid.grid_rowconfigure(row, minsize=App.box_borderWidth-1)

	def init_keyboard(self): # Binds some keyboard keys to some functions
		self.win.bind("<KeyPress>", self.edit_selection)
		self.win.bind("<Return>", self.confirm_selection)
		self.win.bind("n", self.new_sudoku)
		self.win.bind("v", self.verify_sudoku)
		self.win.bind("c", self.__revert_colors)
		self.win.bind("s", self.solve_sudoku)
		self.win.bind("g", lambda e: self.get_new_thread(self.show_algorithm, None).start())

	###########CELL EDIT FUNCTIONS###########

	def set_selection(self, btn): # Sets the current editing cell

		self.previous_selection = self.current_selection
		self.current_selection = btn

		if self.current_selection["style"] in ("cell.TButton", "cellError.TButton"):
			self.current_selection.configure(style="cellActive.TButton")
			try:
				self.previous_selection.configure(style="cell.TButton")
			except:
				pass
		elif self.current_selection["style"] == "cellActive.TButton":
			self.current_selection.configure(style="cell.TButton")
			self.current_selection = None

	def edit_selection(self, e):
		if e.keysym != "BackSpace": #Backspace Detection
			try:
				char = int(e.char)
			except:
				return

			if self.current_selection == None or not self.in_between(char, 1, 9):
				return
		else:
			char = ""
		
		self.current_selection["text"] = char

	def confirm_selection(self, e=None):
		try:
			self.current_selection.configure(style="cell.TButton")
			self.current_selection = None
		except:
			pass

	###########SUDOKU EXTENDED FUNCTIONS###########

	def new_sudoku(self, e=None): #Makes a new sudoku
		
		self.generate()
		self.setDifficulty(2)
		grid = self.get_grid()
		self.current_sudoku = grid
		self.clear()
		self.confirm_selection()

		for row in range(9):
			for cell in range(9):
				if grid[row][cell] == 0:
					self.btn_grid[row][cell]["command"] = lambda button=self.btn_grid[row][cell]: self.set_selection(button)
					grid[row][cell] = ""
					self.btn_grid[row][cell]["style"] = "cell.TButton"
				else:
					self.btn_grid[row][cell]["command"] = self.null
					self.btn_grid[row][cell]["style"] = "cellFixed.TButton"

				self.btn_grid[row][cell]["text"] = grid[row][cell]

	def get_sudoku(self):
		grid = [[self.btn_grid[i][j]["text"] for j in range(9)] for i in range(9)]

		for i in range(9):
			for j in range(9):
				if grid[i][j] == "":
					grid[i][j] = 0

		return grid

	def set_sudoku(self, grid):

		for i in range(9):
			for j in range(9):
				if self.btn_grid[i][j]["text"] != grid[i][j]:
					if grid[i][j] == 0:
						self.btn_grid[i][j]["text"] = ""
					else:
						self.btn_grid[i][j]["text"] = grid[i][j]

	def verify_sudoku(self, e=None):

		self.set_grid(self.get_sudoku())
		errors = self.check_errors()

		# Looks chaotic... but just changes colors to respective error colors

		for error in errors:
			if error[0] == "row": #If error in row
				for btn in self.btn_grid[error[1]]: 

					if btn["style"] in ("cellFixed.TButton", "cellFixedError.TButton"): #If the box im coloring is not editable
						btn["style"] = "cellFixedError.TButton"
					else:
						btn["style"] = "cellError.TButton"

			elif error[0] == "col": #If error in col
				for btn_row in self.btn_grid:

					if btn_row[error[1]]["style"] in ("cellFixed.TButton", "cellFixedError.TButton"): #If the box im coloring is not editable
						btn_row[error[1]]["style"] = "cellFixedError.TButton"
					else:
						btn_row[error[1]]["style"] = "cellError.TButton"

			elif error[0] == "box": #If error in a box
				for i in range(3):
					for j in range(3):

						if self.btn_grid[error[1][0]*3 + i][error[1][1]*3 + j]["style"] in ("cellFixed.TButton", "cellFixedError.TButton"): #If the box im coloring is not editable
							self.btn_grid[error[1][0]*3 + i][error[1][1]*3 + j]["style"] = "cellFixedError.TButton"
						else:
							self.btn_grid[error[1][0]*3 + i][error[1][1]*3 + j]["style"] = "cellError.TButton"

		if len(errors) == 0:
			return True
		else:
			return False

	def sudoku_filled(self):
		for i in range(9):
			for j in range(9):
				if self.btn_grid[i][j]["text"] == '':
					return False

		return True
	
	def solve_sudoku(self, e=None): #Solves the sudoku for you
		if self.sudoku_filled():
			return True

		solvable = self.verify_sudoku()
		if not solvable:
			return False

		solved, grid = self.solve(self.get_sudoku())
		if solved:
			self.set_sudoku(grid)
			return True
		else:
			return False

	def show_algorithm(self, e=None): #Solves the sudoku for you and shows how the computer solves a sudoku
    
		solvable = self.verify_sudoku()

		if not solvable:
			return False
		
		grid = self.get_sudoku()

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

		solved, grid = self.__show_algorithm(grid, new_cell)

		if solved:
			self.__revert_colors()
			sleep(0.2)

			for i in range(9):
				for j in range(9):
					if self.btn_grid[i][j]["style"] in ("cellFixed.TButton", "cellFixedError.TButton"):
						self.btn_grid[i][j]["style"] = "cellFixedSolved.TButton"
					else:
						self.btn_grid[i][j]["style"] = "cellSolved.TButton"

			sleep(0.2)
			self.__revert_colors()
			self.set_sudoku(grid)
			return True
		else:
			print("Not solvable")
			return False

	def __show_algorithm(self, grid, cell):

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

				for i in range(9):
					for j in range(9):
						if i < row:
							if self.btn_grid[i][j]["style"] in ("cellFixed.TButton", "cellFixedError.TButton"):
								self.btn_grid[i][j]["style"] = "cellFixedSolved.TButton"
							elif self.btn_grid[i][j]["style"] in ("cell.TButton", "cellError.TButton", "cellSolving.TButton"):
								self.btn_grid[i][j]["style"] = "cellSolved.TButton"
						elif i == row:
							if j < col:
								if self.btn_grid[i][j]["style"] in ("cellFixed.TButton", "cellFixedError.TButton"):
									self.btn_grid[i][j]["style"] = "cellFixedSolved.TButton"
								elif self.btn_grid[i][j]["style"] in ("cell.TButton", "cellError.TButton", "cellSolving.TButton"):
									self.btn_grid[i][j]["style"] = "cellSolved.TButton"

				self.btn_grid[row][col]["style"] = "cellSolving.TButton"

				self.set_sudoku(grid)
				sleep(0.1)

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

				solved, grid = self.__show_algorithm(grid, new_cell) #Continue from here
				if solved:
				  return True, grid

			grid[row][col] = 0 #The line that changed my day

			for i in range(9):
				for j in range(9):
					if i >= row:
						if self.btn_grid[i][j]["style"] in ("cellFixedSolved.TButton", "cellFixedError.TButton"):
							self.btn_grid[i][j]["style"] = "cellFixedError.TButton"
						elif self.btn_grid[i][j]["style"] in ("cellSolved.TButton", "cellError.TButton", "cellSolving.TButton"):
							self.btn_grid[i][j]["style"] = "cellError.TButton"
					elif i == row:
						if j >= col:
							if self.btn_grid[i][j]["style"] in ("cellFixedSolved.TButton", "cellFixedError.TButton"):
								self.btn_grid[i][j]["style"] = "cellFixedError.TButton"
							elif self.btn_grid[i][j]["style"] in ("cellSolved.TButton", "cellError.TButton", "cellSolving.TButton"):
								self.btn_grid[i][j]["style"] = "cellError.TButton"

			return False, grid

		return False, grid

	def __revert_colors(self, e=None, delay=0):

		for row in self.btn_grid: #Just reverting error colors
			for btn in row:
				if btn["style"] in ("cellFixed.TButton", "cellFixedError.TButton", "cellFixedSolved.TButton"):
					btn["style"] = "cellFixed.TButton"
				else:
					btn["style"] = "cell.TButton"

	###########USEFUL FUNCTIONS###########

	def in_between(self, value, lower_limit, upper_limit): # Checks if given value is in between 2 numbers (both inclusive)
		if type(value) == int or type(value) == float:
			if value >= lower_limit and value <= upper_limit:
				return True

		return False

	def null(self, *kwarg, **args):
		return

	def get_new_thread(self, thread_function, *args):
		x = threading.Thread(target=thread_function, args=tuple(args), daemon = True)
		return x

	def run(self): # Runs the game

		self.init_styles("clam")
		self.init_widgets()
		self.init_keyboard()
		self.new_sudoku()
		self.win.mainloop()


#################
#     RUN       #
#################

print("Welcome to Sudoku App")
print("Availible Commands\n -> New Sudoku [Key:N]\n -> Solve Sudoku [Key:S]\n -> Display Algo [Key:G]\n -> Clear colors [Key:C]\n -> Check for errors [Key:V]")

game = App("Sudoku", (480, 490), "#F0F0F0")
game.run()