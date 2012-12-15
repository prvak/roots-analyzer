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

class Crossroad:
    def __init__(self, index, branch):
        self._index = index
        self._branches = [branch]
        branch.end(self)

    def append(self, branch):
        self._branches.append(branch)

    def get_index(self):
        return self._index

    def get_branches(self, branch = None):
        # get other branches than branch
        return filter(lambda b: b != branch, self._branches)
    
    def get_branch(self, index):
        return self._branches[index]

class Branch:
    def __init__(self, crossroad):
        self._start = crossroad
        self._end = None
        self._indexes = []

    def end(self, crossroad):
        self._end = crossroad
        self._indexes.pop()

    def append(self, index):
        self._indexes.append(index)

    def get_crossroad(self, crossroad = None):
        # return the crossroad opposite to given crossroad
        return self._end if crossroad == self._start else self._start

    def get_first_index(self, crossroad = None):
        if crossroad == self._start:
            return self._indexes[0] if self._indexes else self._end.get_index()
        else:
            return self._indexes[-1] if self._indexes else self._start.get_index()

    def get_last_index(self):
        return self._indexes[-1]

    def get_indexes(self, crossroad = None):
        # get indexes starting from given crossroad
        return iter(self._indexes) if crossroad == self._start else reversed(self._indexes)


class Analyzer:
    def __init__(self, img, colors = None, verbose = False):
        self._verbose = verbose
        self._coords = Coordinates(img.size)
        self._neigh4 = Neighbours(self._coords, False)
        self._neigh8 = Neighbours(self._coords, True)
        self._colors = colors
    
    def filter_background(self, img, 
            color_threshold = 180, group_threshold = 5):
        # light colors will be marked as background
        img = img.getdata()
        pixels = [0 if c > color_threshold else 1 for c in img]
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
        img = img.getdata()
        pixels = [1 if c in colors else 0 for c in img]
        # assign each pixel a group number, group is a continuous section
        # of background or foreground pixels
        groups, indexes = self._groups_init(pixels, self._neigh4)
        while min((len(g) for g in indexes)) <= group_threshold:
            groups, indexes = self._groups_prune(pixels, groups, indexes, 
                    self._neigh4, group_threshold)

        return pixels, groups, indexes

    def _measure_colors(self, branch, crossroad, pixels, dpi, record, direct, diagonal):
        """Measures total length of the skeleton in the image 'img'.
        
        Returns various statistics of the skeleton. Lengths are in milimeters. """
        data = []

        previous = crossroad.get_index() if crossroad else None
        if not record:
            record = defaultdict(int)
            if previous:
                record[self._get_color_name(pixels[previous])] += 1
            else:
                record[self._get_color_name(None)] += 1
        
            
        indexes = []
        indexes.extend(branch.get_indexes(crossroad))
        if branch.get_crossroad(crossroad):
            indexes.append(branch.get_crossroad(crossroad).get_index())

        for n in indexes:
            if previous:
                if self._is_direct_neighbour(n, previous):
                    direct += 1
                else:
                    diagonal += 1
                if pixels[n] != pixels[previous] and n != indexes[0]: # ignore color change immediately after crossroad
                    # color changed
                    record["barva"] = self._get_color_name(pixels[previous])
                    record["delka"] = self._get_skeleton_length(direct, diagonal, dpi)
                    record[self._get_color_name(pixels[n])] += 1 
                    data.append(record)
                    record = defaultdict(int)
                    record[self._get_color_name(pixels[previous])] += 1 
                    direct = 0
                    diagonal = 0
            previous = n
        else:
            # branch over
            c = branch.get_crossroad(crossroad)
            if c: 
                # continue with the branch that has same color as the crossroad
                # there should be exactly one
                same = [] # branches that have the same color as the crossroad
                different = [] # branches that have different color than the crossroad
                for b in c.get_branches(branch):
                    col = pixels[b.get_first_index(c)]
                    if col == pixels[n]:
                        same.append((b, col))
                    else:
                        different.append((b, col))
                
                if len(same) + len(different) > 2:
                    # only three way crossroads are allowed
                    raise AnalyzerError("Four way crossroad at %s." % (self._coords.index_to_coord(n)))
                if len(same) == 0:
                    # no branch with the same color found
                    raise AnalyzerError("No branch continues with color '%s' at %s." % (self._get_color_name(pixels[n]), self._coords.index_to_coord(n)))
                if len(same) > 1:
                    # too many branches with the same color found
                    raise AnalyzerError("Too many branches continues with color '%s' at %s." % (self._get_color_name(pixels[n]), self._coords.index_to_coord(n)))
                if len(different) == 0:
                    # we have arrived from wrong direction
                    raise AnalyzerError("All branches continue with color '%s' at %s." % (self._get_color_name(pixels[n]), self._coords.index_to_coord(n)))
                if len(different) > 1:
                    # we have arrived from wrong direction
                    raise AnalyzerError("Too many branches with different color than '%s' at %s." % (self._get_color_name(pixels[n]), self._coords.index_to_coord(n)))
                else:
                    record[self._get_color_name(different[0][1])] += 1 
                    data.extend(self._measure_colors(same[0][0], c, pixels, dpi, record, direct, diagonal))
                    data.extend(self._measure_colors(different[0][0], c, pixels, dpi, None, 0, 0))
            else:
                # end of branch without crossroad
                record["barva"] = self._get_color_name(pixels[previous])
                record["delka"] = self._get_skeleton_length(direct, diagonal, dpi)
                record[self._get_color_name(None)] += 1 
                data.append(record)
                record = defaultdict(int)
                direct = 0
                diagonal = 0
        return data                    
    
    def measure_skeleton(self, img, skel, dpi):
        img = img.getdata()
        skel = skel.getdata()
        self._print("Determining colors in skeleton.")
        white = (255, 255, 255)
        colors = [record[1] for record in self._colors]
        pixels = [0 if c < 128 else 1 
                    for c in skel]
        groups, indexes = self._groups_init(pixels, self._neigh8)
        fg_indexes = filter(lambda i: pixels[i[0]] == 1, indexes)
        if len(fg_indexes) == 0:
            raise AnalyzerError("No skeleton found")
        elif len(fg_indexes) > 1:
            raise AnalyzerError("Too many skeletons (%d)." % (len(fg_indexes)))
        skel = fg_indexes[0] # select first (and the only) skeleton
        tails = self._find_tails(skel)
        coloredpixels = [white if pixels[i] == 0 else img[i]
                for i in self._coords.indexes()]
        start = self._find_root_begining(tails, coloredpixels)

        # find crossroads and branches
        crossroads = []
        branches = []
        index = start
        pixels[index] = 2
        branch = Branch(None)
        branch.append(index)
        branches.append(branch)
        queue = deque([branch])
        while len(queue) > 0:
            # get next index
            branch = queue.popleft()
            index = branch.get_last_index()
            if not coloredpixels[index] in colors:
                raise AnalyzerError("Unknown color %s at %s" % (coloredpixels[index], self._coords.index_to_coord(index)))
            if pixels[index] == 2: # already selected
                neighbours = self._filter_neighbours8_by_color(index, 1, pixels)
                l = len(neighbours)
                if l == 0:
                    pass
                elif l == 1:
                    n = neighbours[0]
                    pixels[n] = 2
                    branch.append(n)
                    queue.append(branch)
                else:
                    crossroad = Crossroad(index, branch)
                    for n in neighbours:
                        pixels[n] = 2
                        branch = Branch(crossroad)
                        branch.append(n)
                        branches.append(branch)
                        crossroad.append(branch)
                        queue.append(branch)
                    crossroads.append(crossroad)

        # on each crossroad, determine which color starts here and which continues
        pixels = coloredpixels
    
        for c in crossroads:
            n = c.get_index()
            nc = pixels[n]
            colordata = []
            for b in c.get_branches():
                length, next_color = self._follow_root_by_color(b, c, nc, pixels)
                colordata.append((b, nc, length, next_color))
            if len(colordata) == 3:
                colors = map(lambda b: b[1], colordata)
                if colors[0] == colors[1] == colors[2]:
                    # all branches have the same color, recolor the shortest of them
                    lengths = map(lambda b: b[2], colordata)
                    index, value = min(enumerate(lengths), key=operator.itemgetter(1))
                    if value:
                        # recolor only branches with at least one pixel
                        self._recolor_branch(colordata[index][0], c, nc, colordata[index][3], pixels)
            else:
                raise AnalyzerError("There are %d branches leading from a crossroad." % (len(neighbours)))

        # this is a begining of the root, mark the tail
        data = self._measure_colors(branches[0], None, pixels, dpi, None, 0, 0)
        data.reverse()
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
        if best == len(pixels):
            for t in tails:
                if pixels[t] == blue and t < best:
                    best = t
        # if neither blue nor red tail exists, find the highest tail
        if best == len(pixels):
            for t in tails:
                if t < best:
                    best = t
        if best == len(pixels):
            raise AnalyzerError("No root begining found.")
        return best

    def _follow_root_by_color(self, branch, crossroad, color, pixels):
        # follow pixels of the root on given branch starting from given crossroad
        length = 0
        for n in branch.get_indexes(crossroad):
            if pixels[n] == color:
                # branch continues with the same color
                length += 1
            else:
                # branch continues but with a different color
                return (length, pixels[n])
        else:
            # end of a section, continue recursively from next crossroad
            nextCrossroad = branch.get_crossroad(crossroad)
            if nextCrossroad:
                n = nextCrossroad.get_index()
                if pixels[n] != color:
                    # crossroad has different color
                    return (length, pixels[n])
                longest = (-1, None)
                for b in nextCrossroad.get_branches(branch):
                    (l, c) = self._follow_root_by_color(b, nextCrossroad, color, pixels)
                    if longest[0] < l:
                        longest = (l, c)
                # return length of the longest section
                return (length + longest[0], longest[1])
            else:
                # end of the root
                return (length, None)

    def _recolor_branch(self, branch, crossroad, color, newColor, pixels):
        for n in branch.get_indexes(crossroad):
            if not newColor:
                raise AnalyzerError("Recoloring with an invalid color at %s." % (str(self._coords.index_to_coord(n))))
            if pixels[n] == color:
                # branch continues with the same color
                pixels[n] = newColor
            else:
                # branch continues but with a different color
                break
   
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
            img.putdata(pixels)
        img.save(filename)
    
    def _print(self, text):
        if self._verbose: print text

def load_colors():
    colors = []
    with open("barvy.cfg") as f:
        f.readline() # first line contains headers
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            (name, color, others) = line.split(";", 2)
            color = ImageColor.getrgb("#"+color[2:]) # color must be in form '#rrggbb'
            colors.append((name, color))
    return colors
