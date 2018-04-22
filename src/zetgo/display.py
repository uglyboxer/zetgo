"""
 Example program to show using an array to back a grid on-screen.
 
 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/
 
 Explanation video: http://youtu.be/mdTeqiWyFnc
"""
import pygame
from game import Game
 
BOARD_SIZE = 5
game = Game(BOARD_SIZE)
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20
 
# This sets the margin between each cell
MARGIN = 5
 
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
WINDOW_SIZE = [255, 255]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
pygame.display.set_caption("ZetGo")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------


while not done and not game.passes[1]:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:  # If user clicked close
        done = True  # Flag that we are done so we exit this loop
    elif event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        # Change the x/y screen coordinates to grid coordinates
        column = pos[0] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)
        if column == BOARD_SIZE and row == BOARD_SIZE:
            move = 'p'
            rv = game.move(move)

        else:
            move = '{}, {}'.format(row, column)
            rv = game.move(move)
            grid[row][column] = game.board.positions[row][column].player
        # Set that location to one
        if rv['complete']:
            game.score()

    # Set the screen background
    screen.fill(BLACK)
 
    # Draw the grid
    for row in range(BOARD_SIZE):
        for column in range(BOARD_SIZE):
            color = WHITE
            if game.board.positions[row][column].player == 1:
                color = GREEN
            elif game.board.positions[row][column].player == -1:
                color = RED
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH,
                              HEIGHT])
    pygame.draw.rect(screen, WHITE,
        [(MARGIN + WIDTH) * BOARD_SIZE + MARGIN,
         (MARGIN + HEIGHT) * BOARD_SIZE + MARGIN,
         WIDTH,
         HEIGHT]) 
    # Limit to 60 frames per second
    clock.tick(10)
    # Go ahead and update the screen with what we've drawn.
    pygame.display.update()
 
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
print(game.score())
pygame.quit()
