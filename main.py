from PIL import Image
from quantize import quantize
from palette import parse_palette

# if __name__ == '__main__':
#     print_hi('PyCharm')

print("Parsing the palette...")
palette = parse_palette('arton-palette.json')
print("Successfully parsed")

print('Opening image...')
im = Image.open("testimage2.png")
print('Image opened')
print(im.format, im.size, im.mode)

print('Quantizing the image...')
quantize(im, palette
         # [(0, 0, 0),
         #      (255, 255, 255),
         #      (255, 255, 0),
         #      (255, 0, 255),
         #      (0, 255, 255),
         #      (255, 0, 0),
         #      (0, 255, 0),
         #      (0, 0, 255)]
)
print('Quantization finished')

print('Saving the quantized image...')
im.save('outputimage.png')
print('Successfully saved')

exit(0)
