from quantize import quantize
from palette import parse_palette
from skimage import io
import sys

if __name__ != '__main__':
    print("The script isn't executed as main, terminating")
    exit(1)

if len(sys.argv) < 4:
    raise Exception('Expected 3 arguments: input image path, palette file path and output image path')
input_img = sys.argv[1]
palette = sys.argv[2]
output_img = sys.argv[3]

print('Parsing the palette from ' + palette + '...')
palette = parse_palette(palette)
print("Successfully parsed")

print('Quantizing the image from file ' + input_img + '...')
result, palette_hystogram = quantize(input_img, palette)
print('Quantization finished')

print('Saving the quantized image to ' + output_img + '...')
io.imsave(output_img, result)
print('Successfully saved')

print("Palette colors usage:")
palette_hystogram_sorted = sorted(palette_hystogram.items(), key=lambda i: i[1])
palette_hystogram_sorted.reverse()
image_area = result.shape[0] * result.shape[1]
for item in palette_hystogram_sorted:
    print(f"Color: {palette[item[0]]['name']}, area: {(item[1] / image_area) * 100} %")

exit(0)
