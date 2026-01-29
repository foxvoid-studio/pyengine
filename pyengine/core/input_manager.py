from sdl2 import *
from pyengine.ecs.resource import Resource


class InputManager(Resource):
    """
    Handles keyboard and mouse input states.
    It tracks keys currently held down and keys pressed/released specifically during the current frame.
    """
    def __init__(self):
        # Dictionary to store the state of keys (True = Held Down, False = Released)
        self._key_states = {}
        
        # Sets to store keys that were pressed or released *this specific frame*
        self._keys_pressed_this_frame = set()
        self._keys_released_this_frame = set()

        # Mouse state
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_wheel_y = 0
        self._mouse_buttons = {}
        self._mouse_buttons_pressed_this_frame = set()

    def update(self) -> None:
        """
        Resets the 'one-shot' events (pressed/released this frame).
        This must be called at the beginning of every game loop iteration.
        """
        self._keys_pressed_this_frame.clear()
        self._keys_released_this_frame.clear()
        self._mouse_buttons_pressed_this_frame.clear()
        self._mouse_wheel_y = 0

    def process_event(self, event) -> None:
        """
        Processes a single SDL event and updates internal state.
        Args:
            event: The SDL_Event to process.
        """
        # --- Keyboard Events ---
        if event.type == SDL_KEYDOWN:
            sym = event.key.keysym.sym
            self._key_states[sym] = True
            
            # If it's not a repeat (holding the key down), mark as pressed this frame
            if not event.key.repeat:
                self._keys_pressed_this_frame.add(sym)

        elif event.type == SDL_KEYUP:
            sym = event.key.keysym.sym
            self._key_states[sym] = False
            self._keys_released_this_frame.add(sym)

        # --- Mouse Events ---
        elif event.type == SDL_MOUSEMOTION:
            self._mouse_x = event.motion.x
            self._mouse_y = event.motion.y

        elif event.type == SDL_MOUSEBUTTONDOWN:
            button = event.button.button
            self._mouse_buttons[button] = True
            self._mouse_buttons_pressed_this_frame.add(button)

        elif event.type == SDL_MOUSEBUTTONUP:
            button = event.button.button
            self._mouse_buttons[button] = False

        elif event.type == SDL_MOUSEWHEEL:
            # event.wheel.y est positif si on pousse la molette (Zoom In)
            # et négatif si on la tire vers soi (Zoom Out)
            self._mouse_wheel_y = event.wheel.y

    # --- Queries ---

    def is_key_down(self, key_code) -> bool:
        """Returns True if the key is currently held down."""
        return self._key_states.get(key_code, False)

    def is_key_pressed(self, key_code) -> bool:
        """Returns True only on the frame the key was pressed."""
        return key_code in self._keys_pressed_this_frame

    def is_key_released(self, key_code) -> bool:
        """Returns True only on the frame the key was released."""
        return key_code in self._keys_released_this_frame

    def get_mouse_position(self) -> tuple[int, int]:
        """Returns the (x, y) coordinates of the mouse."""
        return (self._mouse_x, self._mouse_y)

    def is_mouse_button_down(self, button_code) -> bool:
        """Returns True if the mouse button is held down (e.g., SDL_BUTTON_LEFT)."""
        return self._mouse_buttons.get(button_code, False)
    
    def get_mouse_wheel(self) -> int:
        """Returns the vertical scroll amount for this frame."""
        return self._mouse_wheel_y
    