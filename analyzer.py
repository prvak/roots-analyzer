import math
from collections import deque
import colorsys # for rgb_to_hsv, rgb_to_yiq
from PIL import Image, ImageColor
import operator

class AnalyzerError (Exception):
    def __init__(self, text):
        Exception.__init__(self, text)

class Coordinates:
    """List of coordinates for each pixel.
    
    This class is used to quickly convert coordinates to index and index to
    coordinates."""

    def __init__(self, size):
        self._w = size[0]
        self._h = size[1]
        #self._coords = tuple([(x,y) for y in xrange(size[1]) 
        #                            for x in xrange(size[0])])
        #self._indexes = tuple(range(len(self._coords)))

    def width(self):
        return self._w
    
    def height(self):
        return self._h

    def size(self):
        return (self._w, self._h)

    def total(self):
        return self._w * self._h

    def coords(self):
        return ((x,y) for y in xrange(self._h) for x in xrange(self._w))
        #return self._coords

    def indexes(self):
        return xrange(self.total())
        #return self._indexes

    def coord_to_index(self, coord):
        """Return index of given coordinates."""
        return coord[1] * self._w + coord[0]

    def index_to_coord(self, index):
        """Return coordinates of given index."""
        x = index % self._w
        y = index / self._w
        return (x, y)
        #return self._coords[index]

class Neighbours:
    """List of neighbours of each pixel.
    
    Neighbours can be accessed by x, y coordinates or by index of the pixel.
    Top left pixel has index 0, bottom right pixel has index width * height - 1
    and top right pixel has index widht - 1."""

    def __init__(self, coords, eight):
        # list of coordinates and indexes of each pixel
        # this structure also holds information about size of the original
        # image
        self._coords = coords
        self._eight = eight

        # generate lists of neighbours for each pixel
        # list of neighbours represented as coordinates
        #self._neigh_c = [self._generate(i, eight) 
        #                    for i in xrange(coords.total())]
        # list of neighbours represented as indexes
        #self._neigh_i = [[self._coords.coord_to_index(c) for c in n]
        #                    for n in self._neigh_c]

    def _generate(self, index, eight):
        """Generate list of coordinates of a pixel with index 'index'."""
        w = self._coords.width()
        h = self._coords.height()
        x, y = self._coords.index_to_coord(index)
        if eight:
            # generate all eight neighbours (even invalid ones)
            n = [   
                    (x - 1, y - 1),
                    (x    , y - 1),
                    (x + 1, y - 1),
                    (x - 1, y    ),
                    (x + 1, y    ),
                    (x - 1, y + 1),
                    (x    , y + 1),
                    (x + 1, y + 1)
                ]
        else:
            # generate all four neighbours (even invalid ones)
            n = [   
                    (x    , y - 1),
                    (x - 1, y    ),
                    (x + 1, y    ),
                    (x    , y + 1)
                ]

        # filter out invalid neighbours
        n2 = ((x, y) for x, y in n if x >= 0 and x < w and y >= 0 and y < h)
        return n2

    def neighs_as_indexes(self, pixel):
        if type(pixel) == tuple:
            return (self._coords.coord_to_index(c) for c in 
                    self.neighs_as_coords(self._coords.coord_to_index(pixel)))
            #return self._neigh_i[self._coords.coord_to_index(pixel)]
        else:
            return (self._coords.coord_to_index(c) for c in self.neighs_as_coords(pixel))
            #return self._neigh_i[pixel]
    
    def neighs_as_coords(self, pixel):
        if type(pixel) == tuple:
            return self._generate(self._coords.coord_to_index(pixel), self._eight)
            #return self._neigh_c[self._coords.coord_to_index(pixel)]
        else:
            return self._generate(pixel, self._eight)
            #return self._neigh_c[pixel]

class Analyzer:
    def __init__(self, img, verbose = False):
        self._verbose = verbose
        self._coords = Coordinates(img.size)
        self._neigh4 = Neighbours(self._coords, False)
        self._neigh8 = Neighbours(self._coords, True)
        self._colors = []
        with open("barvy.cfg") as f:
            f.readline() # first line contains headers
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                (name, color, others) = line.split(";", 2)
                color = ImageColor.getrgb("#"+color[2:]) # color must be in form '#rrggbb'
                self._colors.append((name, color))
    
    def filter_background(self, img, 
            color_threshold = 180, group_threshold = 5):
        # light colors will be marked as background
        pixels = [0 if img.getpixel(c) > color_threshold else 1 
                    for c in self._coords.coords()]
        # assign each pixel a group number, group is a continuous section
        # of background or foreground pixels
        groups, indexes = self._groups_init(pixels, self._neigh4)
        while min((len(g) for g in indexes)) <= group_threshold:
            groups, indexes = self._groups_prune(pixels, groups, indexes, 
                    self._neigh4, group_threshold)

        return pixels, groups, indexes
    
    def filter_background2(self, img, group_threshold = 5):
        # light colors will be marked as background
        colors = [record[1] for record in self._colors]
        pixels = [1 if img.getpixel(c) in colors else 0
                    for c in self._coords.coords()]
        # assign each pixel a group number, group is a continuous section
        # of background or foreground pixels
        groups, indexes = self._groups_init(pixels, self._neigh4)
        while min((len(g) for g in indexes)) <= group_threshold:
            groups, indexes = self._groups_prune(pixels, groups, indexes, 
                    self._neigh4, group_threshold)

        return pixels, groups, indexes

    def measure_skeleton(self, img, dpi, color_threshold = 128):
        """Measures total length of the skeleton in the image 'img'.
        
        Returns length of the skeleton in milimeters and number of 
        branches of the skeleton. If there is no skeleton
        or more then one skeleton than None is returned."""
        pixels = [0 if img.getpixel(c) < color_threshold else 1 
                    for c in self._coords.coords()]
        groups, indexes = self._groups_init(pixels, self._neigh8)
        fg_indexes = filter(lambda i: pixels[i[0]] == 1, indexes)
        if len(fg_indexes) == 0:
            raise AnalyzerError("No skeleton found")
        elif len(fg_indexes) > 1:
            raise AnalyzerError("Too many skeletons (%d)." % (len(fg_indexes)))
        fg = fg_indexes[0] # select first (and the only) skeleton

        direct = 0 # number of directly connected pixels
        diagonal = 0 # number of diagonally connected pixels
        tails = 0 # number of tails of the skeleton
        queue = deque([fg[0]]) # select first pixel of the skeleton
        while len(queue) > 0:
            # get next index
            index = queue.popleft()
            if pixels[index] == 1:
                # add selected neighbour to current group
                pixels[index] = 2 # 0 == bg, 1 == fg, 2 == visited fg
                indexes.append(index)
                # get neighbours of selected index
                all_neighbours = self._neigh8.neighs_as_indexes(index)
                # filter out those neighbours that have already been visited
                # or that are background
                neighbours = filter(lambda n: pixels[n] == 1, all_neighbours)
                # detect end of a tail
                if (len(neighbours) == 0 or
                   (len(neighbours) == 1 and direct + diagonal == 0)):
                   # if there are no neighbours that haven't been visited
                   # yet or if the first pixel has exactly one neighbour
                   # then the end of the tail was encountered
                   tails += 1
                # count number of diagonal neighbours and number 
                # of direct neighbours
                direct_neighbours = self._neigh4.neighs_as_indexes(index)
                d = filter(lambda n: n in direct_neighbours, neighbours)
                direct += len(d)
                diagonal += len(neighbours) - len(d)
                # add remaining neighbours to the queue
                queue.extend(neighbours) #mumumu

        # compute length in milimeters
        length = (math.sqrt(2)*diagonal + direct)*25.4/dpi # 1 inch = 25.4 mm
        self._print("%.1f mm Direct: %d, Diagonal: %d, Branches: %d" 
                % (length, direct, diagonal, tails-1)) # #branches == #tails-1
        data = {"delka_korenoveho_systemu": "%0.2f" % (length), 
                "vetveni": "%d" % (tails-2)}
        return data

    def determine_colors(self, img, skel, color_threshold = 128):
        self._print("Determining colors in skeleton.")
        white = (255, 255, 255)
        colors = [record[1] for record in self._colors]
        pixels = [0 if skel.getpixel(c) < color_threshold else 1 
                    for c in self._coords.coords()]
        groups, indexes = self._groups_init(pixels, self._neigh8)
        fg_indexes = filter(lambda i: pixels[i[0]] == 1, indexes)
        if len(fg_indexes) == 0:
            raise AnalyzerError("No skeleton found")
        elif len(fg_indexes) > 1:
            raise AnalyzerError("Too many skeletons (%d)." % (len(fg_indexes)))
        skel = fg_indexes[0] # select first (and the only) skeleton
        start = min(self._find_tails(skel)) # highest tail is the root begining

        # search the skeleton using depth first search
        # keep track of colors in last 2*w pixels, if colors in first w
        # pixels are different from colors of second group of w pixels than
        # the second group will be assigned new color type
        colcounter = 1 # starting color
        col = colcounter # curretnt color
        w = 1 # window will have size 2*w pixels
        
        # colors of the skeleton
        rgb = [img.getpixel(self._coords.index_to_coord(i)) 
                 for i in skel]
        #hsv = [colorsys.rgb_to_hsv(c[0], c[1], c[2]) for c in rgb]
        #yiq = [colorsys.rgb_to_yiq(c[0], c[1], c[2]) for c in rgb]

        # remember crossroads encountered during the DFS algorithm
        crossroads = []

        # start the DFS with the first pixel of the root, 
        # assign it the first color
        index = start
        stack = [index]
        c = img.getpixel(self._coords.index_to_coord(index))
        col = c if c in colors else white
        pixels[index] = col
        while True:
            # find all non-visited neighbours, these have value 1
            neighbours = self._filter_neighbours8(index, 1, pixels)
           
            # check whether this is a crossroad and store its index if so
            # one crossroad may be inserted multiple times, duplicates
            # will be filtered out later
            if len(neighbours) > 1:
                crossroads.append(index)
            if len(neighbours) > 0:
                # add first non-visited neighbour to the stack and color it
                # with current color
                index = neighbours[0]
                c = img.getpixel(self._coords.index_to_coord(index))
                if col != c:
                    col = c if c in colors else white
                    if col == white: # encountered undefined color
                        raise AnalyzerError("Error: Undefined color:", c, "at", self._coords.index_to_coord(index))
                    colcounter = colcounter + 1
                stack.append(index)
                pixels[index] = col

                # compute color difference from previous pixels
                # TODO:
            elif stack:
                # no more neighbours, extract the last pixel from the stack
                index = stack.pop() # get next pixel to examine
                col = pixels[index] # find its color
            else:
                # current pixel has no unvisited neighbours and the stack is empty
                # it means that all pixels have been examined
                break

        # on each crossroad, determine which color starts here and which continues
        for c in crossroads:
            branches = []
            neighbours = self._filter_neighbours8_by_condition(c, 
                    lambda n: pixels[n] != 0)
            for n in neighbours:
                length, next_color = self._follow_root_by_color(n, c, pixels[n], pixels, len(pixels)/100)
                branches.append((pixels[n], length, next_color))
            if len(neighbours) == 3:
                colors = map(lambda b: b[0], branches)
                if colors[0] == colors[1] == colors[2]:
                    # all branches have the same color, discard the shortest of them
                    lengths = map(lambda b: b[1], branches)
                    index, value = min(enumerate(lengths), key=operator.itemgetter(1))
                    if not value:
                        raise AnalyzerError("Branch is too short." % (len(neighbours)))
                    self._recolor_branch(neighbours[index], c, branches[index][2], pixels)

            else:
                raise AnalyzerError("There are %d branches leading from a crossroad." % (len(neighbours)))
            
        # TODO: sequences that are too short will be removed

        # TODO: color that enters the intersection can only continue in one direction
        data = {"vetveni2": "%d" % (len(crossroads))}
        pixels = [white if pixel == 0 else pixel for pixel in pixels]
        return pixels, data
        
    def _follow_root_by_color(self, current, previous, color, pixels, limit):
        length = 1
        while length < limit:
            # filter out previous pixel and pixels with different color
            neighbours = self._filter_neighbours8_by_color(current, 
                    color, pixels, previous)
            if len(neighbours) == 0:
                # end of the root
                neighs = self._filter_neighbours8_by_condition(current, 
                        lambda n: pixels[n] != 0 and pixels[n] != color)
                if len(neighs) == 0:
                    return length, None
                elif len(neighs) == 1:
                    return length, pixels[neighs[0]]
                else:
                    raise AnalyzerError("There are %d neighbours, expected 0 or 1 neighbours." % (len(neighs)))
            elif len(neighbours) == 1:
                # root continues
                length = length + 1
                previous = current
                current = neighbours[0]
            elif len(neighbours) == 2:
                # crossroad, recursively compute all branches and select the longest one
                best = (0, None)
                for n in neighbours:
                    r = self._follow_root_by_color(n, current, color, pixels, limit-length)
                    if r[0] > best[0]:
                        best = r
                length = length + best[0]
                next_color = best[1]
                return length, next_color
            else:
                # crossroad with 4 branches
                raise AnalyzerError("Crossroad with %d branches." % (len(neighbours)+1))
        raise AnalyzerError("Cycle in the root.")

    def _recolor_branch(self, current, previous, color, pixels):
        limit = len(pixels)/100
        while limit > 0:
            original = pixels[current]
            # filter out previous pixel and pixels with different color
            neighbours = self._filter_neighbours8_by_condition(current, 
                    lambda n: pixels[n] == pixels[current] and n != previous)
            pixels[current] = color
            if len(neighbours) == 0:
                # end of the root
                return
            elif len(neighbours) == 1:
                # root continues
                previous = current
                current = neighbours[0]
                limit = limit - 1
            else:
                # crossroad, recolor the pixel with the orginal color
                pixels[current] = original
                return
        raise AnalyzerError("Branch of the root is too long.")

    def _filter_neighbours8(self, index, value, pixels):
        """Filter neighbours of pixel with index 'index' that have value
        'value'. Returns list of indexes of neighbouring pixels."""
        return self._filter_neighbours8_by_condition(index,
            lambda n: pixels[n] == value)
    
    def _filter_neighbours8_by_color(self, index, color, pixels, previous = None):
        return self._filter_neighbours8_by_condition(index, 
                    lambda n: pixels[n] == color and n != previous)

    
    def _filter_neighbours8_by_condition(self, index, condition):
        all_neighbours = self._neigh8.neighs_as_indexes(index)
        neighbours = filter(condition, all_neighbours)
        return neighbours

    def _find_tails(self, indexes):
        """Find tails of given skeleton. Indexes are indexes of pixels of 
        this skeleton. Tail is a pixel that has only one neighbour.
        Returns list of tails."""
        pixels = [0] * self._coords.total()
        for i in indexes:
            pixels[i] = 1
        tails = []
        queue = deque([indexes[0]]) # select first pixel of the skeleton
        while len(queue) > 0:
            # get next index
            index = queue.popleft()
            if pixels[index] == 1:
                pixels[index] = 2 # 0 == bg, 1 == fg, 2 == visited fg
                # get neighbours of selected index
                all_neighbours = self._neigh8.neighs_as_indexes(index)
                # filter out those neighbours that have already been visited
                # or that are background
                neighbours = filter(lambda n: pixels[n] == 1, all_neighbours)
                if (len(neighbours) == 0 or
                   (len(neighbours) == 1 and index == indexes[0])):
                   # if there are no neighbours that havent been visited
                   # yet or if the first pixel has exactly one neighbour
                   # then the end of the tail was encountered
                   tails.append(index)
                queue.extend(neighbours)
        return tails
                

    def _groups_init(self, pixels, neigh):
        """Assign all pixels into group based on same bg/fg status."""
        self._print("Splitting pixels into groups.")
        # each pixel will be assigned to one group
        groups = [0] * self._coords.total()
        # list of lists of pixels for each group
        indexes = []
        value = 1
        for i in self._coords.indexes():
            if groups[i] == 0:
                # found pixel that does not belong to any group yet, 
                # perform flood fill
                indexes.append(self._flood(neigh, groups, pixels, i, value))
                value = value + 1
        self._print("Found %d groups." % len(indexes))
        return groups, indexes
    
    def _groups_prune(self, pixels, groups, indexes, neighs, group_threshold):
        """Assume that small groups are mistakes. Switch pixels of groups
        whose size is smaler than threshold."""
        self._print("Prunning groups.")
        pruned = 0
        for group in indexes:
            if len(group) <= group_threshold:
                for i in group:
                    # change bg/fg pixel
                    pixels[i] = 0 if pixels[i] == 1 else 1
                pruned += 1
        self._print("Pruned %d groups." % (pruned))
        return self._groups_init(pixels, neighs)
        
    def _flood(self, neighs, groups, pixels, index, value):
        orig = pixels[index] # background or foreground
        indexes = []
        queue = deque([index])
        while len(queue) > 0:
            # get next index
            index = queue.popleft()
            if groups[index] != value:
                # add selected neighbour to current group
                groups[index] = value
                indexes.append(index)
                # get neighbours of selected index
                all_neighbours = neighs.neighs_as_indexes(index)
                # filter out those neighbours that have already been selected
                # or that are marked as background
                neighbours = [n for n in all_neighbours 
                                if groups[n] != value and pixels[n] == orig]
                # add remaining neighbours to the queue
                queue.extend(neighbours) #mumumu
        self._print("Filled %d pixels." % (len(indexes)))
        return indexes

    def save_pixels(self, filename, pixels, version = "BW"):
        if not pixels:
            return
        if version == "BW": # black and white picture
            img = Image.new("L", self._coords.size())
            for i in self._coords.indexes():
                col = 0 if pixels[i] == 0 else 255
                xy = self._coords.index_to_coord(i)
                img.putpixel(xy, col)
        elif version == "GS": # grayscale picture
            img = Image.new("L", self._coords.size())
            minimum = min(pixels)
            maximum = max(pixels)
            distance = maximum - minimum
            for i in self._coords.indexes():
                col = int(255*pixels[i]/distance)
                xy = self._coords.index_to_coord(i)
                img.putpixel(xy, col)
        elif version == "RGB": # RGB picture
            img = Image.new("RGB", self._coords.size())
            for i in self._coords.indexes():
                col = pixels[i]
                xy = self._coords.index_to_coord(i)
                img.putpixel(xy, col)
        img.save(filename)
    
    def _print(self, text):
        if self._verbose: print text
