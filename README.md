# palettizer
Palettizer is a simple tool to reduce images' color space to a given palette. 

Requirements:
* python 3
* scikit-image
* scikit-learn

Usage:

```
python setup.py install
python palettizer/main.py <input image path> <comma-separated paths to palette files> <output image path> [<max number of colors, 0 is infinite>]
```

Example:

```
python palettizer/main.py testimage6.png arton-palette.json,mtnblack-palette.json,mtn94-palette.json output.png 30
```