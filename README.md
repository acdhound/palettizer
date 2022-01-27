# Palettizer
Palettizer is a simple tool designed to reduce images' color space to a given palette. 

## Requirements
* python 3
* pip

## Usage

First install all required packages. Run from the project root directory:

```shell
pip install .
```

Then run Palettizer by the following command:

```
# Unix
python palettizer/main.py <input image path> \
    <comma-separated paths to palette files> \
    <output image path> \
    [<max number of colors, 0 is infinite>]
```
```
REM Windows
python palettizer\main.py <input image path> ^
    <palette files> ^
    <output image path> ^
    [<max number of colors>]
```

Parameters:

* **input image path** is the path to any image file (.jpg, .png etc) you want to convert to a given color palette
* **palette files** are comma-separated paths to JSON files containing color RGB codes and names (example - _palette1.json,palette2.json,palette2.json_).
There are some pre-defined palettes in _palettizer/resources_ folder you can use.
If you'd like to create your own palette files they should have the following structure:
```json
{
  "palette": [
    {"color":"ff0000","name":"Color 1","vendor":"ABC"},
    {"color":"00ff00","name":"Color 2","vendor":"ABC"},
    {"color":"0000ff","name":"Color 3","vendor":"ABC"}
  ]
}
```
* **output image path** is the path to the file to save the converted image
* **max number of colors** is an optional parameter denoting the maximum number of colors to use from the palette.
  If you set it to 0, there will be no limit in colors.

See the example command below:

```shell
# Unix
python palettizer/main.py palettizer/resources/bliss.jpg \
    palettizer/resources/mtnblack-palette.json,palettizer/resources/mtn94-palette.json \
    output.png \
    30
```
```cmd
REM Windows
python palettizer\main.py palettizer\resources\bliss.jpg ^
    palettizer\resources\mtnblack-palette.json,palettizer\resources\mtn94-palette.json ^
    output.png ^
    30
```

## For developers

Run tests:

```shell
pip install .[test]
pytest
```

