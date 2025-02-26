import pytest
from unittest.mock import Mock, patch, call
import sys

# Mock pygame and its constants before importing main
with patch.dict('sys.modules', {'pygame': Mock()}):
    import pygame
    # Set up pygame constants that our game uses
    pygame.K_LEFT = 1073741904
    pygame.K_RIGHT = 1073741903
    pygame.K_SPACE = 32
    pygame.QUIT = 256
    pygame.KEYDOWN = 768
    
    # Now import main after pygame is mocked
    from main import main
    from game_classes import RED, WHITE, GameLogic

@pytest.fixture
def mock_pygame():
    with patch('pygame.init') as mock_init, \
         patch('pygame.display.set_mode') as mock_display, \
         patch('pygame.font.Font') as mock_font, \
         patch('pygame.event.get') as mock_events, \
         patch('pygame.key.get_pressed') as mock_keys, \
         patch('pygame.display.flip') as mock_flip, \
         patch('pygame.quit') as mock_quit, \
         patch('pygame.draw.rect') as mock_rect, \
         patch('pygame.time.Clock') as mock_clock, \
         patch('pygame.display.set_caption') as mock_caption:
        
        # Mock display surface
        mock_surface = Mock()
        mock_surface.blit = Mock()
        mock_display.return_value = mock_surface
        
        # Mock font and text rendering
        mock_text_surface = Mock()
        mock_text_surface.get_width = Mock(return_value=100)
        mock_text_surface.get_height = Mock(return_value=30)
        mock_font_obj = Mock()
        mock_font_obj.render = Mock(return_value=mock_text_surface)
        mock_font.return_value = mock_font_obj
        
        # Mock clock
        mock_clock_instance = Mock()
        mock_clock_instance.tick = Mock()
        mock_clock.return_value = mock_clock_instance
        
        # Mock key state
        mock_keys.return_value = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_SPACE: False
        }
        
        yield {
            'init': mock_init,
            'display': mock_display,
            'font': mock_font,
            'events': mock_events,
            'keys': mock_keys,
            'flip': mock_flip,
            'quit': mock_quit,
            'surface': mock_surface,
            'text_surface': mock_text_surface,
            'clock': mock_clock_instance
        }

def test_game_quit(mock_pygame):
    # Simulate quitting the game
    mock_pygame['events'].return_value = [pygame.event.Event(pygame.QUIT)]
    
    with pytest.raises(SystemExit):
        main()
    
    mock_pygame['quit'].assert_called_once()

def test_game_over_restart(mock_pygame):
    with patch('game_classes.GameLogic') as MockGameLogic:
        # Create a mock game instance that's in game over state
        mock_game = Mock()
        mock_game.game_over = True
        mock_game.score = 10
        mock_game.lives = 0
        mock_game.update_game_state = Mock()  # Prevent state updates
        MockGameLogic.return_value = mock_game
        
        # Run the game loop for a few frames
        mock_pygame['events'].side_effect = [
            [],  # First frame: show game over screen
            [pygame.event.Event(pygame.QUIT)]  # Second frame: quit
        ]
        
        # Run the game until it quits
        with pytest.raises(SystemExit):
            main()
        
        # Verify that game over text was rendered
        render_method = mock_pygame['font'].return_value.render
        render_calls = render_method.call_args_list
        render_texts = [args[0] for args, kwargs in render_calls]
        assert any('GAME OVER' in str(text) for text in render_texts), "Game over text was not rendered"
        assert any('Score' in str(text) for text in render_texts), "Score text was not rendered"
        assert any('SPACE' in str(text) for text in render_texts), "Restart instruction was not rendered"

def test_paddle_movement(mock_pygame):
    with patch('game_classes.GameLogic') as MockGameLogic:
        # Create a mock game instance
        mock_game = Mock()
        mock_game.game_over = False
        MockGameLogic.return_value = mock_game
        
        # Set up key state for left movement
        key_state = {
            pygame.K_LEFT: True,
            pygame.K_RIGHT: False,
            pygame.K_SPACE: False
        }
        mock_pygame['keys'].return_value = key_state
        
        # Run one frame then quit
        mock_pygame['events'].return_value = [pygame.event.Event(pygame.QUIT)]
        
        with pytest.raises(SystemExit):
            main()
        
        # Verify paddle movement was called
        mock_game.move_paddle_left.assert_called_once()