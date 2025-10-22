import tkinter as tk
from SokobanSolver import SokobanSolver
from SokobanGUI import SokobanGUI



if __name__ == "__main__":
    Sokoban_default = '''
######
##  .#
# $ ##
#@#  #
#    #
######'''.splitlines()[1:]
    root = tk.Tk()
    app = SokobanGUI(root, Sokoban_default)
    root.mainloop()