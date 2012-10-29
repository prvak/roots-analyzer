#!/usr/bin/python
import argparse
import os

from PIL import Image
from analyzer import Analyzer, AnalyzerError, load_colors

errors = 0

def clear_background_for_image(source, target, colors, verbose = True):
    """Clear background of source image.
    
    Result is a black and white image in png format. White color 
    coresponds to foreground pixels, black color to background pixels."""
    print "%s -> %s" % (source, target)
    img = Image.open(source)
    gray = img.convert("L")
    # compute mean color
    total = (gray.size[0] * gray.size[1])
    mean = sum((col * n for col, n in gray.getcolors())) / total
    try:
        analyzer = Analyzer(img, colors, verbose)
        pixels, groups, indexes = analyzer.filter_background(gray, 
                color_threshold = mean - 30) # 
        analyzer.save_pixels(target, pixels)
    except AnalyzerError as e:
        print "Error: %s: %s" % (source, str(e))
        errors = errors + 1


def clear_background_for_image2(source, target, colors, verbose = True):
    """Clear background of source image.
    
    Result is a black and white image in png format. White color 
    coresponds to foreground pixels, black color to background pixels."""
    global errors
    print "%s -> %s" % (source, target)
    img = Image.open(source)
    # compute mean color
    try:
        analyzer = Analyzer(img, colors, verbose)
        pixels, groups, indexes = analyzer.filter_background2(img, 20) 
        analyzer.save_pixels(target, pixels)
    except AnalyzerError as e:
        print "Error: %s: %s" % (source, str(e))
        errors = errors + 1

def clear_background_for_directory(source, target, version, colors, verbose = False):
    """Clear background of all images in the source directory.
    
    Result is a black and white image in png format. White color 
    coresponds to foreground pixels, black color to background pixels.
    One result file will be created in target directory for each image
    in the source directory. Base name of the source file will be appended
    with .skel.png extension."""
    # append folder separator if it is not present in source
    source_dir = source + os.path.sep if source[-1] != os.path.sep else source
    # append folder separator if it is not present in target
    target_dir = target + os.path.sep if target[-1] != os.path.sep else target

    try: 
        filenames = []
        filenames = os.listdir(source)
    except:
        print "Error: Falied to list directory '%s'" % (source)
        return

    filenames.sort()
    for filename in filenames:
        # create target directory if it does not exist
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        # insert ".root" before extension of the target filename
        target_fn = os.path.splitext(filename)[0] + ".root.png"
        source_fn = filename

        # see if the source file is in supported format and if so, analyze it
        source_path = source_dir + source_fn
        if (os.path.isfile(source_path) 
                and not source_fn.endswith(".root.png")
                and not source_fn.endswith(".cols.png")
                and not source_fn.endswith(".skel.png")):
            # encountered a file
            root, ext = os.path.splitext(source_fn)
            ext = ext.lower()
            if ext in (".bmp", ".png", ".jpg", ".jpeg"):
                # encountered image file
                if version == 1:
                    clear_background_for_image(source_path, 
                            target_dir + target_fn, colors, verbose)
                elif version == 2:
                    clear_background_for_image2(source_path, 
                            target_dir + target_fn, colors, verbose)
                else:
                    print "Unknown version '%d'." % (version)

if __name__=="__main__":
    # parse commandline arguments
    parser = argparse.ArgumentParser(
            description="Create black and white version of given image or of all images in given directory.")
            
    parser.add_argument("source", type=str, help="source directory or file")
    parser.add_argument("target", type=str, help="target directory or file")
    arguments = parser.parse_args()
    source = arguments.source
    target = arguments.target

    # run the script
    print "Running..."
    colors = load_colors()
    if os.path.isdir(source):
        # source is a directory, clear background of all images in that
        # directory and save each result to separate file in target directory
        clear_background_for_directory(source, target, 2, colors)
    else:
        # source is a file, clear background of that image
        clear_background_for_image2(source, target, colors)
    if errors > 0:
        print "Warning: There were %d errors in skeleton examination." % (errors)
    print "Finished."



