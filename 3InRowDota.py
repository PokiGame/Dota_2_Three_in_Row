from array import array
from PIL import Image, ImageGrab
import os
import numpy as np
import pyautogui
from colorama import Fore, Style, init
import time
import keyboard  # Додаємо бібліотеку для роботи з гарячими клавішами

def find_best_move(board1):
    board = board1.copy()

    def count_matches(line):
        max_count = 0
        count = 1
        prev = line[0]
        for i in range(1, len(line)):
            if line[i] == prev:
                count += 1
            else:
                max_count = max(max_count, count)
                count = 1
                prev = line[i]
        return max(max_count, count)

    def get_best_move_for_board(board):
        best_move = None
        max_count = 0

        for i in range(len(board)):
            for j in range(len(board[i])):
                if j < len(board[i]) - 1:
                    board[i][j], board[i][j + 1] = board[i][j + 1], board[i][j]
                    row_count = count_matches(board[i])
                    col_count = max(count_matches([board[x][j] for x in range(len(board))]),
                                    count_matches([board[x][j + 1] for x in range(len(board))]))
                    if row_count >= 3 or col_count >= 3:
                        if row_count > max_count or col_count > max_count:
                            best_move = ((i, j), (i, j + 1))
                            max_count = max(row_count, col_count)
                    board[i][j], board[i][j + 1] = board[i][j + 1], board[i][j]

                if i < len(board) - 1:
                    board[i][j], board[i + 1][j] = board[i + 1][j], board[i][j]
                    row_count = max(count_matches(board[i]), count_matches(board[i + 1]))
                    col_count = count_matches([board[x][j] for x in range(len(board))])
                    if row_count >= 3 or col_count >= 3:
                        if row_count > max_count or col_count > max_count:
                            best_move = ((i, j), (i + 1, j))
                            max_count = max(row_count, col_count)
                    board[i][j], board[i + 1][j] = board[i + 1][j], board[i][j]

        return best_move

    best_move = get_best_move_for_board(board)
    return best_move

def average_color(image):
    np_image = np.array(image)
    avg_color = np.mean(np_image, axis=(0, 1))
    return tuple(avg_color.astype(int))

def color_distance(color1, color2):
    return np.sqrt(np.sum((np.array(color1) - np.array(color2)) ** 2))

def get_color_mapping(colors, tolerance):
    unique_colors = []
    color_mapping = {}
    color_id = 0

    for color in colors:
        found = False
        for unique_color in unique_colors:
            if color_distance(color, unique_color) < tolerance:
                color_mapping[color] = color_mapping[unique_color]
                found = True
                break
        if not found:
            unique_colors.append(color)
            color_mapping[color] = color_id
            color_id += 1

    return color_mapping

def split_image(image, square_size, tolerance=30):
    img_width, img_height = image.size

    color_matrix = []
    all_colors = []

    for y in range(0, img_height, square_size):
        row_colors = []
        for x in range(0, img_width, square_size):
            box = (x, y, min(x + square_size, img_width), min(y + square_size, img_height))
            square = image.crop(box)
            avg_color = average_color(square)
            all_colors.append(avg_color)
            row_colors.append(avg_color)
        color_matrix.append(row_colors)

    color_mapping = get_color_mapping(all_colors, tolerance)

    numeric_matrix = np.zeros((len(color_matrix), len(color_matrix[0])))

    for y in range(len(color_matrix)):
        for x in range(len(color_matrix[0])):
            color = color_matrix[y][x]
            numeric_matrix[y][x] = color_mapping[color]

    return numeric_matrix, color_matrix

def save_image(image, file_name):
    image.save(file_name)

def save_color_matrix_image(color_matrix, file_name):
    img_array = np.array(color_matrix, dtype=np.uint8)
    img = Image.fromarray(img_array, 'RGB')
    img.save(file_name)

def take_screenshot_and_process():
    print("Захоплення скріншоту області екрану...")
    screenshot = ImageGrab.grab(bbox=(225, 135, 945, 855))
    save_image(screenshot, "screenshot.png")
    print("Скріншот захоплено.")

    square_size = 90
    tolerance = 10

    print("Аналіз скріншоту...")
    board, color_matrix = split_image(screenshot, square_size, tolerance)
    save_color_matrix_image(color_matrix, "color_matrix.png")
    print("Скріншот проаналізовано.")

    print("Пошук найкращого ходу...")
    best_move = find_best_move(board)
    print("Найкращий хід знайдено: ", best_move)
    tolerance = 10

    if best_move is not None:
        (rr, cr), (rg, cg) = best_move
        print_array_with_highlight(board, rr, cr, rg, cg)
        return (rr, cr), (rg, cg)
    else:
        print("Немає доступних ходів.")
        tolerance += 10
        return None

def execute_best_move(start, end):
    if start and end:
        x_start, y_start = 225 + start[1] * 90 + 45, 135 + start[0] * 90 + 45
        x_end, y_end = 225 + end[1] * 90 + 45, 135 + end[0] * 90 + 45

        print("Виконання найкращого ходу...")
        pyautogui.moveTo(x_start, y_start, duration=0.05)
        pyautogui.dragTo(x_end, y_end, duration=0.2)
        print("Хід виконано.")

def print_array_with_highlight(array, rr, cr, rg, cg):
    for i in range(8):
        for j in range(8):
            if (i == rr and j == cr):
                print(Fore.RED + str(int(array[i][j])) + Style.RESET_ALL, end=" ")
            elif (i == rg and j == cg):
                print(Fore.GREEN + str(int(array[i][j])) + Style.RESET_ALL, end=" ")
            else:
                print(int(array[i][j]), end=" ")
        print("")




if __name__ == "__main__":
    time.sleep(3)
    while True:
        if keyboard.is_pressed('p'):
             print("Гаряча клавіша p натиснута. Програма завершена.")
             break
        move = take_screenshot_and_process()
        if move:
            execute_best_move(*move)
        #time.sleep(0.1)
