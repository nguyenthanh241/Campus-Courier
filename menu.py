import pygame
import sys
import subprocess  # Đảm bảo subprocess được import
from button import Button

pygame.init()
clock = pygame.time.Clock()

SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Menu")

BG = pygame.image.load("assets/Background.jpg")

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def play():
    # Chạy game CrossRoad.py từ subprocess
    subprocess.Popen(["python3", "CrossRoad.py"])  # Dùng Popen để không chặn chương trình chính

def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        
        background_image = pygame.image.load("assets/How_to_play.png")
        SCREEN.blit(background_image, (0, 0))
        OPTIONS_BACK = Button(image=pygame.image.load("assets/How_to_play Rect.png"), pos=(550, 250), 
                            text_input="EXIT", font=get_font(60), base_color="#00f6ff", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(400, 230), 
                            text_input="Start", font=get_font(30), base_color="#00f6ff", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(400, 350), 
                            text_input="How to play", font=get_font(25), base_color="#00f6ff", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(400, 470), 
                            text_input="Quit", font=get_font(30), base_color="#00f6ff", hovering_color="White")
        
        # Vòng lặp nút bấm
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()  # Gọi hàm play() để chuyển sang game
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

if __name__ == "__main__":
    main_menu()
