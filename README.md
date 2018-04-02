Requirements
============

- [`python`](https://www.python.org/)
- [`pygame`](https://www.pygame.org/) (needed only for `points.py` and `colors.py`)
- [`fiji`](https://fiji.sc/) (needed only for `skeleton.imj`)


Usage
=====

points.py
---------

Tool for choosing edge points of the root.

Launch with command:

  `python points.py DIRECTORY`

where `DIRECTORY` is a directory containing images with roots.
Root images will be displayed one by one and user will have to manually select edge points.
Selected points will be saved in a file called `DIRECTORY.csv`. If the file already exists
its content will be loaded. If it does not exist it will be created.


colors.py
---------

Tool for redrawing roots with solid colors so that it is easier to analyze them.

Launch with command:

  `python colors.py DIRECTORY`


analyze-background.py
---------------------

Script for transfering colorized root images to black and white images where root is white and
background is black.

Launch with command:

  `python analyze-background.py COLORIZED_ROOTS_DIR BLACK_AND_WHITE_DIR`

Images from directory `COLORIZED_ROOTS_DIR` will be transformed to black and white versions and saved
in directory `BLACK_AND_WHITE_DIR` with extension `.root.png`.


skeleton.ijm
------------

This is a macro for [`fiji`](https://fiji.sc/)  program. It computes a root skeleton from a black
and white image of a root.

Launch with command:

  `fiji -batch skeleton.ijm BLACK_AND_WHITE_DIR:SKELETON_DIR`

Please notice that the directory names are separated by a colon `:`.

The macro expect the directory `BLACK_AND_WHITE_DIR` to contain black and white images of roots
with extensions `.root.png`. It ignores all other files. The root in the image is expected to
be white, the background is expected to be black. Computed skeletons will be saved into
directory `SKELETON_DIR` with extensions `.skel.png`.


analyze-skeleton.py
-------------------

Script for computing various parameters of root skeletons.

Launch with command:

  `python analyze-skeleton.py COLORIZED_ROOTS_DIR SKELETON_DIR COLORIZED_SKELETONS_DIR results.csv`

The `COLORIZED_ROOTS_DIR` directory should contain original colorized roots, the same that were
used in the `analyze-background.py` script. These images are used to produce colorized version
of skeleton.

The `SKELETON_DIR` should contain images of skeletons. Skeleton must be in a form of a black
and white image where the skeleton in the image is white and one pixel thick and the background
is black. Images with skeletons are expected to have extension `.skel.png`.

Computed parameters will be stored in `results.csv`. If the file already exists it will be
overwritten. Colorized versions of skeletons will be stored in `COLORIZED_SKELETON_DIR`.


analyze.sh
----------

Skript that launches `analyze-background.py`, `skeleton.ijm` and `analyze-skeleton.py`
one after another.

Launch with command:
  `bash analyze.sh DIRECTORY PREFIX`
or:
  `bash analyze.sh COLORIZED_ROOTS PREFIX COMMAND_NUMBER`

Directory `PREFIX` is expected to have several subdirectories, all starting with prefix
`PREFIX`.
:
 - colored-roots: Zde musí být obrázky kořenů.
 - white-roots: Zde budou vygenerovány černobílé obrázky kořenů.
 - skeletons: Zde budou vygenerovány černobílé obrázky koster.
 - colored-skeletons: Zde budou vygenerovány barevné obrázky koster a csv soubor
     s výsledky.

Parameter `COMMAND_NUMBER` is optional. It must be a number 1, 2 or 3. If present the script will
run only the selected command (1 - `analyze-background.py`, 2 - `skeleton.ijm`,
3 - `analyze-skeleton.py`).

