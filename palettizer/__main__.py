from . quantize import quantize
from . palette import Palette
from . htmlview import image_and_palette_as_html
from skimage import io
import sys


def nonempty_str(value):
    str_in = str(value)
    if len(str_in) <= 0:
        raise Exception("a non-empty argument is required")
    return str_in


if __name__ != '__main__':
    print("The script isn't executed as main, terminating")
    exit(1)

if len(sys.argv) < 4:
    raise Exception('Expected 3 arguments: input image path, palette file path and output image path')
input_img = nonempty_str(sys.argv[1])
palette = nonempty_str(sys.argv[2])
output_img = nonempty_str(sys.argv[3])

n_colors = 0
if len(sys.argv) > 4:
    n_colors = int(sys.argv[4])
    if n_colors < 0:
        raise Exception("Number of colors should be >= 0")

print('Parsing the palette from ' + palette + '...')
palette = Palette.from_files(palette.split(","))
print("Successfully parsed")

print('Quantizing the image from file ' + input_img + '...')
q_image = quantize(input_img, palette, n_colors)
print('Quantization finished')

print('Saving the quantized image to ' + output_img + '...')
io.imsave(output_img, q_image.image)
print('Successfully saved')

print("Palette colors usage:")
colors_sorted = sorted(q_image.color_pixels.items(), key=lambda i: i[1], reverse=True)
image_area = q_image.image.shape[0] * q_image.image.shape[1]
for item in colors_sorted:
    area_percentage = (item[1] / image_area) * 100
    print(f"Color: {item[0].name} {item[0].vendor}, area: {area_percentage} %")

html_file = output_img + ".html"
print("Saving results to HTML file " + html_file)
html_result = image_and_palette_as_html(q_image)
with open(html_file, 'w') as f:
    f.write(html_result)

exit(0)
