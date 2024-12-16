import pygame
import random

# Khởi tạo Pygame
pygame.init()

# Các thông số màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Campus courier"

# Cài đặt font chữ
pygame.font.init()
font = pygame.font.SysFont("comicsans", 30)
# Lớp Game
class Game:
    TICK_RATE = 60
    is_game_over = False
    collision_count = 0

    correct_answers = dict({"câu 1.png":"2022","câu 2.png":"Dr.Dung","câu 3.png":"1","câu 4.png":"3","câu 5.png":"Prof.Thinh","câu 6.png":"1976"})

    def __init__(self, title, width, height, background_image_path, choice_background_path, question_image_paths):
        self.title = title
        self.width = width
        self.height = height

        # Tải hình nền chính, hình nền lựa chọn và background câu hỏi
        self.background_image = pygame.image.load(background_image_path)
        self.background_image = pygame.transform.scale(self.background_image, (width, height))

        self.choice_background = pygame.image.load(choice_background_path)
        self.choice_background = pygame.transform.scale(self.choice_background, (width, height))

        self.question_image_paths = question_image_paths

        # Tạo màn hình game
        self.game_screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        self.current_question_image = None

        # Khởi tạo đồng hồ
        self.clock = pygame.time.Clock()

        # **Khởi tạo Pygame mixer (âm thanh)**
        pygame.mixer.init()

        # **Tải nhạc nền và phát**
        pygame.mixer.music.load('nhạc nền.mp3')  # Thay 'background_music.mp3' bằng đường dẫn đúng
        pygame.mixer.music.set_volume(0.5)  # Điều chỉnh âm lượng nhạc nền
        pygame.mixer.music.play(-1, 0.0)  # Phát nhạc nền liên tục

        # **Tải hiệu ứng âm thanh**
        self.collision_sound = pygame.mixer.Sound('chạm vcan.wav')  
        self.correct_answer_sound = pygame.mixer.Sound('thắng.wav')
        self.lose_answer_sound = pygame.mixer.Sound('thua cuộc.wav')
        self.pass_sound = pygame.mixer.Sound('pass.wav')
    def run_game_loop(self):
        level = 1  # Bắt đầu từ vòng 1
        while level <= 10:
            self.is_game_over = False
            player = PlayerCharacter("green campus.png", 375, 500,60, 60)  # Nhân vật
            delivery_point = GameObject("điểm đến.jpg", 350, 10,100, 100)  # Điểm giao hàng
            pickup_point = self.create_random_pickup_point()  # Tạo điểm lấy hàng ngẫu nhiên
            item = None  # Thùng hàng, ban đầu không có gì

            # Tăng số lượng vật cản và tốc độ theo từng vòng
            obstacles = self.create_obstacles(level)

            # Biến kiểm tra xem câu hỏi đã được trả lời chưa
            answered_correctly = False  # Biến để theo dõi câu hỏi đã trả lời hay chưa
            question_asked = False  # Biến kiểm tra xem câu hỏi đã được hỏi hay chưa

            # Biến đếm số lần va chạm

            max_collisions = 2  # Giới hạn số lần va chạm tối đa

            while not self.is_game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_game_over = True

                # Xử lý di chuyển
                keys = pygame.key.get_pressed()
                player.move(keys, self.width, self.height)

                # Kiểm tra va chạm với vật cản
                for obstacle in obstacles:
                    if player.detect_collision(obstacle):
                        self.collision_count += 1
                        pygame.mixer.stop()  # Dừng tất cả âm thanh
                        self.collision_sound.play()  # Phát âm thanh va chạm
                        pygame.time.wait(500)
                        if self.collision_count > max_collisions:
                            self.is_game_over = True
                            pygame.mixer.stop()  # Dừng tất cả âm thanh
                            self.lose_answer_sound.play()
                            pygame.time.wait(6000) 
                            return
                        # Nếu chưa trả lời câu hỏi và chưa hỏi câu hỏi này
                        if not answered_correctly and not question_asked:
                            self.display_question_or_exit(level)  # Hiển thị câu hỏi xác nhận
                            question_asked = True  # Đánh dấu là câu hỏi đã được hỏi

                            if self.is_game_over: # Nếu người chơi chọn thoát, kết thúc game
                                pygame.mixer.stop()  # Dừng tất cả âm thanh
                                self.lose_answer_sound.play()
                                pygame.time.wait(6000)    
                                return  # Kết thúc game nếu chọn thoát

                            # Sau khi câu hỏi hiển thị và người chơi trả lời
                            answered_correctly = self.ask_question(level)  # Kiểm tra câu hỏi

                        if answered_correctly:
                            pygame.mixer.stop()  # Dừng tất cả âm thanh
                            self.correct_answer_sound.play()
                            pygame.time.wait(1000)
                            # Đặt lại vị trí của player về vị trí ban đầu sau khi trả lời đúng
                            player.x_pos = 375
                            player.y_pos = 500
                            # Tạo lại vật cản mới và tiếp tục kiểm tra va chạm
                            obstacles = self.create_obstacles(level)  # Tạo lại vật cản mới
                            answered_correctly = False  # Đặt lại trạng thái câu hỏi
                            question_asked = False  # Đặt lại câu hỏi đã hỏi
                            break  # Thoát khỏi vòng lặp kiểm tra va chạm sau khi xử lý

                # Kiểm tra nếu người chơi tới điểm lấy hàng và lấy hàng
                if pickup_point and player.detect_collision(pickup_point) and item is None:
                    item = Item("thùng hàng.png", player.x_pos,player.y_pos, 30, 30)  # Tạo thùng hàng
                    pickup_point = None  # Xóa điểm lấy hàng

                # Kiểm tra nếu người chơi tới điểm giao hàng và giao hàng thành công
                if player.detect_collision(delivery_point) and item:
                    item = None  # Thùng hàng đã được giao, xóa thùng hàng
                    pygame.mixer.stop()  # Dừng tất cả âm thanh
                    self.pass_sound.play()
                    pygame.time.wait(500)
                    level += 1  # Chuyển sang vòng tiếp theo nếu tới điểm giao hàng
                    break  # Nếu đến điểm giao hàng, thoát khỏi vòng này và bắt đầu vòng mới

                # Vẽ lại màn hình
                self.game_screen.fill((255, 255, 255))  # Xóa màn hình (không cần nếu dùng background)
                self.game_screen.blit(self.background_image, (0, 0))  # Vẽ background

                # Vẽ các đối tượng
                player.draw(self.game_screen)
                if item:
                    item.update_position(player.x_pos, player.y_pos)  # Cập nhật vị trí thùng hàng theo nhân vật
                    item.draw(self.game_screen)
                delivery_point.draw(self.game_screen)
                if pickup_point:  # Vẽ điểm lấy hàng nếu còn
                    pickup_point.draw(self.game_screen)
                for obstacle in obstacles:
                    obstacle.move(self.width)  # Di chuyển vật cản
                    obstacle.draw(self.game_screen)

                # Cập nhật màn hình
                pygame.display.update()
                self.clock.tick(self.TICK_RATE)

            # Nếu người chơi trả lời sai, kết thúc game
            if self.is_game_over:
                pygame.mixer.stop()  # Dừng tất cả âm thanh
                self.lose_answer_sound.play()
                pygame.time.wait(2000)
                break  # Kết thúc game nếu thua

    def create_random_pickup_point(self):
        """Tạo điểm lấy hàng ngẫu nhiên"""
        x = random.randint(SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4)
        y = random.randint(SCREEN_HEIGHT // 3, 2 * SCREEN_HEIGHT // 3)
        return GameObject("thùng hàng.png", x, y, 50, 50)

    def create_obstacles(self, level):
        obstacles = []
        # Tăng dần số lượng vật cản từ vòng 1 đến vòng 10
        num_obstacles = 1 + (level - 1) // 3  # Tăng số lượng vật cản sau mỗi 3 vòng

        # Tăng tốc độ di chuyển của vật cản (tăng tốc nhanh hơn)
        speed = 5 + (level - 1) * 2  # Tốc độ vật cản tăng dần từ 5 và tăng 2 đơn vị mỗi vòng

        for _ in range(num_obstacles):
            # Tạo vật cản tại vị trí ngẫu nhiên trong khu vực giữa màn hình
            x = random.randint(SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4)
            y = random.randint(SCREEN_HEIGHT // 3, 2 * SCREEN_HEIGHT // 3)
            obstacles.append(Obstacle(x, y, 50, 50, speed))
        return obstacles

    def display_game_over(self, message):
        # Hàm hiển thị thông báo game over với khung bao quanh
        font = pygame.font.SysFont("Arial", 40, bold=True)  # Phông chữ đậm hơn và kích thước lớn hơn
        game_over_text = font.render(message, True, (255, 255, 255))  # Màu trắng, dễ nhìn hơn

        # Khung bao quanh thông báo
        text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        border_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 20, text_rect.width + 40, text_rect.height + 40)

        # Vẽ lại màn hình, giữ nguyên background và các đối tượng khác
        self.game_screen.blit(self.background_image, (0, 0))  # Vẽ background chính
        pygame.draw.rect(self.game_screen, (0, 0, 0), border_rect, 4)  # Vẽ khung bao quanh thông báo
        self.game_screen.blit(game_over_text, text_rect)  # Hiển thị thông báo

        pygame.display.update()  # Cập nhật màn hình

        # Dừng lại một chút để người chơi có thể nhìn thấy thông báo
        pygame.time.wait(2000)  # Chờ 2 giây trước khi thoát

    def ask_question(self, level):
        # Lựa chọn ngẫu nhiên một câu hỏi
        question_image_path = random.choice(self.question_image_paths)
        self.current_question_image = pygame.image.load(question_image_path)
        self.current_question_image = pygame.transform.scale(self.current_question_image, (self.width, self.height))

        # Vẽ hình nền câu hỏi lên màn hình
        self.game_screen.blit(self.current_question_image, (0, 0))
        pygame.display.update()

        # Hàm nhập câu trả lời
        user_answer = self.get_user_input("What is the answer?")

        correct_answer = self.correct_answers.get(question_image_path)

        # Kiểm tra câu trả lời
        if user_answer == correct_answer:
            return True
        else:
            return False

    def get_user_input(self, prompt):
        input_box = pygame.Rect(210, 300, 400, 50)
        user_input = ""
        is_typing = True

        while is_typing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        is_typing = False
                    else:
                        user_input += event.unicode

            # Vẽ màn hình câu hỏi
            self.game_screen.fill((0, 0, 0))  # Xóa màn hình
            self.game_screen.blit(self.current_question_image, (0, 0))  # Vẽ background câu hỏi

            # Vẽ ô nhập câu trả lời
            pygame.draw.rect(self.game_screen, (255, 255, 255), input_box, 2)
            answer_text = font.render(user_input, True, (0,0,0))
            self.game_screen.blit(answer_text, (input_box.x + 30, input_box.y + 5))

            pygame.display.update()
            self.clock.tick(60)  # Tốc độ khung hình

        return user_input

    def display_question_or_exit(self, level):
        # Vẽ hình nền lựa chọn
        self.game_screen.blit(self.choice_background, (0, 0))  # Vẽ background lựa chọn

        # Xác định khu vực nút trên background để người chơi có thể tương tác
        continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 270, 150)

        pygame.display.update()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()  # Lấy vị trí chuột

                    # Kiểm tra click vào nút "Chơi tiếp"
                    if continue_button_rect.collidepoint(mouse_pos):
                        print("Chơi tiếp!")  # Thông báo nếu click vào nút "Chơi tiếp"
                        waiting_for_input = False  # Quay lại trò chơi sau khi chọn "Chơi tiếp"
                        return  # Quay lại vòng lặp trò chơi

                    # Kiểm tra click vào nút "Kết thúc"
                    elif quit_button_rect.collidepoint(mouse_pos):
                        print("Kết thúc game!")  # Thông báo nếu click vào nút "Kết thúc"
                        self.is_game_over = True  # Đánh dấu kết thúc game
                        waiting_for_input = False  # Dừng vòng lặp, thoát game
                        return  # Kết thúc game và thoát


class GameObject:
    def __init__(self, image_path, x, y, width, height):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.x_pos = x
        self.y_pos = y
        self.width = width
        self.height = height

    def draw(self, screen):
        screen.blit(self.image, (self.x_pos, self.y_pos))

    def detect_collision(self, other):
        if self.x_pos < other.x_pos + other.width and self.x_pos + self.width > other.x_pos:
            if self.y_pos < other.y_pos + other.height and self.y_pos + self.height > other.y_pos:
                return True
        return False


class PlayerCharacter(GameObject):
    SPEED = 5

    def __init__(self, image_path, x, y, width, height):
        super().__init__(image_path, x, y, width, height)
        self.item = None  # Không có thùng hàng khi bắt đầu

    def move(self, keys, max_width, max_height):
        if keys[pygame.K_LEFT]:
            self.x_pos -= self.SPEED
        if keys[pygame.K_RIGHT]:
            self.x_pos += self.SPEED
        if keys[pygame.K_UP]:
            self.y_pos -= self.SPEED
        if keys[pygame.K_DOWN]:
            self.y_pos += self.SPEED

        if self.x_pos < 0:
            self.x_pos = 0
        elif self.x_pos > max_width - self.width:
            self.x_pos = max_width - self.width
        if self.y_pos < 0:
            self.y_pos = 0
        elif self.y_pos > max_height - self.height:
            self.y_pos = max_height - self.height

class Obstacle(GameObject):
    def __init__(self, x, y, width, height, speed):
        super().__init__("enemy.png", x, y, width, height)
        self.direction = 1
        self.speed = speed

    def move(self, max_width):
        if self.x_pos <= 0 or self.x_pos + self.width >= max_width:
            self.direction *= -1  # Đổi chiều khi chạm vào rìa màn hình

        self.x_pos += self.speed * self.direction  # Di chuyển vật cản


class Item(GameObject):
    def __init__(self, image_path, x, y, width, height):
        super().__init__(image_path, x, y, width, height)

    def update_position(self, x, y):
        self.x_pos = x
        self.y_pos = y

# Khởi tạo game
questions_images = ["câu 1.png","câu 2.png","câu 3.png","câu 4.png","câu 5.png","câu 6.png" ]
new_game = Game(SCREEN_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, "background.png","bgthua.gif", questions_images)
new_game.run_game_loop()

pygame.quit()
quit()