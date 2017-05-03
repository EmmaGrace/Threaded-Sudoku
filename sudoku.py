import requests
import threading
import string
import sys
from bs4 import BeautifulSoup

# future features:

# development goals:
# reduce copied code -- more functions?
# smarter AI?
# more efficient within threads
# comments and style guide stuff

def select_board():
    if len(sys.argv) == 1:
        return get_rand_sudoku()
    elif len(sys.argv) == 2:
        try:
            int(sys.argv[1])
            return get_ID_sudoku(sys.argv[1])
        except:
            return get_file_sudoku(sys.argv[1])
    else:
        return False

def get_rand_sudoku():
    url = "http://show.websudoku.com/?level=1"
    response = requests.post(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pid = (soup.find('input', attrs={'name':'id', 'id':'pid', 'type':'hidden'}))['value']
    cheat = (soup.find('input', attrs={'name':'cheat', 'id':'cheat', 'type':'hidden'}))['value']
    editmask = (soup.find('input', attrs={'id':'editmask', 'type':'hidden'}))['value']

    puzzle = ""
    for i in range(len(cheat)):
        if not int(editmask[i]):
            puzzle += cheat[i]
        else:
            puzzle += "0"

    print("Easy puzzle #", pid, " from websudoku.com:", sep = "")
    print_sudoku(puzzle)
    
    return puzzle

def get_ID_sudoku(pid):
    url = "http://show.websudoku.com/?level=1&set_id=" + str(pid)
    response = requests.post(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cheat = (soup.find('input', attrs={'name':'cheat', 'id':'cheat', 'type':'hidden'}))['value']
    editmask = (soup.find('input', attrs={'id':'editmask', 'type':'hidden'}))['value']

    puzzle = ""
    for i in range(len(cheat)):
        if not int(editmask[i]):
            puzzle += cheat[i]
        else:
            puzzle += "0"

    print("Easy puzzle #", pid, " from websudoku.com:", sep = "")
    print_sudoku(puzzle)
    
    return puzzle

def get_file_sudoku(filename):
    try:
        fin = open(filename)
    except:
        print("Invalid file name. Exiting...")
        return False
    
    text = fin.read() 
    table = str.maketrans("", "", string.punctuation + string.ascii_letters + string.whitespace)
    text = text.translate(table)
    if len(text) != 81:
        print("Invalid puzzle. Exiting...")
        return False
    
    print("Custom puzzle:")
    print_sudoku(text)
    
    return text

def print_sudoku(puzzle): 
    for i in range(len(puzzle)):
        print(puzzle[i], end = "")
        if i % 3 == 2:
            if i % 9 != 8:
                print("|", end = "")  
            else:
                print()
            if (i % 27 == 26 and i < 80):
                print("---+---+---")
                
    return

def get_row(y, matrix):
    list = []
    
    for i in range(9):
        if matrix[y][i] != "0":
            list.append(matrix[y][i])
            
    return list
    
def get_col(x, matrix):
    list = []
    
    for i in range(9):
        if matrix[i][x] != "0":
            list.append(matrix[i][x])
            
    return list
    
def get_box(x, y, matrix):
    list = []
    x_mod = x % 3
    y_mod = y % 3
    
    if x_mod == 0:
        x_lbound = x
        x_ubound = x + 3
    elif x_mod == 1:
        x_lbound = x - 1
        x_ubound = x + 2
    else:
        x_lbound = x - 2
        x_ubound = x + 1
    
    if y_mod == 0:
        y_lbound = y
        y_ubound = y + 3
    elif y_mod == 1:
        y_lbound = y - 1
        y_ubound = y + 2
    else:
        y_lbound = y - 2
        y_ubound = y + 1
        
    for i in range(y_lbound, y_ubound):
        for j in range(x_lbound, x_ubound):
            if matrix[i][j] != "0":
                list.append(matrix[i][j]) 
                
    return list, x_lbound, x_ubound, y_lbound, y_ubound

def solve_row_empty(index, matrix):
    missing = ["!"]
    while missing:
        missing = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        present = get_row(index, matrix)
        for val in present:
            missing.remove(val)
        
        empty = []
        for i in range(9):
            if matrix[index][i] == "0":
                empty.append(i)
        
        for cell in empty:
            blocked = get_col(cell, matrix) + get_box(cell, index, matrix)[0]
            for num in blocked:
                if blocked.count(num) == 2:
                    blocked.remove(num)
            
            option = 0
            multiple = 0
            for val in missing:
                if blocked.count(val) == 0:
                    if multiple != 0:
                        multiple += 1
                        break
                    else:
                        option = val
                        multiple += 1
            if multiple == 1:
                matrix[index][cell] = option
                missing.remove(option)
                empty.remove(cell)
                
    return
    
def solve_col_empty(index, matrix):
    missing = ["!"]
    while missing:
        missing = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        present = get_col(index, matrix)
        for val in present:
            missing.remove(val)
        
        empty = []
        for i in range(9):
            if matrix[i][index] == "0":
                empty.append(i) 
        
        for cell in empty:
            blocked = get_row(cell, matrix) + get_box(index, cell, matrix)[0]
            for num in blocked:
                if blocked.count(num) == 2:
                    blocked.remove(num)
            
            option = 0
            multiple = 0
            for val in missing:
                if blocked.count(val) == 0:
                    if multiple != 0:
                        multiple += 1
                        break
                    else:
                        option = val
                        multiple += 1
            if multiple == 1:
                matrix[cell][index] = option
                missing.remove(option)
                empty.remove(cell)

    return    
    
def solve_box_empty(index, matrix):
    missing = ["!"]
    # find the cell in the upper left so we can determine contents of box
    x = (index % 3) * 3
    y = (index // 3) * 3
    while missing:
        missing = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        present, x_lbound, x_ubound, y_lbound, y_ubound = get_box(x, y, matrix)
        for val in present:
            missing.remove(val)
        
        empty = []
        for i in range(y_lbound, y_ubound):
            for j in range(x_lbound, x_ubound):
                if matrix[i][j] == "0":
                    empty.append((i, j))       
        
        for cell in empty:
            blocked = get_row(cell[0], matrix) + get_col(cell[1], matrix)
            for num in blocked:
                if blocked.count(num) == 2:
                    blocked.remove(num)
                    
            option = 0
            multiple = 0
            for val in missing:
                if blocked.count(val) == 0:
                    if multiple != 0:
                        multiple += 1
                        break
                    else:
                        option = val
                        multiple += 1
            if multiple == 1:
                matrix[cell[0]][cell[1]] = option
                missing.remove(option)
                empty.remove(cell)      
        
    return

def solve_row_missing(index, matrix):
    missing = ["!"]
    while missing:
        missing = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        present = get_row(index, matrix)
        for val in present:
            try:
                missing.remove(val)
            except:
                print("-", val, "-", missing)
        
        empty = []
        for i in range(9):
            if matrix[index][i] == "0":
                empty.append(i)
                    
        for val in missing:
            option = 0
            multiple = 0            
            
            for cell in empty:
                blocked = get_col(cell, matrix) + get_box(cell, index, matrix)[0]
                for num in blocked:
                    if blocked.count(num) == 2:
                        blocked.remove(num)                
                               
                if blocked.count(val) == 0:
                    if multiple != 0:
                        multiple += 1
                        break
                    else:
                        option = cell
                        multiple += 1
            if multiple == 1:
                matrix[index][option] = val
                missing.remove(val)
                empty.remove(option)
                
    return
    
def solve_col_missing(index, matrix):
    missing = ["!"]
    while missing:
        missing = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        present = get_col(index, matrix)
        for val in present:
            missing.remove(val)
        
        empty = []
        for i in range(9):
            if matrix[i][index] == "0":
                empty.append(i)        
        
        for val in missing:
            option = 0
            multiple = 0            
            
            for cell in empty:
                blocked = get_row(cell, matrix) + get_box(index, cell, matrix)[0]
                for num in blocked:
                    if blocked.count(num) == 2:
                        blocked.remove(num)                
                               
                if blocked.count(val) == 0:
                    if multiple != 0:
                        multiple += 1
                        break
                    else:
                        option = cell
                        multiple += 1
            if multiple == 1:
                matrix[option][index] = val
                missing.remove(val)
                empty.remove(option)

    return    
    
def solve_box_missing(index, matrix):
    missing = ["!"]
    # find the cell in the upper left so we can determine contents of box
    x = (index % 3) * 3
    y = (index // 3) * 3
    while missing:
        missing = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        present, x_lbound, x_ubound, y_lbound, y_ubound = get_box(x, y, matrix)
        for val in present:
            missing.remove(val)
        
        empty = []
        for i in range(y_lbound, y_ubound):
            for j in range(x_lbound, x_ubound):
                if matrix[i][j] == "0":
                    empty.append((i, j))    
        
        for val in missing:
            option = 0
            multiple = 0            
            
            for cell in empty:
                blocked = get_row(cell[0], matrix) + get_col(cell[1], matrix)
                for num in blocked:
                    if blocked.count(num) == 2:
                        blocked.remove(num)                
                               
                if blocked.count(val) == 0:
                    if multiple != 0:
                        multiple += 1
                        break
                    else:
                        option = cell
                        multiple += 1
            if multiple == 1:
                matrix[option[0]][option[1]] = val
                missing.remove(val)
                empty.remove(option)
            
    return

def solve_sudoku(puzzle):
    threads = []
    
    matrix = [["!" for j in range(9)] for i in range(9)]
    i = 0
    for j in range(9):
        for k in range(9):
            matrix[j][k] = puzzle[i]
            i += 1
    
    for i in range(9):
        threads.append(threading.Thread(target = solve_row_empty, args = (i, matrix)))
    for i in range(9):
        threads.append(threading.Thread(target = solve_col_empty, args = (i, matrix)))
    for i in range(9):
        threads.append(threading.Thread(target = solve_box_empty, args = (i, matrix)))
    for i in range(9):
        threads.append(threading.Thread(target = solve_row_missing, args = (i, matrix)))
    for i in range(9):
        threads.append(threading.Thread(target = solve_col_missing, args = (i, matrix)))
    for i in range(9):
        threads.append(threading.Thread(target = solve_box_missing, args = (i, matrix)))
    
    
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
     
    puzzle = ""
    for i in range(9):
        for j in range(9):
            puzzle += matrix[i][j]
    
    return puzzle

def main():
    board = select_board()
    if (board):
        board = solve_sudoku(board)
        print("\nSOLUTION:")
        print_sudoku(board)
    
if __name__ == '__main__':
    main()
    
    