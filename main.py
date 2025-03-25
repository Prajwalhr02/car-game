import pygame
import sys
import os
import random  # Add import for random
import json  # Add import for leaderboard storage
import time  # Add import for timeout handling
import threading  # Add threading for firework effect
import itertools  # Add itertools for cycling firework characters

# Suppress libpng warnings
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Welcome! car_game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load assets with error handling
try:
    car_image = pygame.image.load("car.png")  # Load from root directory
    car_image = pygame.transform.scale(car_image, (100, 100))  # Expanded both horizontally and vertically
    car_image = car_image.convert_alpha()  # Ensure the image supports transparency
    car_image.set_colorkey(WHITE)  # Remove white background by setting it as transparent
except pygame.error:
    print("Error: 'car.png' not found. Please add the file.")
    sys.exit()

try:
    start_sound = pygame.mixer.Sound("start.wav")  # Load from root directory
except pygame.error:
    print("Error: 'start.wav' not found. Please add the file.")
    sys.exit()

try:
    stop_sound = pygame.mixer.Sound("stop.wav")  # Load from root directory
except pygame.error:
    print("Error: 'stop.wav' not found. Please add the file.")
    sys.exit()

try:
    crash_sound = pygame.mixer.Sound("crash.wav")  # Load from root directory
except pygame.error:
    print("Error: 'crash.wav' not found. Please add the file.")
    sys.exit()

# Clear the console
os.system('cls' if os.name == 'nt' else 'clear')
# Game variabless
car_x, car_y = WIDTH // 2, HEIGHT // 2
is_running = False
is_paused = False  # New variable for pause state

# Obstacle dimensions and position
obstacle_width, obstacle_height = 50, 50

# List to hold multiple obstacles
obstacles = [{"x": random.randint(0, WIDTH - obstacle_width), "y": random.randint(0, HEIGHT - obstacle_height)}]

# Coin dimensions and position
coin_width, coin_height = 30, 30
coin_x = random.randint(0, WIDTH - coin_width)
coin_y = random.randint(0, HEIGHT - coin_height)

# Score variable
score = 0

# High score variable
high_score = 0

# Font for displaying status
font = pygame.font.Font(None, 36)

# Font for displaying instructions
instruction_font = pygame.font.Font(None, 28)

# Display instructions on the terminal
print("""
Welcome to the car_game!
Controls:
- Press 'S' to start the car
- Press 'T' to stop the car
- Press 'P' to pause/unpause the game
- Press 'H' for help
- Press 'Q' to quit the game
- Use arrow keys to move the car (only when running)
""")

# Leaderboard file
LEADERBOARD_FILE = "leaderboard.json"

# Load leaderboard
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)
    return []

# Save leaderboard
def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file)

# Display leaderboard
def display_leaderboard():
    leaderboard = load_leaderboard()
    while True:
        screen.fill(WHITE)  # Clear the screen
        title_surface = font.render("Leaderboard", True, BLACK)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))  # Display title at the top

        for idx, entry in enumerate(sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:5], start=1):
            entry_surface = font.render(f"{idx}. {entry['name']} - {entry['score']}", True, WHITE)
            screen.blit(entry_surface, (WIDTH // 2 - entry_surface.get_width() // 2, 100 + idx * 40))  # Display each entry

        back_surface = font.render("Press 'B' to go back", True, BLACK)
        screen.blit(back_surface, (WIDTH // 2 - back_surface.get_width() // 2, HEIGHT - 100))  # Display back button

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:  # Back to menu
                    return

# Function to display the menu on the game screen
def display_menu():
    screen.fill(WHITE)  # Set the screen to white (inverted from black)

    title_surface = font.render("Welcome! to car_game", True, BLACK)  # Text color inverted to black
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 200))  # Adjusted position to fit below the title

    menu_options = [
        "1. Start Game",
        "2. View Leaderboard",
        "3. Instructions",
        "4. Quit"
    ]

    for idx, option in enumerate(menu_options):
        option_surface = font.render(option, True, BLACK)  # Text color inverted to black
        screen.blit(option_surface, (WIDTH // 2 - option_surface.get_width() // 2, 250 + idx * 50))  # Adjusted position to fit below the title

    pygame.display.flip()

# Function to display instructions on the game screen
def display_instructions():
    while True:
        screen.fill(WHITE)  # Set the screen to black
        instructions = [
            "Instructions:",
            "- Use arrow keys to move the car.",
            "- Press 'S' to start the game.",
            "- Press 'T' to stop the game.",
            "- Press 'P' to pause/unpause the game.",
            "- Avoid obstacles and collect coins.",
            "- Press 'Q' to quit the game."
            "- Yellow coins will increase your score." 
            "- You will get 10 points for each coin collected.",
            "- The game will get faster as your score increases "
            "- Red obstacles will end the game if you hit them.",
            "- The game will automatically restart after a crash.",
    
        ]

        for idx, line in enumerate(instructions):
            line_surface = font.render(line, True, BLACK)
            screen.blit(line_surface, (WIDTH // 2 - line_surface.get_width() // 2, 100 + idx * 40))

        back_surface = font.render("Press 'B' to go back", True, BLACK)
        screen.blit(back_surface, (WIDTH // 2 - back_surface.get_width() // 2, HEIGHT - 100))  # Display back button

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:  # Back to menu
                    return
def display_loading_screen():
    try:
        additional_image = pygame.image.load("loading_image.png")  # Load from root directory
        additional_image = pygame.transform.scale(additional_image, (300, 300))  # Adjust size for better visibility
    except pygame.error as e:
        print(f"Warning: Loading image not found or failed to load. Error: {e}")
        additional_image = None  # Set to None if the file is not found

    screen.fill(WHITE)  # Set the screen to white
    if additional_image:
        screen.blit(additional_image, (WIDTH // 2 - additional_image.get_width() // 2, HEIGHT // 2 - additional_image.get_height() // 2))  # Center the additional image
    pygame.display.flip()  # Update the display
    pygame.time.delay(10000)  # Display for 10 seconds

# Main menu logic
def main_menu():
    display_loading_screen()  # Show the loading screen before the menu
    while True:
        display_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Start Game
                    return True
                elif event.key == pygame.K_2:  # View Leaderboard
                    display_leaderboard()
                elif event.key == pygame.K_3:  # Instructions
                    display_instructions()
                elif event.key == pygame.K_4:  # Quit
                    pygame.quit()
                    sys.exit()

# Function to check collision
def check_collision(car_rect, obstacle_rect):
    return car_rect.colliderect(obstacle_rect)

# Function to check collision with the center part of the obstacle 
def check_center_collision(car_rect, obstacle_rect):
    center_obstacle_rect = pygame.Rect(
        obstacle_rect.x + obstacle_width // 4,
        obstacle_rect.y + obstacle_height // 4,
        obstacle_width // 2,
        obstacle_height // 2
    )
    return car_rect.colliderect(center_obstacle_rect)

# Function to display a popup dialog box with optional text input
def display_popup_with_input(message, prompt_text=None):
    popup_font = pygame.font.Font(None, 48)
    input_font = pygame.font.Font(None, 36)
    popup_surface = popup_font.render(message, True, WHITE)
    popup_rect = popup_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    pygame.draw.rect(screen, BLACK, popup_rect.inflate(20, 20))  # Background for the popup
    screen.blit(popup_surface, popup_rect)

    if prompt_text:
        input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 40)
        pygame.draw.rect(screen, WHITE, input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        pygame.display.flip()

        user_input = ""
        start_time = time.time()  # Start the timeout timer
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Submit input
                        return user_input if user_input else "Player"  # Default name if input is empty
                    elif event.key == pygame.K_BACKSPACE:  # Remove last character
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode

            # Check for timeout (10 seconds)
            if time.time() - start_time > 10:
                return "Player"  # Default name after timeout

            # Update input box
            screen.fill(WHITE, input_box)  # Clear the input box area
            label_surface = input_font.render("Name -   ", True, BLACK)  # Added extra spaces after "Name -"
            screen.blit(label_surface, (input_box.x + 5, input_box.y + 5))
            input_surface = input_font.render(user_input, True, BLACK)  # User input text
            screen.blit(input_surface, (input_box.x + 90, input_box.y + 5))  # Adjusted offset for "Name -   "
            pygame.display.flip()

    pygame.time.wait(2000)  # Display the popup for 2 seconds if no input is required

def firework_effect():
    firework_chars = itertools.cycle(["*", "o", ".", "+", "x"])  # Characters for firework effect
    for _ in range(20):  # Number of firework bursts
        print("\033[1;31m" + " " * random.randint(0, 50) + next(firework_chars) + "\033[0m")  # Random position and color
        time.sleep(0.1)  # Delay between bursts

def firework_effect_in_game():
    firework_chars = itertools.cycle(["*", "o", ".", "+", "x"])  # Characters for firework effect
    for _ in range(20):  # Number of firework bursts
        x = random.randint(50, WIDTH - 50)  # Random x-coordinate
        y = random.randint(50, HEIGHT - 50)  # Random y-coordinate
        char = next(firework_chars)
        color = random.choice([RED, (255, 165, 0), (255, 255, 0)])  # Random firework colors
        pygame.draw.circle(screen, color, (x, y), 10)  # Draw firework burst
        pygame.display.flip()  # Update the display
        time.sleep(0.1)  # Delay between bursts
        screen.fill(WHITE)  # Clear the screen after each burst

def burst_effect_in_game():
    for _ in range(30):  # Number of bursts
        for _ in range(10):  # Number of particles per burst
            x = random.randint(50, WIDTH - 50)  # Random x-coordinate
            y = random.randint(50, HEIGHT - 50)  # Random y-coordinate
            color = random.choice([RED, (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)])  # Random colors
            pygame.draw.circle(screen, color, (x, y), random.randint(5, 15))  # Draw particle
        pygame.display.flip()  # Update the display
        time.sleep(0.1)  # Delay between bursts
        screen.fill(WHITE)  # Clear the screen after each burst

# Function to reset the game
def reset_game():
    global car_x, car_y, obstacles, coin_x, coin_y, score, high_score, is_running, is_paused
    if score > high_score:  # Update high score if the current score is higher
        high_score = score
        name = display_popup_with_input("New High Score!", "Enter your name:")  # Show popup with input for name
        leaderboard = load_leaderboard()
        leaderboard.append({"name": name, "score": high_score})
        save_leaderboard(leaderboard)
        # Start firework and burst effects in the game console
        firework_effect_in_game()
        burst_effect_in_game()
    car_x, car_y = WIDTH // 2, HEIGHT // 2
    obstacles = [{"x": random.randint(0, WIDTH - obstacle_width), "y": random.randint(0, HEIGHT - obstacle_height)}]
    coin_x = random.randint(0, WIDTH - coin_width)
    coin_y = random.randint(0, HEIGHT - coin_height)
    score = 0
    is_running = False  # Ensure the game is not running after a reset
    is_paused = False
    display_popup_with_input("Crash! Restarting...")  # Show popup for crash
    print("Game restarted!")  # No music is played here

# Pause functionality
def toggle_pause():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print("Game Paused. Press 'P' to resume.")

# Function to display a hamburger button
def display_hamburger_button():
    pygame.draw.rect(screen, BLACK, (10, 10, 30, 30))  # Draw the button background
    for i in range(3):  # Draw three horizontal lines
        pygame.draw.line(screen, WHITE, (15, 15 + i * 8), (35, 15 + i * 8), 2)

# Function to check if the hamburger button is clicked
def is_hamburger_clicked(pos):
    return 10 <= pos[0] <= 40 and 10 <= pos[1] <= 40

# Main game logic
if main_menu():  # Show main menu before starting the game
    running = True
    while running:
        screen.fill(WHITE)  # Clear the screen
        screen.blit(car_image, (car_x, car_y))  # Draw the car

        # Display the hamburger button
        display_hamburger_button()

        # Add new obstacles based on score
        if is_running and len(obstacles) < (score // 50):  # Add one obstacle for every 50 points
            obstacles.append({"x": random.randint(0, WIDTH - obstacle_width), "y": -obstacle_height})

        # Move and draw obstacles
        for obstacle in obstacles:
            if is_running and not is_paused:  # Only move obstacles if the game is running and not paused
                obstacle["y"] += 0.2 + (score // 100) * 0.1  # Increase speed as score exceeds multiples of 100
                if obstacle["y"] > HEIGHT:  # Reset obstacle to the top after it moves out of the screen
                    obstacle["y"] = -obstacle_height
                    obstacle["x"] = random.randint(0, WIDTH - obstacle_width)
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle_width, obstacle_height)
            pygame.draw.rect(screen, RED, obstacle_rect)

            # Check for collision with the center part of the obstacle
            car_rect = pygame.Rect(car_x, car_y, 100, 50)  # Car dimensions
            if check_center_collision(car_rect, obstacle_rect):
                crash_sound.play()  # Play crash sound
                reset_game()
                break

        # Draw the coin
        coin_rect = pygame.Rect(coin_x, coin_y, coin_width, coin_height)
        pygame.draw.circle(screen, (255, 215, 0), (coin_x + coin_width // 2, coin_y + coin_height // 2), coin_width // 2)

        # Display car status
        if is_paused:
            status_text = "Paused"
        else:
            status_text = "Running" if is_running else "Stopped"
        status_surface = font.render(f"Car Status: {status_text}", True, BLACK)
        screen.blit(status_surface, (50, 10))  # Adjusted position to avoid overlapping with the hamburger button

        # Display score and high score in one line
        score_surface = font.render(f"Score: {score}", True, BLACK)
        high_score_surface = font.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(score_surface, (WIDTH - 350, 10))  # Adjusted position to fit within the screen
        screen.blit(high_score_surface, (WIDTH - 200, 10))  # Adjusted position to fit within the screen

        pygame.display.flip()  # Update the display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse click
                if is_hamburger_clicked(event.pos):  # If hamburger button is clicked
                    if main_menu():  # Return to the main menu
                        reset_game()  # Reset the game when returning to the menu
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:  # Help
                    pass
                elif event.key == pygame.K_s:  # Start
                    if not is_running:  # Only play start sound if the game is not already running
                        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
                        is_running = True
                        is_paused = False  # Ensure the game is unpaused when starting
                        start_sound.play()  # Play start sound only when 'S' is pressed
                elif event.key == pygame.K_t:  # Stop
                    if is_running:
                        is_running = False
                        if not pygame.mixer.get_busy():  # Ensure no other sound is playing
                            stop_sound.play()
                elif event.key == pygame.K_p:  # Pause
                    toggle_pause()  # Toggle pause state
                elif event.key == pygame.K_q:  # Quit
                    running = False

        # Handle car movement
        keys = pygame.key.get_pressed()
        if is_running and not is_paused:  # Only allow movement if the car is running and not paused
            if keys[pygame.K_UP] and car_y > 0:
                car_y -= 2  # Reduced speed from 3 to 2
            if keys[pygame.K_DOWN] and car_y < HEIGHT - 50:
                car_y += 2  # Reduced speed from 3 to 2
            if keys[pygame.K_LEFT] and car_x > 0:
                car_x -= 2  # Reduced speed from 3 to 2
            if keys[pygame.K_RIGHT] and car_x < WIDTH - 100:
                car_x += 2  # Reduced speed from 3 to 2

        # Update score logic to award 10 points per coin
        if check_collision(car_rect, coin_rect):
            score += 10  # Each coin adds 10 points
            coin_x = random.randint(0, WIDTH - coin_width)
            coin_y = random.randint(0, HEIGHT - coin_height)

pygame.quit()
sys.exit()
