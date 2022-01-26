# palettizer
Palettizer is a simple tool to reduce images' color space to a given palette. 

Requirements:
* python 3
* scikit-image
* scikit-learn

Usage:

```
pip install .
python palettizer/main.py <input image path> <comma-separated paths to palette files> <output image path> [<max number of colors, 0 is infinite>]
```

Example:

```
python palettizer/main.py palettizer/resources/testimage2.png palettizer/resources/arton-palette.json,palettizer/resources/mtnblack-palette.json,palettizer/resources/mtn94-palette.json output.png 30
```

Run tests:
```
pip install .[test]
pytest
```