#!/usr/bin/python
import argparse
import os

from PIL import Image, ImageColor
from analyzer import Analyzer, AnalyzerError, load_colors

errors = 0

def measure_skeleton_for_image(source, skeleton, target, dpi, colors, verbose = True):
    """Measure skeleton stored in a bitmap image in file 'source'.
    
    Image must be black and white. Background must be black, skeleton must
    be white. All pixels of the skeleton must be connected together into a
    single skeleton.
    
    Returns list containing filename, length of the skeleton and number 
    of branches. Length is in milimeters."""
    global errors
    print "%s -> %s" % (skeleton, target)
    img = Image.open(source)
    skel = Image.open(skeleton)
    if img.size == skel.size:
        data = []
        try:
            analyzer = Analyzer(img, colors, verbose)
            pixels, data = analyzer.measure_skeleton(img, skel, dpi)
            analyzer.save_pixels(target, pixels, "RGB")
        except AnalyzerError as e:
            print "Error: %s: %s" % (skeleton, str(e))
            errors = errors + 1
        return data
    else:
        print "Error: Images '%s' and '%s' do not have the same sizes!" % (source, skeleton)
        errors = errors + 1
        return {}

def measure_skeleton_for_directory(source, skeleton, target, dpi, colors, verbose = False):
    """Measure skeletons stored in a bitmap images in directory 'source'.
    
    Images must be black and white. Background must be black, skeleton must
    be white. All pixels of the skeleton must be connected together into a
    single skeleton.
    
    Only those images are measured whose filename ends with .skel.png.
    Other files are ignored.

    Returns list of results. One result contains filename, length of the 
    skeleton and number of branches. Filename is without the skel.png 
    extension, length is in milimeters."""
    # append folder separator if it is not present in folder names
    source_dir = source + os.path.sep if source[-1] != os.path.sep else source
    skeleton_dir = skeleton + os.path.sep if skeleton[-1] != os.path.sep else skeleton
    target_dir = target + os.path.sep if target[-1] != os.path.sep else target

    # make target directry if it does not exist
    if not os.path.exists(target_dir):
        os.path.makedirs(target_dir)

    # get list of files in the source directory
    try: 
        filenames = []
        filenames = os.listdir(source)
    except:
        print "Falied to list directory '%s'" % (source)
        return {}

    measurements = []
    filenames.sort()
    for filename in filenames:
        base = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        # see if the source file is in supported format and if so, analyze it
        source_fn = filename
        source_path = source_dir + source_fn
        skeleton_path = skeleton_dir + base + ".skel.png"
        target_path = target_dir + base + ".cols.png"
        if (os.path.isfile(source_path)
                and ext in [".bmp", ".png", ".jpg", ".jpeg"]
                and not source_fn.endswith(".root.png")
                and not source_fn.endswith(".skel.png")
                and not source_fn.endswith(".cols.png")
                and os.path.isfile(skeleton_path)):
            # encountered image file that has a coresponding skeleton file
            data = measure_skeleton_for_image(source_path, skeleton_path, 
                    target_path, dpi, colors, verbose)
            name = os.path.split(source_path)[1] # remove folder name
            name = os.path.splitext(name)[0] # remove format extension
            name = os.path.splitext(name)[0] # remove skel extension
            for d in data:
                d["jmeno"] = name
            measurements = data + measurements # files will be ordered alphabetically in the csv
    return measurements

def save_skeleton_measurements(data, target):
    """Saves result of the measurement into the target file.
    
    Format of the file is csv. Each element in the data will be saved
    into one line. Elements of the data will be separated by colons.
    The first line contains header."""
    data.reverse()
    errors = 0 # number of errors
    with open(target, 'w') as f:
        # this specifies which columns will be written out and in which order
        leading_headers = [
                "jmeno",
                "barva",
                "delka"
                ]
        other_headers = [
                "%s" % (c[0]) for c in colors
                ]
        other_headers.append("bila")
        headers = leading_headers + other_headers
        f.write(";".join(headers)+"\n")
        #print data
        for row in data:
            records = []
            for column in headers:
                record = row[column] if row.has_key(column) else 0
                if type(record) == int:
                    record = "%d" % (record)
                elif type(record) == float:
                    record = "%0.4f" % (record)
                elif type(record) == str:
                    pass
                else:
                    print "Error: Unexpected type '%s' of value '%s'. Allowed are int, float and str." % (type(record), record)
                    record = str(record)
                records.append(record)
            f.write(";".join(records)+"\n")


if __name__=="__main__":
    # parse commandline arguments
    parser = argparse.ArgumentParser(
            description="Measure length of a skeleton in given image or of all images in given directory.")
    parser.add_argument("images", type=str, help="source directory or file with original images")
    parser.add_argument("skeletons", type=str, help="source directory or file with skeletons")
    parser.add_argument("target", type=str, help="target directory or file where colored skeletons will be saved")
    parser.add_argument("stats", type=str, help="file where measurements will be saved")
    arguments = parser.parse_args()
    images = arguments.images
    skeletons = arguments.skeletons
    target = arguments.target
    stats = arguments.stats
    dpi = 300

    # run the script
    print "Running..."
    colors = load_colors()
    if os.path.isdir(images):
        data = measure_skeleton_for_directory(images, skeletons, target, dpi, colors)
        save_skeleton_measurements(data, stats)
    else:
        data = measure_skeleton_for_image(images, skeletons, target, dpi, colors)
        save_skeleton_measurements(data, stats)
    if errors > 0:
        print "Warning: There were %d errors in skeleton examination." % (errors)
    print "Finished."




