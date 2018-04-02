#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame
import os
import sys

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

    def filePosition(self):
        """Returns 'file position/total files'."""
        return "%d/%d" % (self.position + 1, len(self.imageFiles))

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

class Route:
    def __init__(self, point, color, width):
        self.color = color
        self.width = width
        self.points = [point] # starting point of the route
        self.isTerminated = False

    def add(self, bod):
        self.points.append(bod)

    def terminate(self):
        self.isTerminated = True

    def draw(self, image):
        for index in xrange(len(self.points) - 1):
            self.drawSection(image, index)

    def drawLastSection(self, image):
        self.drawSection(image, len(self.points) - 2)

    def drawSection(self, image, index):
        a = self.points[index]
        b = self.points[index + 1]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        lx = abs(dx)
        ly = abs(dy)
        l = max(lx, ly)
        if l > 0:
            for bod in [(int(a[0]+1.0*n*dx/l), int(a[1]+1.0*n*dy/l)) for n in xrange(l)]:
                pygame.draw.circle(image, self.color, bod, self.width / 2, 0)
        else:
            # two points at the same location
            pygame.draw.circle(image, self.color, a, self.width / 2, 0)
            

class Button:
    def __init__(self, name, color, color2, event, isWithText = True):
        self.name = name
        self.color = pygame.Color(color)
        self.color2 = pygame.Color(color2)
        self.event = event
        self.isWithText = isWithText
        self.rectangle = None
        self.isSelected = False
        self.isMarked = False
        self.group = None
    
    def jeNaPozici(self, bod):
        if self.rectangle:
            return self.rectangle.collidepoint(bod)
        return False

    def setGroup(self, group):
        self.group = group

    def push(self):
        if self.group:
            for t in self.group:
                t.select(False)
            self.select(True)
        self.sendEvent()

    def select(self, isSelected):
        self.isSelected = isSelected
        self.redraw()
    
    def mark(self, isMarked):
        self.isMarked = isMarked
        self.redraw()

    def draw(self, window, rectangle):
        self.rectangle = rectangle
        self.window = window
        self.redraw()

    def redraw(self):
        borderColor = pygame.Color(0x00000000)
        backgroundColor = self.color
        if self.isMarked:
            backgroundColor = self.color2
        if self.isSelected or self.isMarked:
            borderColor = pygame.Color(0xedd53300)
        self.window.fill(backgroundColor, self.rectangle)
        pygame.draw.rect(self.window, borderColor, self.rectangle, 2)
        if self.isWithText:
            text = font.render(self.name, True, borderColor)
            textRectangle = text.get_rect()
            textRectangle.center = self.rectangle.center
            self.window.blit(text, textRectangle)
        pygame.display.update(self.rectangle) # zobrazime provedenou zmenu 
     
    def sendEvent(self):
        event = pygame.event.Event(pygame.USEREVENT, code=self.event)
        pygame.event.post(event)

class ColorButton(Button):
    def __init__(self, name, color, color2):
        Button.__init__(self, name, color, color2, "color", False)
     
    def sendEvent(self):
        event = pygame.event.Event(pygame.USEREVENT, code=self.event, color=self.color)
        pygame.event.post(event)
        

class Menu:
    def __init__(self):
        with open("colors.cfg") as f:
            f.readline() # first line contains headers, ignore it
            lines = f.readlines()
        
        self.colorButtons = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            (name, color, remainder) = line.split(";", 2) # only interested in first two columns
            button = ColorButton(name, int(color + "00", 16), int(color + "55", 16))
            self.colorButtons.append(button)
        self.colorButtons.append(ColorButton("Bila", "0xffffff00", "0xffffff55"))
        self.thicknesButtons = []
        self.thicknesButtons.append(Button(u"Thick", 0xffffff00, 0xdddddd00, "thick"))
        self.thicknesButtons.append(Button(u"Thin", 0xffffff00, 0xdddddd00, "thin"))
        self.buttons = []
        self.buttons.extend(self.colorButtons)
        self.buttons.extend(self.thicknesButtons)
        self.buttons.append(Button(u"Undo", 0xffffff00, 0xdddddd00, "undo"))
        self.buttons.append(Button("+", 0xffffff00, 0xdddddd00, "+"))
        self.buttons.append(Button("-", 0xffffff00, 0xdddddd00, "-"))
        self.buttons.append(Button(u"Next", 0xffffff00, 0xdddddd00, "next"))
        for t in self.colorButtons:
            t.setGroup(self.colorButtons)
        for t in self.thicknesButtons:
            t.setGroup(self.thicknesButtons)
        self.colorButtons[0].isSelected = True
        self.thicknesButtons[0].isSelected = True
        self.rectangle = None # rectangle where the menu is drawn

    def onClick(self, bod):
        """Provede akci po stisknuti tlacitka na pozici 'bod'.
        Vraci True, pokud bylo kliknuto na nejake button, jinak vraci False."""
        return False

    def buttonAtPosition(self, bod):
        if self.buttons:
            for t in self.buttons:
                if t.jeNaPozici(bod):
                    return t
        return None

    def draw(self, window):
        o = window.get_rect()
        s = 80
        self.rectangle = pygame.Rect(o.width - s, 0, s, o.height)
        buttonCount = len(self.buttons)
        if buttonCount > 0:
            v = self.rectangle.height/buttonCount # height of one buttonn
            x = self.rectangle.left # distance of the button from the left side
            for i in xrange(buttonCount):
                y = i*v
                button = self.buttons[i]
                buttonRectangle = pygame.Rect(x, y, s, v)
                button.draw(window, buttonRectangle)

class Manager:
    def __init__(self, menu, window, filenames):
        self.window = window
        self.menu = menu
        self.filenames = filenames
        self.color = menu.colorButtons[0].color
        self.thick()
        self.zoom = 1 
        self.backgroundColor = pygame.Color(0x12670b00)
        
    def load(self, previous = False):
        if previous:
            filename = self.filenames.previousImageFile()
        else:
            filename = self.filenames.nextImageFile()
        if not filename:
            print "No more files. Exiting."
            return False
        print "Loading file '%s'" % (filename)
        self.image = loadImage(filename) # original image
        self.changedImage = self.image.copy() # image with changes
        self.zoomedImage = self.image.copy() # image with changes and zoom
        self.routes = [] # routes added to image
        self.removedRoutes = []
        # how many displayed pixels corespond to 1 pixel in original image
        self.shift = (0, 0)
        self.redraw()
        return True

    def save(self):
        filename = self.filenames.currentImageFile()
        if self.routes:
            print "Saving file '%s'" % (filename)
            pygame.image.save(self.changedImage, self.filenames.currentImageFile())
        else:
            print "No changes in file '%s'" % (filename)

    def thin(self):
        self.lineWidth = 2
    
    def thick(self):
        self.lineWidth = 8
    
    def zoomIn(self):
        self.zoom = self.zoom + 1
        if self.zoom > 8:
            self.zoom = 8
        size = [x * self.zoom for x in self.changedImage.get_size()]
        self.zoomedImage = pygame.transform.scale(self.changedImage, size)
        self.redraw()

    def zoomOut(self):
        self.zoom = self.zoom - 1
        if self.zoom <= 1:
            self.zoom = 1
        size = [x * self.zoom for x in self.changedImage.get_size()]
        self.zoomedImage = pygame.transform.scale(self.changedImage, size)
        self.redraw()

    def setColor(self, color):
        self.color = color

    def drag(self, shift):
        self.shift = [sum(x) for x in zip(self.shift, shift)]
        self.redraw()

    def draw(self, point, terminate = False):
        point2 = [int((x[0]-x[1]) / self.zoom) for x in zip(point, self.shift)]
        if not self.routes or self.routes[-1].isTerminated:
            # no route exists yet or the last route is terminated
            # create new route starting with this point
            route = Route(point2, self.color, self.lineWidth)
            self.routes.append(route)
        else:
            # update last route
            route = self.routes[-1]
        if terminate:
            # terminate current route
            route.terminate()
        point1 = route.points[-1]
        # find region, that will contain all changed pixels
        # for efficiency reasons we will zoom and redraw only this region
        t = route.width
        upperLeft = [min(x)-t for x in zip(point1,point2)]
        size = [abs(x[1] - x[0])+3*t for x in zip(point1, point2)]
        selectionRectangle = pygame.Rect(upperLeft, size)
        imageRectangle = self.changedImage.get_rect()
        selectionRectangle = selectionRectangle.clamp(imageRectangle)
        if self.menu.buttonAtPosition(point) or not imageRectangle.contains(selectionRectangle):
            # drawing outside of the image, terminate route to prevent long line when the cursor reenters the image
            route.terminate()
            if len(route.points) == 1:
                # route contains only one point and that point lies outside of the image, remove route
                self.routes.pop()
            return # no redraw
        route.add(point2)
        # draw line to the changed image
        route.drawLastSection(self.changedImage)
        # cut selection rectangle from changed image in original scale
        selection = self.changedImage.subsurface(selectionRectangle)
        # scale the selection to current zoom
        upperLeft = selectionRectangle.topleft
        zoomedUpperLeft = [x * self.zoom for x in upperLeft]
        size = selectionRectangle.size
        zoomedSize = [x * self.zoom for x in size]
        zoomedSelection = pygame.transform.scale(selection, zoomedSize)
        # redraw currently displayed image
        self.zoomedImage.blit(zoomedSelection, zoomedUpperLeft)
        self.redraw(zoomedSelection.get_rect())

    def undo(self):
        if not self.routes:
            return
        self.routes.pop()
        self.changedImage = self.image.copy()
        for c in self.routes:
            c.draw(self.changedImage)
        velikost = [x * self.zoom for x in self.changedImage.get_size()]
        self.zoomedImage = pygame.transform.scale(self.changedImage, velikost)
        self.redraw()

    def redo(self):
        pass

    def redraw(self, selection = None):
        windowRectangle = self.window.get_rect()
        if not selection:
            selection = windowRectangle
        imageRectangle = self.zoomedImage.get_rect().move(self.shift[0], self.shift[1])
        # fill whole screan with background color
        pygame.draw.rect(window, self.backgroundColor, selection)
        
        # draw image
        window.blit(self.zoomedImage, imageRectangle)
        
        # display filename
        text = font.render(self.filenames.filePosition() + ": " + self.filenames.currentImageFile(), True, pygame.Color(0x00000000))
        rectangleTextu = text.get_rect()
        rectangleTextu.topleft = windowRectangle.topleft
        self.window.blit(text, rectangleTextu)
        
        # draw menu
        self.menu.draw(window)
        # draw changes
        pygame.display.update() 
    

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
    obrazek = pygame.image.load(imagePath).convert()
    return obrazek

def usage():
    print "Usage: colors.py DIRECTORY"
    print "    DIRECTORY Directory with images to colorize."


# check commandline arguments
if len(sys.argv) <= 1:
    print "Missing arguments."
    exit()
elif len(sys.argv) >= 3:
    print "Too many arguments."
    exit()

# parse commandline arguments
adresar = sys.argv[1]
if adresar[-1] != '/':
    adresar = adresar + '/'

if not os.path.isdir(adresar):
    print "Not a directory:"
    print adresar
    exit()

fileList = FileList([adresar])
if fileList.isEnd():
    print "No acceptable files in directory:"
    print adresar
    exit()

window = createWindow()
font = pygame.font.Font("font.ttf", 15)
menu = Menu()
manager = Manager(menu, window, fileList)

# load and display first image
manager.load()
heldBy = None
drawnFrom = None
button = None
while(1):
    # event loop
    event = pygame.event.wait()
    if event.type==pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            # 1 == left button
            manager.draw(event.pos) # zacatek cary
            drawnFrom = event.pos
        elif event.button == 2:
            # 2 == middle button
            heldBy = event.pos
    elif event.type==pygame.MOUSEBUTTONUP:
        if event.button == 1:
            manager.draw(event.pos, True)
            drawnFrom = None
            t = menu.buttonAtPosition(event.pos)
            if t and button:
                # mouse is over the button
                button.push()
                button = t
            else:
                button = None
        elif event.button == 2:
            if heldBy and heldBy != event.pos:
                manager.drag([x[1] - x[0] for x in zip(heldBy, event.pos)])
            heldBy = None
    elif event.type==pygame.MOUSEMOTION:
        if heldBy:
            # image is being dragged
            manager.drag([x[1] - x[0] for x in zip(heldBy, event.pos)])
            heldBy = event.pos
        elif drawnFrom:
            manager.draw(event.pos) # line continued
            drawnFrom = event.pos
        else:
            t = menu.buttonAtPosition(event.pos)
            if t:
                # mouse is over the button
                if button != t:
                    if button:
                        button.mark(False)
                    t.mark(True)
                button = t
            else:
                if button:
                    button.mark(False)
                button = None
                # draw jen pokud nejsme nad tlacitkem
    elif event.type == pygame.USEREVENT:
        if event.code == "color":
            manager.setColor(event.color)
        elif event.code == "thin":
            manager.thin()
        elif event.code == "thick":
            manager.thick()
        elif event.code == "undo":
            manager.undo()
        elif event.code == "next":
            manager.save()
            if not manager.load():
                exit()
        elif event.code == "+":
            manager.zoomIn()
        elif event.code == "-":
            manager.zoomOut()
    
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
            # right arrow => next image
            manager.save()
            if not manager.load():
                exit()
        if event.key == pygame.K_LEFT:
            # left arrow => previous image
            manager.save()
            if not manager.load(True): # True == load previous image
                exit()
        elif event.key == pygame.K_ESCAPE:
            # esc => terminate program
            manager.save()
            exit()
        else:
            pass
    elif event.type == pygame.QUIT:
        # window closed, save and exit
        manager.save()
        exit()

