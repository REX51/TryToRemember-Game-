# Try to Remember
# By Rahul Singha
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

fps = 30
window_width = 640
window_height = 480
reveal_speed = 8
box_size = 40
gap_size = 10
board_width = 10
board_height = 7
assert (board_width * board_height) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
x_margin = int((window_width-(board_width*(box_size+gap_size))) /2)
y_margin = int((window_height-(board_height*(box_size+gap_size)))/2)

#               R   G   B
gray        = (100,100,100)
navy_blue   = ( 60, 60,100)
white       = (255, 255, 255)
red         = (255, 0, 0)
green       = ( 0, 255, 0)
blue        = ( 0, 0, 255)
yellow      = (255, 255, 0)
orange      = (255, 128, 0)
purple      = (255, 0, 255)
cyan        = ( 0, 255, 255)

bg_color = navy_blue
light_bg_color = gray
box_color = white
high_light_color = blue

donut = 'donut'
square = 'square'
diamond = 'diamond'
lines = 'lines'
oval = 'oval'

all_colors = (red,green,blue,yellow,orange,purple,cyan)
all_shapes = (donut,square,diamond,lines,oval)
assert len(all_colors) * len(all_shapes) * 2 >= board_width*board_height, "Board is too big for the number of shapes/colors defined."

def main():
    global fps_clock, DISPLAYSURF
    pygame.init()
    fps_clock = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((window_width,window_height))

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None

    DISPLAYSURF.fill(bg_color)
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False

        DISPLAYSURF.fill(bg_color)
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True


        boxx, boxy = getBoxAtPixel(mousex,mousey)
        if boxx !=None and boxy != None:
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True
                if firstSelection == None:
                    firstSelection = (boxx, boxy)
                else:
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        pygame.time.wait(1000)
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)


                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)


                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)


                        startGameAnimation(mainBoard)
                    firstSelection = None


                pygame.display.update()
                fps_clock.tick(fps)

def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(board_width):
        revealedBoxes.append([val] * board_height)
    return revealedBoxes

def getRandomizedBoard():
    icons = []
    for color in  all_colors:
        for shape in all_shapes:
            icons.append((shape,color))

    random.shuffle(icons)
    numIconsUsed = int(board_width * board_height / 2)
    icons = icons[:numIconsUsed] * 2
    random.shuffle(icons)

    board = []
    for x in range(board_width):
        column = []
        for y in range(board_height):
            column.append(icons[0])
            del icons[0]
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (box_size + gap_size) + x_margin
    top = boxy * (box_size + gap_size) + y_margin
    return (left, top)

def getBoxAtPixel(x, y):
    for boxx in range(board_width):
        for boxy in range(board_height):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, box_size, box_size)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)

def drawIcon(shape, color, boxx, boxy):
    quarter = int(box_size * 0.25)
    half = int(box_size * 0.5)

    left, top = leftTopCoordsOfBox(boxx,boxy)

    if shape == donut:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top+ half), half - 5)
        pygame.draw.circle(DISPLAYSURF, bg_color, (left + half, top + half), quarter - 5)
    elif shape == square:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, box_size - half, box_size - half))
    elif shape == diamond:
        pygame.draw.polygon(DISPLAYSURF, color, (
        (left + half, top), (left + box_size - 1, top + half), (left + half, top + box_size - 1), (left, top + half)))
    elif shape == lines:
        for i in range(0, box_size, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + box_size - 1), (left + box_size - 1, top + i))
    elif shape == oval:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, box_size, half))


def getShapeAndColor(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]


def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, bg_color, (left, top, box_size, box_size))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0:
            pygame.draw.rect(DISPLAYSURF, box_color,(left, top, coverage, box_size))
    pygame.display.update()
    fps_clock.tick(fps)

def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(box_size, (-reveal_speed) - 1, -reveal_speed):
        drawBoxCovers(board, boxesToReveal, coverage)

def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, box_size + reveal_speed, reveal_speed):
        drawBoxCovers(board, boxesToCover, coverage)

def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(board_width):
        for boxy in range(board_height):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF, box_color, (left, top, box_size, box_size))
            else:
                # Draw the (revealed) icon.
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)

def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect( DISPLAYSURF, high_light_color, (left - 5, top - 5,  box_size + 10, box_size + 10), 4)

def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(board_width):
        for y in range(board_height):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = light_bg_color
    color2 = bg_color

    for i in range(13):
        color1, color2 = color2, color1
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)

def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:
            return
    return True

if __name__ == '__main__':
    main()
