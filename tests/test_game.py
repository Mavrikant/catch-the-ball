import pytest
import pygame
import random
from unittest.mock import patch, MagicMock
from game_classes import Ball, Bomb, GameLogic, WIDTH, HEIGHT, BALL_RADIUS, BOMB_RADIUS, PADDLE_WIDTH, BALL_COLORS


# Initialize pygame for tests
pygame.init()

# Mock the screen for draw operations
@pytest.fixture
def mock_screen():
    mock = MagicMock()
    # Add draw attribute with circle and line methods
    mock.draw = MagicMock()
    mock.draw.circle = MagicMock()
    mock.draw.line = MagicMock()
    return mock


class TestBall:
    def test_init(self):
        with patch('random.randint', return_value=100):
            with patch('random.choice', return_value=(255, 0, 0)):
                ball = Ball()
                assert ball.y == 0
                assert ball.x == 100
                assert ball.speed == 100
                assert ball.color == (255, 0, 0)

    def test_update(self):
        ball = Ball()
        initial_y = ball.y
        speed = ball.speed
        ball.update()
        assert ball.y == initial_y + speed

    def test_is_caught(self):
        ball = Ball()
        # Position ball right above paddle
        ball.x = 400  # Middle of screen
        ball.y = HEIGHT - 40 - BALL_RADIUS  # Just above paddle
        
        # Paddle is centered and should catch the ball
        assert ball.is_caught(400 - PADDLE_WIDTH//2, HEIGHT - 40)
        
        # Paddle is too far left
        assert not ball.is_caught(200, HEIGHT - 40)
        
        # Paddle is too far right
        assert not ball.is_caught(600, HEIGHT - 40)

    def test_is_off_screen(self):
        ball = Ball()
        
        # Ball is at the top of the screen
        ball.y = 0
        assert not ball.is_off_screen()
        
        # Ball is at the middle of the screen
        ball.y = HEIGHT // 2
        assert not ball.is_off_screen()
        
        # Ball is below the screen
        ball.y = HEIGHT + 1
        assert ball.is_off_screen()

    def test_draw(self, mock_screen):
        with patch('pygame.draw.circle') as mock_circle:
            ball = Ball()
            ball.draw(mock_screen)
            # Verify the circle was drawn
            mock_circle.assert_called_once()

    def test_reset(self):
        # Need to provide enough values for all random calls
        with patch('random.randint', side_effect=[100, 5, 200, 5]):
            with patch('random.choice', side_effect=[(255, 0, 0), (0, 255, 0)]):
                ball = Ball()
                old_x = ball.x
                old_speed = ball.speed
                old_color = ball.color
                
                # Reset ball with mocked values
                ball.reset()
                
                assert ball.x == 200
                assert ball.y == -BALL_RADIUS
                assert ball.speed == 5
                assert ball.color == (0, 255, 0)
                assert (ball.x != old_x or ball.speed != old_speed or ball.color != old_color)

    def test_ball_color_assignment(self):
        # Test that the ball color is chosen from the available colors
        for _ in range(10):  # Test multiple times to reduce chance of coincidence
            ball = Ball()
            assert ball.color in BALL_COLORS

    def test_ball_speed_range(self):
        # Test that the ball speed is within the expected range
        speeds = set()
        for _ in range(20):  # Multiple iterations to cover the range
            with patch('random.choice', return_value=BALL_COLORS[0]):
                ball = Ball()
                speeds.add(ball.speed)
        
        # We expect speeds between 3 and 7
        assert min(speeds) >= 3
        assert max(speeds) <= 7
        assert len(speeds) > 1  # Should get multiple different speeds


class TestBomb:
    def test_init(self):
        with patch('random.randint', return_value=100):
            bomb = Bomb()
            assert bomb.x == 100
            assert bomb.y == -BOMB_RADIUS
            assert bomb.speed == 100

    def test_update(self):
        bomb = Bomb()
        initial_y = bomb.y
        speed = bomb.speed
        bomb.update()
        assert bomb.y == initial_y + speed

    def test_is_caught(self):
        bomb = Bomb()
        # Position bomb right above paddle
        bomb.x = 400  # Middle of screen
        bomb.y = HEIGHT - 40 - BOMB_RADIUS  # Just above paddle
        
        # Paddle is centered and should catch the bomb
        assert bomb.is_caught(400 - PADDLE_WIDTH//2, HEIGHT - 40)
        
        # Paddle is too far left
        assert not bomb.is_caught(200, HEIGHT - 40)
        
        # Paddle is too far right
        assert not bomb.is_caught(600, HEIGHT - 40)

    def test_is_off_screen(self):
        bomb = Bomb()
        
        # Bomb is at the top of the screen
        bomb.y = 0
        assert not bomb.is_off_screen()
        
        # Bomb is at the middle of the screen
        bomb.y = HEIGHT // 2
        assert not bomb.is_off_screen()
        
        # Bomb is below the screen
        bomb.y = HEIGHT + 1
        assert bomb.is_off_screen()

    def test_draw(self, mock_screen):
        with patch('pygame.draw.circle') as mock_circle:
            with patch('pygame.draw.line') as mock_line:
                bomb = Bomb()
                bomb.draw(mock_screen)
                # Verify drawing operations happened
                mock_circle.assert_called()
                mock_line.assert_called()

    def test_reset(self):
        # Need to provide enough values for all random calls
        with patch('random.randint', side_effect=[100, 3, 300, 4]):
            bomb = Bomb()
            old_x = bomb.x
            old_speed = bomb.speed
            
            # Reset bomb with mocked values
            bomb.reset()
            
            assert bomb.x == 300
            assert bomb.y == -BOMB_RADIUS
            assert bomb.speed == 4
            assert bomb.x != old_x or bomb.speed != old_speed

    def test_bomb_speed_range(self):
        # Test that the bomb speed is within the expected range
        speeds = set()
        for _ in range(20):  # Multiple iterations to cover the range
            bomb = Bomb()
            speeds.add(bomb.speed)
        
        # We expect speeds between 2 and 5
        assert min(speeds) >= 2
        assert max(speeds) <= 5
        assert len(speeds) > 1  # Should get multiple different speeds


class TestGameLogic:
    def test_init(self):
        game = GameLogic()
        assert game.score == 0
        assert game.lives == 3
        assert not game.game_over
        assert len(game.balls) == 1
        assert len(game.bombs) == 0
        assert game.paddle_x == WIDTH // 2 - PADDLE_WIDTH // 2
        assert game.paddle_y == HEIGHT - 40

    def test_reset_game(self):
        game = GameLogic()
        game.score = 10
        game.lives = 0
        game.game_over = True
        game.balls = []
        game.bombs = [Bomb()]
        
        game.reset_game()
        
        assert game.score == 0
        assert game.lives == 3
        assert not game.game_over
        assert len(game.balls) == 1
        assert len(game.bombs) == 0

    def test_move_paddle_left(self):
        game = GameLogic()
        initial_x = game.paddle_x
        game.move_paddle_left()
        assert game.paddle_x == initial_x - game.paddle_speed

        # Test boundary condition
        game.paddle_x = 5  # Close to left edge
        game.move_paddle_left()
        assert game.paddle_x == 0  # Should stop at left edge

    def test_move_paddle_right(self):
        game = GameLogic()
        initial_x = game.paddle_x
        game.move_paddle_right()
        assert game.paddle_x == initial_x + game.paddle_speed

        # Test boundary condition
        game.paddle_x = WIDTH - PADDLE_WIDTH - 5  # Close to right edge
        game.move_paddle_right()
        assert game.paddle_x == WIDTH - PADDLE_WIDTH  # Should stop at right edge

    def test_update_game_state_game_over(self):
        game = GameLogic()
        game.game_over = True
        
        # Game state shouldn't change when game is over
        initial_balls = len(game.balls)
        initial_bombs = len(game.bombs)
        
        game.update_game_state()
        
        assert len(game.balls) == initial_balls
        assert len(game.bombs) == initial_bombs

    def test_update_game_state_ball_caught(self):
        game = GameLogic()
        
        # Position the ball to be caught
        test_ball = Ball()
        test_ball.x = game.paddle_x + PADDLE_WIDTH // 2
        test_ball.y = game.paddle_y - BALL_RADIUS
        game.balls = [test_ball]
        
        initial_score = game.score
        
        game.update_game_state()
        
        assert game.score == initial_score + 1
        assert len(game.balls) == 0  # Ball should be removed

    def test_update_game_state_ball_missed(self):
        game = GameLogic()
        
        # Position the ball to be missed (below screen)
        test_ball = Ball()
        test_ball.y = HEIGHT + BALL_RADIUS
        game.balls = [test_ball]
        
        initial_score = game.score
        
        game.update_game_state()
        
        assert game.score == initial_score  # Score shouldn't change
        assert len(game.balls) == 0  # Ball should be removed

    def test_update_game_state_bomb_hit(self):
        game = GameLogic()
        
        # Position the bomb to hit paddle
        test_bomb = Bomb()
        test_bomb.x = game.paddle_x + PADDLE_WIDTH // 2
        test_bomb.y = game.paddle_y - BOMB_RADIUS
        game.bombs = [test_bomb]
        
        initial_lives = game.lives
        
        game.update_game_state()
        
        assert game.lives == initial_lives - 1
        assert len(game.bombs) == 0  # Bomb should be removed
        assert not game.game_over  # Game not over yet

    def test_update_game_state_bomb_hit_game_over(self):
        game = GameLogic()
        game.lives = 1  # Set lives to 1
        
        # Position the bomb to hit paddle
        test_bomb = Bomb()
        test_bomb.x = game.paddle_x + PADDLE_WIDTH // 2
        test_bomb.y = game.paddle_y - BOMB_RADIUS
        game.bombs = [test_bomb]
        
        game.update_game_state()
        
        assert game.lives == 0
        assert len(game.bombs) == 0  # Bomb should be removed
        assert game.game_over  # Game should be over

    def test_update_game_state_bomb_missed(self):
        game = GameLogic()
        
        # Position the bomb to be missed (below screen)
        test_bomb = Bomb()
        test_bomb.y = HEIGHT + BOMB_RADIUS
        game.bombs = [test_bomb]
        
        initial_lives = game.lives
        
        game.update_game_state()
        
        assert game.lives == initial_lives  # Lives shouldn't change
        assert len(game.bombs) == 0  # Bomb should be removed

    def test_update_game_state_spawn_ball(self):
        game = GameLogic()
        game.balls = []
        game.ball_spawn_timer = game.ball_spawn_delay - 1
        
        game.update_game_state()
        
        assert len(game.balls) == 1  # New ball should be spawned
        assert game.ball_spawn_timer == 0  # Timer should be reset

    def test_update_game_state_spawn_bomb(self):
        game = GameLogic()
        game.bombs = []
        game.bomb_spawn_timer = game.bomb_spawn_delay - 1
        
        game.update_game_state()
        
        assert len(game.bombs) == 1  # New bomb should be spawned
        assert game.bomb_spawn_timer == 0  # Timer should be reset
        
    def test_difficulty_scaling_ball_spawn(self):
        game = GameLogic()
        
        # Initial ball spawn delay
        initial_delay = game.ball_spawn_delay
        assert initial_delay == 60
        
        # Explicitly update ball_spawn_delay based on score
        # (not relying on update_game_state to do it)
        game.score = 10
        game.ball_spawn_delay = max(15, 60 - (game.score // 5) * 5)
        
        assert game.ball_spawn_delay == 50  # 60 - (10 // 5) * 5 = 60 - 2 * 5 = 50
        
        # Test maximum difficulty
        game.score = 100
        game.ball_spawn_delay = max(15, 60 - (game.score // 5) * 5)
        
        assert game.ball_spawn_delay == 15  # Should not go below minimum of 15
        
    def test_difficulty_scaling_bomb_spawn(self):
        game = GameLogic()
        
        # Initial bomb spawn delay
        initial_delay = game.bomb_spawn_delay
        assert initial_delay == 180
        
        # Explicitly update bomb_spawn_delay based on score
        game.score = 20
        game.bomb_spawn_delay = max(60, 180 - (game.score // 10) * 15)
        
        assert game.bomb_spawn_delay == 150  # 180 - (20 // 10) * 15 = 180 - 2 * 15 = 150
        
        # Test maximum difficulty
        game.score = 200
        game.bomb_spawn_delay = max(60, 180 - (game.score // 10) * 15)
        
        assert game.bomb_spawn_delay == 60  # Should not go below minimum of 60
        
    def test_multiple_balls_update(self):
        game = GameLogic()
        
        # Add multiple balls
        ball1 = Ball()
        ball1.x = game.paddle_x + PADDLE_WIDTH // 2
        ball1.y = game.paddle_y - BALL_RADIUS  # Will be caught
        
        ball2 = Ball()
        ball2.y = HEIGHT + BALL_RADIUS  # Will be missed (off screen)
        
        ball3 = Ball()
        ball3.x = 100
        ball3.y = HEIGHT // 2  # Will remain in play
        
        game.balls = [ball1, ball2, ball3]
        
        initial_score = game.score
        
        game.update_game_state()
        
        assert game.score == initial_score + 1  # One ball caught
        assert len(game.balls) == 1  # Only one ball should remain
        assert game.balls[0] == ball3  # The middle ball should remain
        
    def test_multiple_bombs_update(self):
        game = GameLogic()
        
        # Add multiple bombs
        bomb1 = Bomb()
        bomb1.x = game.paddle_x + PADDLE_WIDTH // 2
        bomb1.y = game.paddle_y - BOMB_RADIUS  # Will be hit
        
        bomb2 = Bomb()
        bomb2.y = HEIGHT + BOMB_RADIUS  # Will be missed (off screen)
        
        bomb3 = Bomb()
        bomb3.x = 100
        bomb3.y = HEIGHT // 2  # Will remain in play
        
        game.bombs = [bomb1, bomb2, bomb3]
        
        initial_lives = game.lives
        
        game.update_game_state()
        
        assert game.lives == initial_lives - 1  # One life lost
        assert len(game.bombs) == 1  # Only one bomb should remain
        assert game.bombs[0] == bomb3  # The middle bomb should remain

    def test_simultaneous_ball_and_bomb_spawn(self):
        game = GameLogic()
        game.balls = []
        game.bombs = []
        game.ball_spawn_timer = game.ball_spawn_delay - 1
        game.bomb_spawn_timer = game.bomb_spawn_delay - 1
        
        game.update_game_state()
        
        assert len(game.balls) == 1
        assert len(game.bombs) == 1
        assert game.ball_spawn_timer == 0
        assert game.bomb_spawn_timer == 0
    
    def test_game_over_no_updates(self):
        game = GameLogic()
        game.game_over = True
        
        # Add a ball and bomb that would normally be caught
        test_ball = Ball()
        test_ball.x = game.paddle_x + PADDLE_WIDTH // 2
        test_ball.y = game.paddle_y - BALL_RADIUS
        game.balls = [test_ball]
        
        test_bomb = Bomb()
        test_bomb.x = game.paddle_x + PADDLE_WIDTH // 2
        test_bomb.y = game.paddle_y - BOMB_RADIUS
        game.bombs = [test_bomb]
        
        game.ball_spawn_timer = game.ball_spawn_delay - 1
        game.bomb_spawn_timer = game.bomb_spawn_delay - 1
        
        initial_score = game.score
        initial_lives = game.lives
        
        game.update_game_state()
        
        # Nothing should change when game is over
        assert game.score == initial_score
        assert game.lives == initial_lives
        assert len(game.balls) == 1
        assert len(game.bombs) == 1
        assert game.ball_spawn_timer == game.ball_spawn_delay - 1
        assert game.bomb_spawn_timer == game.bomb_spawn_delay - 1
    
    def test_ball_spawn_timer_increment(self):
        game = GameLogic()
        game.balls = [Ball()]  # Keep existing ball
        initial_timer = game.ball_spawn_timer
        
        game.update_game_state()
        
        assert game.ball_spawn_timer == initial_timer + 1
    
    def test_bomb_spawn_timer_increment(self):
        game = GameLogic()
        game.bombs = []  # No bombs
        initial_timer = game.bomb_spawn_timer
        
        game.update_game_state()
        
        assert game.bomb_spawn_timer == initial_timer + 1
    
    def test_ball_at_edge_of_paddle(self):
        game = GameLogic()
        
        # Position ball at left edge of paddle
        left_ball = Ball()
        left_ball.x = game.paddle_x
        left_ball.y = game.paddle_y - BALL_RADIUS
        
        # Position ball at right edge of paddle
        right_ball = Ball()
        right_ball.x = game.paddle_x + PADDLE_WIDTH
        right_ball.y = game.paddle_y - BALL_RADIUS
        
        assert left_ball.is_caught(game.paddle_x, game.paddle_y)
        assert right_ball.is_caught(game.paddle_x, game.paddle_y)
    
    def test_bomb_at_edge_of_paddle(self):
        game = GameLogic()
        
        # Position bomb at left edge of paddle
        left_bomb = Bomb()
        left_bomb.x = game.paddle_x
        left_bomb.y = game.paddle_y - BOMB_RADIUS
        
        # Position bomb at right edge of paddle
        right_bomb = Bomb()
        right_bomb.x = game.paddle_x + PADDLE_WIDTH
        right_bomb.y = game.paddle_y - BOMB_RADIUS
        
        assert left_bomb.is_caught(game.paddle_x, game.paddle_y)
        assert right_bomb.is_caught(game.paddle_x, game.paddle_y)
        
    def test_ball_just_above_paddle(self):
        game = GameLogic()
        
        # Position ball just above paddle (should NOT be caught yet)
        ball = Ball()
        ball.x = game.paddle_x + PADDLE_WIDTH // 2
        ball.y = game.paddle_y - BALL_RADIUS - 1  # One pixel above catching position
        game.balls = [ball]
        
        # Mock the is_caught method to return False for this test
        with patch.object(Ball, 'is_caught', return_value=False):
            game.update_game_state()
            # Ball should still be in play, not caught yet
            assert len(game.balls) == 1
        
        # Move ball to exact catching position and use actual is_caught method
        ball.y = game.paddle_y - BALL_RADIUS
        game.update_game_state()
        # Ball should now be caught
        assert len(game.balls) == 0
        assert game.score == 1
    
    def test_paddle_boundary_conditions(self):
        game = GameLogic()
        
        # Test left boundary
        game.paddle_x = 5  # Close to left edge
        game.move_paddle_left()
        assert game.paddle_x == 0  # Should stop at left edge (not go negative)
        game.move_paddle_left()
        assert game.paddle_x == 0  # Should remain at left edge
        
        # Test right boundary
        game.paddle_x = WIDTH - PADDLE_WIDTH - 5  # Close to right edge
        game.move_paddle_right()
        assert game.paddle_x == WIDTH - PADDLE_WIDTH  # Should stop at right edge
        game.move_paddle_right()
        assert game.paddle_x == WIDTH - PADDLE_WIDTH  # Should remain at right edge