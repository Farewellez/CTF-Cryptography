from PIL import Image

with Image.open("flag_7ae18c704272532658c10b5faad06d74.png") as image1:
    img1 = image1.convert("RGB")
    rgb_bytes1 = img1.tobytes()

# print(rgb_bytes1)
# print(len(rgb_bytes1))

with Image.open("lemur_ed66878c338e662d3473f0d98eedbd0d.png") as image2:
    img2 = image2.convert("RGB")
    rgb_bytes2 = img2.tobytes()

# print(rgb_bytes2)
# print(len(rgb_bytes2))

assert len(rgb_bytes1) == len(rgb_bytes2)

flag = bytes([x ^ y for x,y in zip(rgb_bytes1, rgb_bytes2)])

width, height = img1.size 

solved_image = Image.frombytes("RGB", (width, height), flag)
solved_image.save("solve.png")