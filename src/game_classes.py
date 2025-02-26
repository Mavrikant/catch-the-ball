import pygame
import random
import json
import os
from typing import Dict, List

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_RADIUS = 15
BOMB_RADIUS = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BALL_COLORS = [RED, GREEN, BLUE]

# Add the following constant to define the scores file path at the project root
SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'scores.json')

# Ball class
class Ball:
    def __init__(self):
        self.reset()
        self.y = 0  # Start from the top
        
    def reset(self):
        self.x = random.randint(BALL_RADIUS, WIDTH - BALL_RADIUS)
        self.y = -BALL_RADIUS  # Start just above the screen
        self.speed = random.randint(3, 7)
        self.color = random.choice(BALL_COLORS)
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), BALL_RADIUS)
        
    def is_caught(self, paddle_x, paddle_y):
        return (self.y + BALL_RADIUS >= paddle_y and 
                paddle_x <= self.x <= paddle_x + PADDLE_WIDTH)
                
    def is_off_screen(self):
        return self.y > HEIGHT

# Bomb class
class Bomb:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(BOMB_RADIUS, WIDTH - BOMB_RADIUS)
        self.y = -BOMB_RADIUS
        self.speed = random.randint(2, 5)
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), BOMB_RADIUS)
        # Draw bomb details (a simple fuse)
        pygame.draw.line(screen, RED, (self.x, self.y - BOMB_RADIUS), 
                        (self.x, self.y - BOMB_RADIUS - 10), 2)
        pygame.draw.circle(screen, RED, (self.x, self.y - BOMB_RADIUS - 12), 3)
        
    def is_caught(self, paddle_x, paddle_y):
        return (self.y + BOMB_RADIUS >= paddle_y and 
                paddle_x <= self.x <= paddle_x + PADDLE_WIDTH)
                
    def is_off_screen(self):
        return self.y > HEIGHT

# Game logic class
class GameLogic:
    def __init__(self, player_name: str = "Player"):
        self.player_name = player_name
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
        self.paddle_y = HEIGHT - 40
        self.paddle_speed = 8
        self.balls = [Ball()]
        self.bombs = []
        self.ball_spawn_timer = 0
        self.bomb_spawn_timer = 0
        self.ball_spawn_delay = 60
        self.bomb_spawn_delay = 180

    def save_score(self):
        scores = self.load_scores()
        scores.append({"name": self.player_name, "score": self.score})
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:10]  # Keep only top 10 scores
        
        with open(SCORES_FILE, "w") as f:
            json.dump(scores, f)

    @staticmethod
    def load_scores() -> List[Dict[str, any]]:
        if not os.path.exists(SCORES_FILE):
            return []
        try:
            with open(SCORES_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def reset_game(self):
        if self.game_over:
            self.save_score()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.balls = [Ball()]
        self.bombs = []
        self.ball_spawn_timer = 0
        self.bomb_spawn_timer = 0
        self.ball_spawn_delay = 60
        self.bomb_spawn_delay = 180
    
    def move_paddle_left(self):
        self.paddle_x = max(0, self.paddle_x - self.paddle_speed)
            
    def move_paddle_right(self):
        self.paddle_x = min(WIDTH - PADDLE_WIDTH, self.paddle_x + self.paddle_speed)
    
    def update_game_state(self):
        if self.game_over:
            return
            
        # Update balls
        caught_balls = []
        for ball in self.balls[:]:
            ball.update()
            if ball.is_caught(self.paddle_x, self.paddle_y):
                caught_balls.append(ball)
            elif ball.is_off_screen():
                self.balls.remove(ball)
        
        # Process caught balls
        for ball in caught_balls:
            if ball in self.balls:
                self.score += 1
                self.balls.remove(ball)

        # Update bombs
        caught_bombs = []
        off_screen_bombs = []
        for bomb in self.bombs[:]:
            bomb.update()
            if bomb.is_caught(self.paddle_x, self.paddle_y):
                caught_bombs.append(bomb)
            elif bomb.is_off_screen():
                off_screen_bombs.append(bomb)
        
        # Process caught bombs
        for bomb in caught_bombs:
            if bomb in self.bombs:  # Check if bomb is still in play
                self.lives = max(0, self.lives - 1)
                self.bombs.remove(bomb)
                if self.lives <= 0:
                    self.game_over = True
                    self.save_score()  # Save score immediately when game ends
        
        # Remove off-screen bombs
        for bomb in off_screen_bombs:
            if bomb in self.bombs:  # Check if bomb is still in play
                self.bombs.remove(bomb)
        
        # Spawn new balls
        self.ball_spawn_timer += 1
        if self.ball_spawn_timer >= self.ball_spawn_delay:
            self.balls.append(Ball())
            self.ball_spawn_timer = 0
            # Make the game harder as the score increases
            self.ball_spawn_delay = max(15, 60 - (self.score // 5) * 5)
        
        # Spawn new bombs
        self.bomb_spawn_timer += 1
        if self.bomb_spawn_timer >= self.bomb_spawn_delay:
            self.bombs.append(Bomb())
            self.bomb_spawn_timer = 0
            # Increase bomb frequency as score increases
            self.bomb_spawn_delay = max(60, 180 - (self.score // 10) * 15)