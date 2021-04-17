import pygame
import random
import numpy as np
import copy
import time
from pynput.keyboard import Key, Controller

colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
    (255,255,77)
]


class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [1, 4, 5, 8]],
        [[5, 6, 8, 9] , [0, 4, 5, 9]],
        [[0, 1, 4, 8] , [4, 5, 6, 10], [1, 5, 9, 8], [0, 4, 5, 6]],
        [[0, 1, 5, 9] , [2, 4, 5, 6],  [0, 4, 8, 9], [4, 5, 6, 8]],
        [[1, 4, 5, 6] , [0, 4, 5, 8], [4, 5, 6, 9], [1, 4, 5, 9]],
        [[0, 1, 4, 5]],
    ]
    """ 
    figures are represented within a 4x4 matrix space:
    00 01 02 03
    04 05 06 07
    08 09 10 11
    12 13 14 15 
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        rand = random.randint(0, len(self.figures) - 1)
        self.type = rand
        self.color = rand + 1
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class Tetris:
    level = 2
    score = 0
    state = "start"
    field = []
    height = 0
    width = 0
    x = 100
    y = 60
    zoom = 20
    figure = None

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"

        # creating the field
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)
    
    # Initialise the left corner of the 4x4 space at the index (0,0) of the field which is relatively makes it at the left corner
    def new_figure(self):
        self.figure = Figure(0, 0)
    
    # Checks if the figure intersects anything fixed on the field
    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                # If the figure goes out of bound above, to the sides or overlaps anoter figure on the board
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection
    
    # Check if there is a complete line
    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:  # If no zeros, aka a full line, copy the above line onto the current line
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2    # Increase the score per cleared line
        """ 
        The break_line() function checks from bottom to the top in order to maintain the structure
        of the blocks 
        """
    # Freeze the block when it reaches the bottom or touches a block
    def freeze(self, break_line = True):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        if break_line:
            self.break_lines()
        self.new_figure()
        if self.intersects():   # If it intersects at the top then game over
            self.state = "gameover"

    def go_space(self, player = True):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze(player)
        """
        Loop until the bottom then freeze
        """

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation


# AI CODES - GENETIC ALGORITHM
class Ai:
    def __init__(self, height_weight, line_weight, hole_weight, bump_weight, game_copy):
        self.height_weight = height_weight
        self.line_weight = line_weight
        self.hole_weight = hole_weight
        self.bump_weight = bump_weight

        self.game = game_copy
        
    # Aggregate height
    def column_height(self, game):
        heights = [0] * len(game.field[0])
        for j in range(len(game.field[0])):
            temp = 0
            for i in range(len(game.field)):
                if game.field[i][j] != 0:
                    break
                temp += 1
            heights[j] = 20 - temp
            
        return heights

    def aggregate_height(self, heights):
        return np.sum(heights)

    # Complete Lines
    def is_Line(self, row):
        for i in row:
            if i == 0:
                return False    
        return True

    def complete_lines(self, game):
        count = 0
        for i in game.field:
            if self.is_Line(i) :
                count += 1
        return count

    # Holes
    def hole(self, heights):
        holes = 0
        for j in range(len(self.game.field[0])):
            blocks = 0
            for i in range(len(self.game.field)-1, -1, -1):
                if blocks >= heights[j]:
                    break
                if self.game.field[i][j] == 0:
                    holes += 1
                    
                blocks += 1
        return holes

    # Bumpiness
    def bumpiness(self,heights):
        sum = 0
        for i in range(0, len(heights)-1):
            sum += abs(heights[i] - heights[i+1])
        return sum
    
    def evaluate(self):
        scores = []
        counter = 0
        while True:
            game2 = copy.deepcopy(self.game)
            for i in range(len(game2.figure.figures[game2.figure.type])):
                moves = []
                if(counter >0):
                    for j in range(counter):
                        moves.append('right')
                if(i > 0):
                    for j in range(i):
                        moves.append('up')
                game2.go_space(player = False)
                score = self.height_weight * self.aggregate_height(self.column_height(game2)) + self.line_weight * self.complete_lines(game2) +self.hole_weight * self.hole(self.column_height(game2)) +self.bump_weight*self.bumpiness(self.column_height(game2))
                scores.append((score, moves))
            counter += 1
            game2.go_side(1)
            for j in range(4):
                if j + game2.figure.x > game2.width - 1:
                    break
        scores = sorted(score, key = lambda x: x[0], reverse = True)
        return scores[0]

# Initialize the game engine
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

size = (400, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Tetris")

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)
counter = 0

pressing_down = False

keyboard = Controller()

while not done:
    if game.figure is None:
        game.new_figure()

    counter += 1
    if counter > 100000:
        counter = 0

    if counter % (fps // game.level // 2) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
            if event.key == pygame.K_SPACE:
                game.go_space()
            if event.key == pygame.K_ESCAPE:
                game.__init__(20, 10)

    if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.fill(WHITE)

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])
    
    """ # TETRIS GAME WONT WORK
    bot = Ai(-0.51006,0.760066,-0.35663, -0.184483, game)
    score = bot.evaluate()
    time.sleep(3)
    for i in range(len(score[1])+1):
        if i > len(score[1]):
            keyboard.press(Key.space)
            keyboard.release(Key.space)
        if score[1][i] == 'up':
            keyboard.press(Key.up)
            keyboard.release(Key.up)
        if score[1][i] == 'right':
            keyboard.press(Key.right)
            keyboard.release(Key.right)  """


    font = pygame.font.SysFont('Calibri', 25, True, False)
    font1 = pygame.font.SysFont('Calibri', 65, True, False)
    text = font.render("Score: " + str(game.score), True, BLACK)
    text_game_over = font1.render("Game Over", True, (255, 125, 0))
    text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

    screen.blit(text, [0, 0])
    if game.state == "gameover":
        screen.blit(text_game_over, [20, 200])
        screen.blit(text_game_over1, [25, 265])
    
    #print(column_height(game.field))
    #print(hole(column_height(game.field), game.field))
    #print(aggregate_height(column_height(game.field)))
    #print(bumpiness(column_height(game.field)))
    #print(game.field)
    
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()