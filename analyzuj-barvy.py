#!/usr/bin/python
import argparse
import os

from PIL import Image

from analyzer import Analyzer

def colors_for_image(image, skeleton, target, verbose = True):
    print "%s -> %s" % (skeleton, target)
    img = Image.open(image)
    skel = Image.open(skeleton)
    if img.size == skel.size:
        analyzer = Analyzer(img, verbose)
        analyzer.determine_colors(img, skel)
    else:
        print "Error: Images '%s' and '%s' do not have the same size!" % (image, skeleton)

def colors_for_directory(source, dpi, verbose = False):
    # append folder separator if it is not present in source
    source_dir = source + os.path.sep if source[-1] != os.path.sep else source

    try: 
        filenames = []
        filenames = os.listdir(source)
    except:
        print "Falied to list directory '%s'" % (source)
        return []

    measurements = []
    filenames.sort()
    for filename in filenames:
        # insert ".root" before extension of the target filename
        source_fn = filename
        # see if the source file is in supported format and if so, analyze it
        source_path = source_dir + source_fn
        if os.path.isfile(source_path) and source_fn.endswith(".skel.png"):
            # encountered skeleton file
            data = colors_for_image(source_path, dpi, verbose)
            name = os.path.split(source_path)[1] # remove folder name
            name = os.path.splitext(name)[0] # remove format extension
            name = os.path.splitext(name)[0] # remove skel extension
            measurements.append([name] + data)
    return measurements

if __name__=="__main__":
    # parse commandline arguments
    parser = argparse.ArgumentParser(
            description="Measure length of a skeleton in given image or of all images in given directory.")
    parser.add_argument("images", type=str, help="source directory or file with original images")
    parser.add_argument("skeletons", type=str, help="source directory or file with skeletons")
    parser.add_argument("target", type=str, help="target directory or file")
    arguments = parser.parse_args()
    images = arguments.images
    skeletons = arguments.skeletons
    target = arguments.target

    # run the script
    print "Running..."
    if os.path.isdir(images) and os.path.isdir(skeletons):
        # determine colors for all skeletons in directory 'skeletons'
        colors_for_directory(images, skeletons, target)
    else:
        # determine colors for given skeleton
        colors_for_image(images, skeletons, target)
    print "Finished."





