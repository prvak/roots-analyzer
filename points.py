#!/usr/bin/python
import pygame
import os
import sys
import math

class FileList:
    """Class representing a list of image files. """

    """Supported file extensions."""
    supportedExtensions = (".bmp", ".jpg", ".png")
    
    """Position of next filename to be returned by 'nextImageFile()'."""
    position = -1

    """List of image files."""
    imageFiles = []

    def __init__(self, directories):
        """Read files in given directories."""
        for directory in directories:
            self.findImageFilesInDirectory(directory)

    def findImageFilesInDirectory(self, directory):
        # Get list of image files from each directory.
        fileList = os.listdir(directory)
        # Walk through all files in the directory and ignore those that do not match any
        # supported extension.
        for filename in fileList:
            fullPath = os.path.join(directory, filename)
            if os.path.isfile(fullPath):
                (jmeno, extension) = os.path.splitext(filename)
                # lowercase because 'BMP' is the same as 'bmp'
                extension = extension.lower()
                if extension in self.supportedExtensions:
                    self.imageFiles.append(fullPath)
        self.imageFiles = sorted(self.imageFiles)

    def currentImageFile(self):
        """Returns currently displayed file."""
        if self.position >= 0 and self.position < len(self.imageFiles):
            return self.imageFiles[self.position]
        else:
            return ""
    
    def nextImageFile(self):
        """Returns next file to display."""
        if self.isEnd():
            return ""
        else:
            self.position = self.position + 1
            jmenoSouboru = self.imageFiles[self.position]
            return jmenoSouboru
    
    def previousImageFile(self):
        """Returns previous file to display."""
        if self.isStart():
            return ""
        else:
            self.position = self.position - 1
            return self.imageFiles[self.position]

    def isEnd(self):
        """Returns true if currently displayed file is the last one in the list."""
        return self.position == len(self.imageFiles) - 1

    def isStart(self):
        """Returns true if currently displayed file is the first one in the list."""
        return self.position <= 0

class SelectedPoint:
    """Class representing a point selected in the image."""

    """Circle diameter in pixels."""
    CIRCLE_DIAMETER = 15

    """Line width in pixels."""
    CIRCLE_LINE_WIDTH = 1
    
    """Central cross line length."""
    CIRCLE_CROSS_LENGTH = CIRCLE_DIAMETER / 3
    
    """How many pixels from the center of the circle should the cross line end. This way the selected point is
    not obscured by the central cross."""
    CIRCLE_CROSS_SPACE = 3

    def __init__(self, color):
        # nove vytvoreny bod je skryty
        self.isVisible = False
        # position je na pocatku 0,0, bude nastavena po kliknuti mysi, position urcuje stred obrazku
        self.position = (0, 0)
        # krome position si budeme pamatovat i ohraniceni obrazku, tj. obdelnik ve kterem je obrazek nakreslen
        r = SelectedPoint.CIRCLE_DIAMETER
        self.boundary = pygame.Rect(-r, -r, r * 2, r * 2)
        # point is represented by a circle with a cross
        # prepare the image in memory
        self.image = pygame.Surface((SelectedPoint.CIRCLE_DIAMETER * 2, SelectedPoint.CIRCLE_DIAMETER * 2))
        self.image.set_colorkey(0x000000) # nastavi cernou barvu jako pruhlednou
        # the cross
        pygame.draw.line(self.image, color, (SelectedPoint.CIRCLE_DIAMETER - SelectedPoint.CIRCLE_CROSS_LENGTH, SelectedPoint.CIRCLE_DIAMETER), (SelectedPoint.CIRCLE_DIAMETER - SelectedPoint.CIRCLE_CROSS_SPACE, SelectedPoint.CIRCLE_DIAMETER))
        pygame.draw.line(self.image, color, (SelectedPoint.CIRCLE_DIAMETER + SelectedPoint.CIRCLE_CROSS_LENGTH, SelectedPoint.CIRCLE_DIAMETER), (SelectedPoint.CIRCLE_DIAMETER + SelectedPoint.CIRCLE_CROSS_SPACE, SelectedPoint.CIRCLE_DIAMETER))
        pygame.draw.line(self.image, color, (SelectedPoint.CIRCLE_DIAMETER, SelectedPoint.CIRCLE_DIAMETER - SelectedPoint.CIRCLE_CROSS_LENGTH), (SelectedPoint.CIRCLE_DIAMETER, SelectedPoint.CIRCLE_DIAMETER - SelectedPoint.CIRCLE_CROSS_SPACE))
        pygame.draw.line(self.image, color, (SelectedPoint.CIRCLE_DIAMETER, SelectedPoint.CIRCLE_DIAMETER + SelectedPoint.CIRCLE_CROSS_LENGTH), (SelectedPoint.CIRCLE_DIAMETER, SelectedPoint.CIRCLE_DIAMETER + SelectedPoint.CIRCLE_CROSS_SPACE))
        # the circle
        pygame.draw.circle(self.image, color, (SelectedPoint.CIRCLE_DIAMETER, SelectedPoint.CIRCLE_DIAMETER), SelectedPoint.CIRCLE_DIAMETER, SelectedPoint.CIRCLE_LINE_WIDTH)
        # in order to be able to move the circle aroud we are going to store the background of the circle
        # and use it to restore the original image if the point is moved
        self.background = pygame.Surface((SelectedPoint.CIRCLE_DIAMETER * 2, SelectedPoint.CIRCLE_DIAMETER * 2))

    def show(self, window, position):
        """Draw this point at given position in given window."""
        if not self.isVisible:
            self.position = position
            self.boundary.topleft = [position[0] - SelectedPoint.CIRCLE_DIAMETER, position[1] - SelectedPoint.CIRCLE_DIAMETER]
            # save background so we can restore it if the point is moved
            self.background.blit(window, self.background.get_rect(), self.boundary)
            # draw the image
            window.blit(self.image, self.boundary)
            self.isVisible = True
        else:
            raise Exception("Can not display already visible point!")
    
    def redraw(self, window, position):
        """Redraw already visible point."""
        if self.isVisible:
            # redraw the last position with the background
            window.blit(self.background, self.boundary)
            # update position
            self.position = position
            self.boundary.topleft = [position[0] - SelectedPoint.CIRCLE_DIAMETER, position[1] - SelectedPoint.CIRCLE_DIAMETER]
            # save new background
            self.background.blit(window, self.background.get_rect(), self.boundary)
            # draw circle at the new position
            window.blit(self.image, self.boundary)
        else:
            raise Exception("Can not redraw point that is not visible.")
        
    def hide(self, window):
        """Hide visible point."""
        if self.isVisible:
            # redraw last position with background image
            window.blit(self.background, self.boundary)
            self.isVisible = False
        else:
            raise Exception("Can not hide already hidden point!")

    def isPositionNearPoint(self, position):
        x1, y1 = self.position
        x2, y2 = position
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) < SelectedPoint.CIRCLE_DIAMETER

    def distanceFromCenter(self, position):
        """Returns distance of given position from the center of the circle. Usefull for dragging the circle."""
        x1, y1 = self.position
        x2, y2 = position
        return (x2 - x1, y2 - y1)

class SelectedPoints:
    def __init__(self):
        self.points = []
        self.points.append(SelectedPoint(0xff0000))
        self.points.append(SelectedPoint(0x00ff00))
        self.points.append(SelectedPoint(0x0000ff))
        self.points.append(SelectedPoint(0xffff00))

    def readPoints(self, window, record, ratio, x0, y0):
        """Read points from given record and display them."""
        self.reset()
        for (position, point) in zip(record.points, self.points):
            if position != (-1, -1):
                # transform position in the image to position at screen
                x, y = position # position in the image
                x = x * ratio + x0
                y = y * ratio + y0
                point.show(window, (x, y))

    def addPoint(self, window, position):
        for point in self.points:
            if not point.isVisible:
                point.show(window, position)
                break
    
    def removePoint(self, window, position):
        pointAtPosition = self.getPointAt(position)
        if pointAtPosition != None:
            pointAtPosition.hide(window)

    def getPointAt(self, position):
        """Returns point at given position (or nearby) or None if there is no point there."""
        pointAtPosition = None
        for points in self.points:
            if points.isVisible:
                if points.isPositionNearPoint(position):
                    pointAtPosition = points
        return pointAtPosition
    
    def reset(self):
        """Mark all points as hidden."""
        for bod in self.points:
            bod.isVisible = False
        
        
class Record:
    """Class representing a record in the database."""
   
    @staticmethod
    def header():
        return "#jmeno,hash,x0,y0,x1,y1,x2,y2,x3,y3"

    def __init__(self):
        self.filename = ""
        self.hash = 0
        self.points = [(-1, -1), (-1, -1), (-1, -1), (-1, -1)] # -1,-1 means not initialized

    def set(self, imageFile, imageHash):
        self.filename = imageFile
        self.hash = imageHash # to detect that the file changed
        self.points = [(-1, -1), (-1, -1), (-1, -1), (-1, -1)] # -1,-1 means not initialized

    def load(self, line):
        columns = line.split(",")
        if len(columns) == 10:
            self.filename = os.path.split(columns[0])[1] # ignore directory name
            self.hash = int(columns[1])
            for i in xrange(4):
                x = int(columns[2 + i*2])
                y = int(columns[2 + i*2 + 1])
                self.points[i] = ((x, y))

    def save(self):
        radek = "%s,%d" % (self.filename, self.hash)
        for bod in self.points:
            radek = radek + ",%d,%d" % bod
        return radek

    def setPoints(self, selectedPoints, ratio, x0, y0):
        index = 0
        for point in selectedPoints.points:
            if point.isVisible:
                x, y = point.position
                x = (x-x0) / ratio
                y = (y-y0) / ratio
                self.points[index] = (x, y)
            else:
                self.points[index] = (-1, -1)
            index = index + 1


class Database:
    """Database of point records for multiple image files."""

    def __init__(self, dbFilename):
        """Create new database in given file or load it if the file already exists."""
        self.records = {}
        self.dbFilename = dbFilename
        if os.path.exists(dbFilename) and os.path.isfile(dbFilename):
            # nacti zaznamy ze souboru
            print "Loading database file: " + dbFilename
            self.load()
        else:
            # create empty file with header
            print "Creating database file: " + dbFilename
            file = open(self.dbFilename, "w")
            line = Record.header() + "\n"
            file.write(line)
            file.close()

    def load(self):
        file = open(self.dbFilename)
        lines = file.readlines()
        file.close()
        for line in lines:
            line = line.strip()
            if len(line) > 0 and line[0] != "#":
                # ignore empty lines and lines starting with #
                record = Record()
                record.load(line)
                self.records[record.filename] = record

    def save(self):
        file = open(self.dbFilename, "w")
        line = Record.header() + "\n"
        file.write(line)
        keys = sorted(self.records.keys())
        for key in keys:
            line = self.records[key].save() + "\n"
            file.write(line)
        file.close()

    
def createWindow():
    pygame.init()
    pygame.display.init()

    #window = pygame.display.set_mode((800,600), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE) # fullscreen, but draws only in the middle
    #window = pygame.display.set_mode((0,0), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE) # true fulscreen
    window = pygame.display.set_mode((800,600), pygame.DOUBLEBUF|pygame.HWSURFACE) # just a window

    pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
    pygame.event.set_allowed(pygame.KEYDOWN)
    return window

def loadImage(imagePath):
    return pygame.image.load(imagePath).convert()

def drawImage(image, window):
    """Draw image so that it fits into the window. Returns coordinates of upper left corner, scaled image dimensions
    and scaling ratio."""
    
    # get dimensions of the window and the image
    windowWidth, windowHeight = window.get_size()
    imageWidth, imageHeight = image.get_size()

    # compute dimension that would fit the window, keep the image size ratio
    if float(windowWidth)/imageWidth > float(windowHeight) / imageHeight:
        ratio = float(windowHeight)/imageHeight
        imageWidth = imageWidth * windowHeight / imageHeight
        imageHeight = windowHeight
        x0 = (windowWidth - imageWidth) / 2
        y0 = 0
    else:
        ratio = float(windowWidth) / imageWidth
        imageHeight = imageHeight * windowWidth / imageWidth
        imageWidth = windowWidth
        y0 = (windowHeight - imageHeight) / 2
        x0 = 0

    # scale the image so that it fits the window
    scaledImage = pygame.transform.scale(image, (imageWidth, imageHeight))

    # fill whole screen with background color
    wholeWindowRectangle = pygame.Rect(0, 0, windowWidth, windowHeight)
    pygame.draw.rect(window, 0x424242, wholeWindowRectangle)
    
    # draw image
    imageRectangle = pygame.Rect(0, 0, imageWidth, imageHeight) # what part of the image to display (the whole image)
    obdelnikOkna = pygame.Rect(x0, y0, imageWidth, imageHeight) # where to put the image
    window.blit(scaledImage, obdelnikOkna, imageRectangle)
    
    return (x0, y0, imageWidth, imageHeight, ratio)

def drawImageFromFile(imagePath, window, database, selectedPoints):
    imageFilename = os.path.split(imagePath)[1] # just the filename
    imageHash = 0
    if database.records.has_key(imageFilename):
        record = database.records[imageFilename]
    else:
        # no record for this image in the database
        record = Record()
        record.set(imageFilename, imageHash)
        database.records[imageFilename] = record
    image = loadImage(imagePath)
    (x0, y0, imageWidth, imageHeight, ratio) = drawImage(image, window)
    pygame.display.set_caption(imagePath)
    selectedPoints.readPoints(window, record, ratio, x0, y0)
    pygame.display.flip()
    return (x0, y0, imageWidth, imageHeight, ratio, record)

def displayNextImage(fileList, window, databaze, selectedPoints):
    """Display next image. There must be an image to display. Returns coordinates of upper left corner,
    scaled image dimensions and scaling ratio."""
    imagePath = fileList.nextImageFile()
    return drawImageFromFile(imagePath, window, databaze, selectedPoints)

def displayPreviousImage(fileList, window, databaze, selectedPoints):
    """Display previous image. There must be a previous image to display. Returns coordinates of upper left corner,
    scaled image dimensions and scaling ratio."""
    imagePath = fileList.previousImageFile()
    return drawImageFromFile(imagePath, window, databaze, selectedPoints)

def usage():
    print "Usage: points.py DIRECTORY"
    print "    DIRECTORY Directory with images to add points to."



# check commandline arguments
if len(sys.argv) <= 1:
    print "Missing arguments."
    exit()
elif len(sys.argv) >= 3:
    print "Too many arguments."
    exit()

# parse commandline arguments
directory = sys.argv[1]
if directory[-1] != '/':
    directory = directory + '/'

if not os.path.isdir(directory):
    print "Not a directory:"
    print directory
    exit()

fileList = FileList([directory])
if fileList.isEnd():
    print "No acceptable files in directory:"
    print directory
    exit()

window = createWindow()
database = Database(directory[:-1] + ".csv")
selectedPoints = SelectedPoints()

# load and display first image
(x0, y0, imageWidth, imageHeight, ratio, record) = displayNextImage(fileList, window, database, selectedPoints)

movedPoint = None
movedPointHeldAt = (0, 0) # distance of the drag point from the center of the circle
bodPresunut = False
while(1):
    # event loop
    event = pygame.event.wait()
    if event.type==pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            # 1 == left button
            movedPoint = selectedPoints.getPointAt(event.pos)
            if movedPoint != None:
                movedPointHeldAt = movedPoint.distanceFromCenter(event.pos)
            bodPresunut = False
        elif event.button == 3:
            # 3 == right button
            selectedPoints.removePoint(window, event.pos)
            pygame.display.flip()
    elif event.type==pygame.MOUSEBUTTONUP:
        if event.button == 1 and (movedPoint == None or bodPresunut == False):
            # no circle was clicked or a circle was clicked but not moved
            x,y = event.pos
            if (x >= x0 and x <= x0 + imageWidth) and (y >= y0 and y <= y0 + imageHeight):
                # ignore clicks outside of the image
                selectedPoints.addPoint(window, (x, y))
                pygame.display.flip()
        movedPoint = None
    elif event.type==pygame.MOUSEMOTION:
        if movedPoint != None:
            x, y = event.pos
            x1, y1 = movedPointHeldAt
            if (x - x1 >= x0 and x - x1 <= x0 + imageWidth) and (y - y1 >= y0 and y - y1 < y0 + imageHeight):
                # do not move outside of the image
                nx, ny = (x - x1, y - y1)
            else:
                # mouse pointer is outside of the image but it stil holds the circle, move the circle along the edge
                nx, ny = (x - x1, y - y1)
                if x - x1 < x0:
                    nx = x0
                elif x - x1 > x0 + imageWidth:
                    nx = x0 + imageWidth
                if y - y1 < y0:
                    ny = y0
                elif y - y1 > y0 + imageHeight:
                    ny = y0 + imageHeight
            movedPoint.redraw(window, (nx, ny))
            pygame.display.flip()
            bodPresunut = True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
            # right arrow => display next image
            if not fileList.isEnd():
                record.setPoints(selectedPoints, ratio, x0, y0)
                database.save()
                (x0, y0, imageWidth, imageHeight, ratio, record) = displayNextImage(fileList, window, database, selectedPoints)
        elif event.key == pygame.K_LEFT:
            # left arrow => display previous image
            if not fileList.isStart():
                record.setPoints(selectedPoints, ratio, x0, y0)
                database.save()
                (x0, y0, imageWidth, imageHeight, ratio, record) = displayPreviousImage(fileList, window, database, selectedPoints)
        elif event.key == pygame.K_ESCAPE:
            # esc => end program
            record.setPoints(selectedPoints, ratio, x0, y0)
            database.save()
            exit()
        else:
            pass
    elif event.type == pygame.QUIT:
        # window closed, save and exit
        record.setPoints(selectedPoints, ratio, x0, y0)
        database.save()
        exit()

