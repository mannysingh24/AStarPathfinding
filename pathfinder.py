import math
from queue import PriorityQueue
from tracemalloc import start
import pygame

window = pygame.display.set_mode((750,750))
pygame.display.set_caption("Pathfinding A* Algorithm")

class nodeTracker:
    def __init__(self, totalRows, rows, columns, width):
        self.currentColor = (255,255,255)
        self.totalRows = totalRows
        self.xAxis = rows * width
        self.yAxis = columns * width
        self.rows = rows
        self.columns = columns
        self.width = width
        self.neighbors = []

    def already_checked(self):
        return self.currentColor == (128,0,128)

    def end_check(self):
        return self.currentColor == (0,255,0)

    def currentPosition(self):
        return self.rows, self.columns

    def free_pos(self):
        return self.currentColor == (255,255,0)

    def reset_color(self):
        self.currentColor = (255,255,255)

    def starting_check(self):
        return self.currentColor == (255,0,0)

    def obstacle_check(self):
        return self.currentColor == (0,0,0)

    def already_checked_change(self):
        self.currentColor = (128,0,128)

    def end_check_change(self):
        self.currentColor = (255,165,0)

    def free_pos_change(self):
        self.currentColor = (0,255,0)

    def starting_check_change(self):
        self.currentColor = (255,0,0)

    def obstacle_check_change(self):
        self.currentColor = (0,0,0)
    
    def indicate_path(self):
        self.currentColor = (255,255,0)

    def checkNeighbors(self, matrix):
        self.neighbors = []
        if self.rows < self.totalRows - 1: 
            if not matrix[self.rows + 1][self.columns].obstacle_check(): #can I move down?
                self.neighbors.append(matrix[self.rows+1][self.columns]) #if so, append it
        if self.rows > 0: 
            if not matrix[self.rows - 1][self.columns].obstacle_check(): #can I move up?
                self.neighbors.append(matrix[self.rows-1][self.columns]) #if so, append it
        if self.columns < self.totalRows - 1:
            if not matrix[self.rows][self.columns + 1].obstacle_check(): #can I move right?
                self.neighbors.append(matrix[self.rows][self.columns+1]) #if so, append it
        if self.columns > 0:
            if not matrix[self.rows][self.columns-1].obstacle_check(): #can I move left?
                self.neighbors.append(matrix[self.rows][self.columns-1]) #if so, append it

    def draw_figure(self, window):
        pygame.draw.rect(window, self.currentColor, (self.xAxis, self.yAxis, self.width, self.width))

    def __lt__(self, otherBox):
        return False

def createMatrix(rows, width):
    matrix = []
    spacing_width = width // rows
    for x in range(rows):
        matrix.append([])
        for y in range(rows):
            box = nodeTracker(rows, x, y, spacing_width) 
            matrix[x].append(box)
    return matrix

def distance(point1, point2): #utilzes manhatten distance
    x_1, y_1 = point1
    x_2, y_2 = point2
    sumPoints = abs(x_1 - x_2) + abs(y_1 - y_2)
    return sumPoints

def draw_matrix(window, matrix, rows, width):
    window.fill((255,255,255))
    for row in matrix:
        for box in row:
            box.draw_figure(window)
    draw_matrix_lines(window, rows, width)
    pygame.display.update()

def draw_matrix_lines(window, rows, width):
    spacing_width = width // rows
    count = 0
    index = 0
    while count < rows:
        pygame.draw.line(window, (128,128,128), (0, (count*spacing_width)), (width, (count*spacing_width))) #drawing horizontal lines
        count = count + 1
        while index < rows:
            pygame.draw.line(window, (128,128,128), ((index*spacing_width), 0), ((index*spacing_width), width)) #drawing vertical lines
            index = index + 1

def primary(window, width):
    current_rows = 50
    matrix = createMatrix(current_rows, width)
    start_pos = None
    end_pos = None
    is_running = True
    while is_running == True:
        draw_matrix(window, matrix, current_rows, width)
        for current_event in pygame.event.get():
            if pygame.mouse.get_pressed()[2]: #right mouse click
                position = pygame.mouse.get_pos()
                row, column = mouse_position(position, current_rows, width)
                box = matrix[row][column]
                box.reset_color()
                if box == start_pos:
                    start_pos = None
                if box == end_pos:
                    end_pos = None
            elif pygame.mouse.get_pressed()[0]: #left mouse click
                position = pygame.mouse.get_pos()
                row, column = mouse_position(position, current_rows, width)
                box = matrix[row][column]
                if not start_pos:
                    if box != end_pos:
                        start_pos = box
                        start_pos.starting_check_change()
                elif not end_pos:
                    if box != start_pos:
                        end_pos = box
                        end_pos.end_check_change()
                elif box != start_pos:
                    if box != end_pos:
                        box.obstacle_check_change()
            if current_event.type == pygame.QUIT:
                is_running = False
            if current_event.type == pygame.KEYDOWN:
                if current_event.key == pygame.K_c:
                    start_pos = None
                    end_pos = None
                    matrix = createMatrix(current_rows, width)
                if current_event.key == pygame.K_SPACE:
                    if start_pos and end_pos:
                        for row in matrix:
                            for box in row:
                                box.checkNeighbors(matrix)
                        pathfind_algo(lambda: draw_matrix(window,matrix,current_rows,width), matrix, start_pos, end_pos)

    pygame.quit()

def mouse_position(position, rows, width):
    spacing_width = width // rows
    point1, point2 = position
    current_row = point1 // spacing_width
    current_col = point2 // spacing_width
    return current_row, current_col

def pathfind_algo(draw_func, matrix, starting, ending):
    count = 0
    store_pairs = PriorityQueue()
    store_pairs.put((0, count, starting)) # put starting node in the queue
    prev_node = {} #where the nodes came from
    g_func = {box: float("inf") for row in matrix for box in row} #keeps track of current shortest distance from start node to current node
    g_func[starting] = 0
    f_func = {box: float("inf") for row in matrix for box in row} #keeps track of predicted distance from current node to end node
    f_func[starting] = distance(starting.currentPosition(), ending.currentPosition()) #guess from start node to end node
    queue_check = {starting} 

    while not store_pairs.empty(): #to quit the loop and algorithm
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current_node = store_pairs.get()[2] #get node from queue
        queue_check.remove(current_node) #avoid duplicates
        if current_node == ending: #node is found
            shortest_path(prev_node, ending, draw_func)
            ending.end_check_change()
            return True
        for neigh in current_node.neighbors: #loop through node's neighbors
            currentG = g_func[current_node] + 1
            if currentG < g_func[neigh]:
                prev_node[neigh] = current_node
                g_func[neigh] = currentG
                f_func[neigh] = currentG + distance(neigh.currentPosition(), ending.currentPosition())
                if neigh not in queue_check:
                    count = count + 1
                    store_pairs.put((f_func[neigh], count, neigh))
                    queue_check.add(neigh)
                    neigh.free_pos_change()
        draw_func()
        if current_node != starting:
            current_node.already_checked_change()

    return False

def shortest_path(previous, node, draw_func):
    while node in previous: #traverse from end node to start node
        node = previous[node]
        node.indicate_path()
        draw_func()




primary(window, 750)


    
