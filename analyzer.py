import math
from collections import deque
import colorsys # for rgb_to_hsv, rgb_to_yiq
from PIL import Image, ImageColor
import operator
from collections import defaultdict

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
        self._colors = None
    
    def set_colors(self, colors):
        self._colors = colors

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

    def _measure_colors(self, index, pixels, dpi, previous = None, direct = 0, diagonal = 0):
        """Measures total length of the skeleton in the image 'img'.
        
        Returns various statistics of the skeleton. Lengths are in milimeters. """
        data = []
        zaznam = defaultdict(int)
        if direct + diagonal == 0:
            # this is a begining of the root, mark the tail
            branch_name = self._get_color_name(None)
            zaznam[branch_name] += 1 # this works thanks to defaultdict 
        while True:
            # get next index
            neighbours = self._filter_neighbours8_by_condition(index, 
                    lambda n: pixels[n] != 0 and n != previous)
            l = len(neighbours)
            if l == 0:
                # end of a branch
                color_name = self._get_color_name(pixels[index])
                zaznam["barva"] = color_name
                length = self._get_skeleton_length(direct, diagonal, dpi)
                zaznam["delka"] = length
                branch_name = self._get_color_name(None)
                zaznam[branch_name] += 1 # this works thanks to defaultdict 
                data.append(zaznam)
                return data
            elif l == 1:
                # branch continues
                n = neighbours[0]
                if pixels[n] != pixels[index]:
                    # color changed
                    color_name = self._get_color_name(pixels[index])
                    zaznam["barva"] = color_name
                    length = self._get_skeleton_length(direct, diagonal, dpi)
                    zaznam["delka"] = length
                    branch_name = self._get_color_name(pixels[n])
                    zaznam[branch_name] += 1 # this works thanks to defaultdict 
                    d = self._is_direct_neighbour(index, n)
                    data.extend(self._measure_colors(n, pixels, dpi, index, 1 if d else 0, 0 if d else 1))
                    data.append(zaznam)
                    return data
                else:
                    # color continues
                    if self._is_direct_neighbour(index, neighbours[0]):
                        direct += 1
                    else:
                        diagonal += 1
                    previous = index
                    index = n
            elif l == 2:
                # crossroad
                c = pixels[index]
                c1 = pixels[neighbours[0]]
                c2 = pixels[neighbours[1]]
                if c == c1 and c != c2:
                    n1 = neighbours[1]
                    n2 = neighbours[0]
                elif c != c1 and c == c2:
                    n1 = neighbours[0]
                    n2 = neighbours[1]
                elif c == c1 and c == c2:
                    raise AnalyzerError("Both neighbours are of the same color.")
                else: #c != c1 and c != c2:
                    raise AnalyzerError("Both neighbours are of different colors.")
                # call recursively on the branch
                d = self._is_direct_neighbour(index, n1)
                branch_name = self._get_color_name(pixels[n1])
                zaznam[branch_name] += 1 # this works thanks to defaultdict 
                data.extend(self._measure_colors(n1, pixels, dpi, index, 1 if d else 0, 0 if d else 1))
                # continue with the same color
                if self._is_direct_neighbour(index, n2):
                    direct += 1
                else:
                    diagonal += 1
                previous = index
                index = n2
            else:
                raise AnalyzerError("There are %d branches, allowed maximum is 2" % (l))
        return data
    
    def measure_skeleton(self, img, skel, dpi):
        self._print("Determining colors in skeleton.")
        white = (255, 255, 255)
        colors = [record[1] for record in self._colors]
        pixels = [0 if skel.getpixel(c) < 128 else 1 
                    for c in self._coords.coords()]
        groups, indexes = self._groups_init(pixels, self._neigh8)
        fg_indexes = filter(lambda i: pixels[i[0]] == 1, indexes)
        if len(fg_indexes) == 0:
            raise AnalyzerError("No skeleton found")
        elif len(fg_indexes) > 1:
            raise AnalyzerError("Too many skeletons (%d)." % (len(fg_indexes)))
        skel = fg_indexes[0] # select first (and the only) skeleton
        tails = self._find_tails(skel)
        tails.sort()
        start = tails[0]

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


        start = self._find_root_begining(tails, pixels)
        data = self._measure_colors(start, pixels, dpi)
        pixels = [white if pixel == 0 else pixel for pixel in pixels]
        return pixels, data

    def _find_root_begining(self, tails, pixels):
        for n, c in self._colors:
            if n == "modra":
                blue = c
            if n == "cervena":
                red = c
        
        # find the heighest blue tail
        best = len(pixels)
        for t in tails:
            if pixels[t] == blue and t < best:
                best = t
        # if no blue tail exists, find highest red tail
        if best < 0:
            for t in tails:
                if pixels[t] == blue and t < best:
                    best = t
        # if neither blue nor red tail exists, find the highest tail
        if best < 0:
            for t in tails:
                if t < best:
                    best = t
        return best

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
   
    def _get_skeleton_length(self, direct, diagonal, dpi):
        length = (math.sqrt(2)*diagonal + direct)*25.4/dpi # 1 inch = 25.4 mm
        return length
       
    def _is_direct_neighbour(self, index, neighbour):
        direct_neighbours = self._neigh4.neighs_as_indexes(index)
        return neighbour in direct_neighbours

    def _get_color_name(self, color):
        for c in enumerate(self._colors):
            if c[1][1] == color:
                return c[1][0]
        return "bila"
        #raise AnalyzerError("Unknown color (%d, %d, %d)" % (color))

    def _get_branch_name(self, color1, color2):
        name1 = self._get_color_name(color1)
        name2 = self._get_color_name(color2)
        return "%s_%s" % (name1, name2)

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
