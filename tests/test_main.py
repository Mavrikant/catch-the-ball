import pytest
from unittest.mock import Mock, patch, call, MagicMock
import sys
import os

# Add project root to sys.path to fix import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock pygame and its constants before importing main
with patch.dict('sys.modules', {'pygame': Mock()}):
    import pygame
    # Set up pygame constants that our game uses
    pygame.K_LEFT = 1073741904
    pygame.K_RIGHT = 1073741903
    pygame.K_SPACE = 32
    pygame.K_RETURN = 13
    pygame.K_BACKSPACE = 8
    pygame.QUIT = 256
    pygame.KEYDOWN = 768
    
    # Create a proper Event class for mocking
    class MockEvent:
        def __init__(self, type, **kwargs):
            self.type = type
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    # Mock event system
    pygame.event = MagicMock()
    pygame.event.Event = MockEvent
    pygame.event.get = MagicMock(return_value=[])
    
    # Now import main after pygame is mocked
    from src.main import main
    from src.game_classes import RED, WHITE, GameLogic

@pytest.fixture
def mock_pygame():
    with patch('pygame.init') as mock_init, \
         patch('pygame.display.set_mode') as mock_display, \
         patch('pygame.font.Font') as mock_font, \
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
            'keys': mock_keys,
            'flip': mock_flip,
            'quit': mock_quit,
            'surface': mock_surface,
            'text_surface': mock_text_surface,
            'clock': mock_clock_instance
        }

def test_game_quit(mock_pygame):
    # Return an event list with a single quit event
    pygame.event.get.return_value = [pygame.event.Event(pygame.QUIT)]
    
    with pytest.raises(SystemExit):
        main()
    
    mock_pygame['quit'].assert_called_once()

def test_game_over_restart(mock_pygame):
    with patch('src.game_classes.GameLogic') as MockGameLogic:
        # Create a mock game instance that's in game over state
        mock_game = Mock()
        mock_game.game_over = True
        mock_game.score = 10
        mock_game.lives = 0
        mock_game.update_game_state = Mock()
        MockGameLogic.return_value = mock_game
        
        # Setup event sequence
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="")
        quit_event = pygame.event.Event(pygame.QUIT)
        pygame.event.get.side_effect = [
            [enter_event],  # Complete name input
            [],  # Game over screen
            [quit_event]  # Quit game
        ]
        
        with pytest.raises(SystemExit):
            main()
        
        render_method = mock_pygame['font'].return_value.render
        render_calls = render_method.call_args_list
        render_texts = [args[0] for args, kwargs in render_calls]
        assert any('GAME OVER' in str(text) for text in render_texts)
        assert any('Score' in str(text) for text in render_texts)
        assert any('SPACE' in str(text) for text in render_texts)

def test_paddle_movement(mock_pygame):
    with patch('src.game_classes.GameLogic') as MockGameLogic:
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
        
        # Setup event sequence
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="")
        quit_event = pygame.event.Event(pygame.QUIT)
        pygame.event.get.side_effect = [
            [enter_event],  # Complete name input
            [quit_event]  # Quit game
        ]
        
        with pytest.raises(SystemExit):
            main()
        
        mock_game.move_paddle_left.assert_called_once()