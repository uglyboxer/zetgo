"""
 Example program to show using an array to back a grid on-screen.
 
 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/
 
 Explanation video: http://youtu.be/mdTeqiWyFnc

Borrowed and updated from https://github.com/xyproto/monkeyjump
"""
import pygame
from game import Game


game = Game()
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

BOARD_SIZE = game.board.board_size
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 25
HEIGHT = 25
 
# This sets the margin between each cell
MARGIN = 2
 
# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.
grid = []
for row in range(BOARD_SIZE):
    # Add an empty array that will hold each cell
    # in this row
    grid.append([])
    for column in range(BOARD_SIZE):
        grid[row].append(0)  # Append a cell
 
# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
 
# Initialize pygame
pygame.init()
 
# Set the HEIGHT and WIDTH of the screen
HEADER_OFFSET = 50
WINDOW_SIZE = [516, 516 + HEADER_OFFSET]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
pygame.display.set_caption("ZetGo")

board = pygame.image.load('src/zetgo/images/board.png')
black_img = pygame.image.load('src/zetgo/images/black.png').convert()
white_img = pygame.image.load('src/zetgo/images/white.png').convert()
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

w, h = screen.get_size()
h = h - HEADER_OFFSET

board = pygame.transform.scale(board, (w, h))
black_img = pygame.transform.scale(black_img, (w // BOARD_SIZE - 1, h // BOARD_SIZE - 1))
white_img = pygame.transform.scale(white_img, (w // BOARD_SIZE - 1, h // BOARD_SIZE - 1))
# not perfect, not based on anythin other than hunch, but it sortof works
margin = 27 + int(19 + BOARD_SIZE * -1.8)
# calculate the bottom/right margin
leftover = w - (((BOARD_SIZE - 1) * (w / float(BOARD_SIZE)) + margin) - margin)
botmargin = leftover - margin 

# Draw the lines on the board
xspace = w / float(BOARD_SIZE)
# one xnum per vertical line
for xnum in range(BOARD_SIZE):
    x = int(xnum * xspace) + margin
    pygame.draw.line(board, (0, 0, 0), (x, margin), (x, h - botmargin), 1)
yspace = h / float(BOARD_SIZE)

# one ynum per horizontal line
for ynum in range(BOARD_SIZE):
    y = int(ynum * yspace) + margin
    pygame.draw.line(board, (0, 0, 0), (margin, y), (w - botmargin, y), 1)
# Draw the letters on the board
pygame.font.init()
# myfont = pygame.font.Font("/usr/share/fonts/truetype/dustin/Balker.ttf", 12)
myfont = pygame.font.SysFont(None, 22)
# letters = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]
# letters = letters[:BOARD_SIZE + 1]
# for i, l in enumerate(letters):
#     halfletterwidth = 2
#     x = int(i * xspace) + margin - halfletterwidth
#     bgcolor = (200, 200, 0, 255)
#     fontimage = myfont.render(l, False, (0, 0, 0, 255), bgcolor)
#     fontimage.set_colorkey(bgcolor)
#     board.blit(fontimage, (x, 0))
# numbers = map(str, range(BOARD_SIZE, 0, -1))
# for i, n in enumerate(numbers):
#     halfletterheight = 5
#     y = int(i * yspace) + margin - halfletterheight
#     bgcolor = (200, 200, 0, 255)
#     fontimage = myfont.render(n, False, (0, 0, 0, 255), bgcolor)
#     fontimage.set_colorkey(bgcolor)
#     fw = fontimage.get_width()
#     board.blit(fontimage, (8 - fw, y))
# Draw the starpoints on the board
if BOARD_SIZE == 19:
    starpoints = 3, 9, 15
    notpoints = ()
elif BOARD_SIZE == 9:
    starpoints = 2, 4, 6
    notpoints = (2, 4), (4, 2), (6, 4), (4, 6)
elif BOARD_SIZE == 5:
    starpoints = 2,
    notpoints = ()
else:
    starpoints = ()
    notpoints = ()
if starpoints:
    if len(starpoints) == 1:
        center = starpoints[0]
    else:
        center = starpoints[int(len(starpoints) / 2.0 + 0.5)]
    for x in starpoints:
        for y in starpoints:
            if (x, y) not in notpoints:
                pos = (int(xspace * x) + margin, int(yspace * y) + margin)
                pygame.draw.circle(board, (0, 0, 0), pos, 4, 0)

screen.blit(board, (0, 0))
pygame.display.update()
caps = 'Black: 0  White: 0'
bgcolor = (0, 0, 0, 255)
fontimage = myfont.render(caps, True, (255, 255, 255, 255), bgcolor)
# -------- Main Program Loop -----------


while not done and not game.passes[1]:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:  # If user clicked close
        done = True  # Flag that we are done so we exit this loop
    elif event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()
        # Change the x/y screen coordinates to grid coordinates
        column = pos[0] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)
        if column <= 10 and row >= BOARD_SIZE:
            move = 'p'
            rv = game.move(move)

        else:
            move = '{}, {}'.format(row, column)
            rv = game.move(move)
            grid[row][column] = game.board.positions[row][column].player
        # Set that location to one
        if rv['complete']:
            rv = game.score()

        caps = 'Black: {}  White: {}'.format(rv['captures'][1], rv['captures'][-1])
        fontimage = myfont.render(caps, True, (255, 255, 255, 255), bgcolor)
    # Set the screen background
    # screen.fill(BLACK)
    # screen.blit(pygame.image.load('src/zetgo/images/board.png').convert(), (0, 0))

    screen.blit(board, (0, 0))
    # Draw the grid
    for row in range(BOARD_SIZE):
        for column in range(BOARD_SIZE):
            color = WHITE
            if game.board.positions[row][column].player == 1:
                color = GREEN
                image = black_img
                screen.blit(image,
                             ((MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN))
            elif game.board.positions[row][column].player == -1:
                color = RED
                image = white_img
                screen.blit(image,
                             ((MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN))
            else:
                # TODO need something here to clear the captures, but leave the lines
                # screen.blit(board, ((MARGIN + WIDTH) * column + MARGIN,
                #               (MARGIN + HEIGHT) * row + MARGIN), pygame.Rect(x, y, HEIGHT, WIDTH))
                pass

    passimage = myfont.render('PASS', True, (255, 255, 255, 255), bgcolor)
    # pygame.draw.rect(screen, WHITE, (10, h + 18, WIDTH, HEIGHT))
    screen.blit(passimage, (10, h + 18))
    screen.blit(fontimage, (300, h + 18))
    # Limit to 60 frames per second
    clock.tick(20)
    # Go ahead and update the screen with what we've drawn.
    pygame.display.update()
 
while not done:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:  # If user clicked close
        done = True
    pygame.display.update()
