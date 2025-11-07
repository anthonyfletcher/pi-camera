from DriverOLED1in32 import OLED_1in32, OLED_WIDTH, OLED_HEIGHT

logo = [[0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,1,1],[1,1,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,0,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,1,1,0,1,1],[1,1,0,0,0,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1,1],[1,1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1,1],[1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,1,1,0,1,1],[1,1,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,0,1,1,1],[1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
logo_height = len(logo)
logo_width = len(logo[0])

x_offset = (OLED_WIDTH- logo_width) // 2
y_offset = (OLED_HEIGHT - logo_height) // 2

buffer = [0x00] * (OLED_WIDTH * OLED_HEIGHT)

for y in range(logo_height):
    for x in range(logo_width):
        pixel_value = 0x0F if logo[y][x] == 1 else 0x00
        screen_x = x + x_offset
        screen_y = y + y_offset
        index = (screen_y * OLED_WIDTH + screen_x) // 2
        if screen_x % 2 == 0:
          buffer[index] = (pixel_value << 4) | (buffer[index] & 0x0F)
        else:
          buffer[index] = (buffer[index] & 0xF0) | pixel_value

display = OLED_1in32()
display.Init()
display.ShowImage(buffer)

