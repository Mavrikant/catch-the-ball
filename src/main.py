import os
import sys
# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pygame
from src.game_classes import Ball, Bomb, GameLogic, WIDTH, HEIGHT, WHITE, BLACK, RED, PADDLE_WIDTH, PADDLE_HEIGHT

# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Ball")
clock = pygame.time.Clock()
FPS = 60

# Initialize fonts
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

def get_player_name():
    name = ""
    input_active = True
    
    while input_active:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15:  # Limit name length
                        name += event.unicode
        
        prompt_text = font.render("Enter your name:", True, WHITE)
        name_text = font.render(name, True, WHITE)
        instruction_text = font.render("Press ENTER when done", True, WHITE)
        
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT//2))
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT//2 + 60))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return name.strip() or "Player"

def show_scoreboard():
    scores = GameLogic.load_scores()
    y_offset = HEIGHT//2 + 20
    
    for i, score in enumerate(scores[:5]):  # Show top 5 scores
        score_text = font.render(f"{i+1}. {score['name']}: {score['score']}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, y_offset))
        y_offset += 40

def main():
    player_name = get_player_name()
    game = GameLogic(player_name)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not game.game_over:  # Save score if game isn't over when quitting
                    game.game_over = True
                    game.save_score()
                running = False
            if event.type == pygame.KEYDOWN:
                if game.game_over and event.key == pygame.K_SPACE:
                    game.reset_game()
        
        if game.game_over:
            screen.fill(BLACK)
            game_over_text = big_font.render("GAME OVER", True, RED)
            score_text = font.render(f"Final Score: {game.score}", True, WHITE)
            restart_text = font.render("Press SPACE to restart", True, WHITE)
            highscores_text = font.render("High Scores:", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 150))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 80))
            screen.blit(highscores_text, (WIDTH//2 - highscores_text.get_width()//2, HEIGHT//2 - 20))
            show_scoreboard()
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT - 100))
            
            pygame.display.flip()
            clock.tick(FPS)
            continue
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game.move_paddle_left()
        if keys[pygame.K_RIGHT]:
            game.move_paddle_right()
        
        game.update_game_state()
        
        screen.fill(BLACK)
        
        pygame.draw.rect(screen, WHITE, (game.paddle_x, game.paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        
        for ball in game.balls:
            ball.draw(screen)
        for bomb in game.bombs:
            bomb.draw(screen)
        
        score_text = font.render(f"Score: {game.score}", True, WHITE)
        lives_text = font.render(f"Lives: {game.lives}", True, RED)
        player_text = font.render(f"Player: {game.player_name}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 120, 10))
        screen.blit(player_text, (WIDTH//2 - player_text.get_width()//2, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()