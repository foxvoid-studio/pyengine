from sdl2 import SDL_GetPerformanceCounter, SDL_GetPerformanceFrequency
from pyengine.ecs.resource import Resource, ResourceManager
from pyengine.ecs.system import System
from pyengine.ecs.plugin import Plugin
from pyengine.ecs.scheduler import SchedulerType
from typing import Optional


class TimeManager(Resource):
    """
    Manages the game loop timing, calculating delta time and FPS.
    """
    def __init__(self):
        # The frequency of the high-resolution counter (ticks per second)
        self._frequency = SDL_GetPerformanceFrequency()

        # The timestamp of the previous frame
        self._last_time = SDL_GetPerformanceCounter()

        # Time elapsed between the last frame and the current frame (in seconds)
        self._delta_time = 0.0

        # A scalar to modify time flow (1.0 = normal, 0.5 = slow motion, 0.0 = pause)
        self.time_scale = 1.0

        # FPS calculation variables
        self._fps_timer = 0.0
        self._frame_count = 0
        self._current_fps = 0

    def update(self) -> None:
        """
        Updates the time values. Must be called once at the start of the game loop.
        """
        current_time = SDL_GetPerformanceCounter()
        
        # Calculate time difference in seconds
        # (Current Ticks - Last Ticks) / Frequency
        dt = (current_time - self._last_time) / self._frequency
        
        self._last_time = current_time

        # Prevent huge delta time in case of lag spike or window drag
        # (Clamping to a maximum of 0.1s ensures physics doesn't explode)
        if dt > 0.1:
            dt = 0.1

        self._delta_time = dt
        
        # Update FPS logic
        self._update_fps(dt)

    def _update_fps(self, dt: float) -> None:
        """
        Accumulates frames and updates the FPS counter every second.
        """
        self._frame_count += 1
        self._fps_timer += dt

        if self._fps_timer >= 1.0:
            self._current_fps = self._frame_count
            self._frame_count = 0
            self._fps_timer -= 1.0

    @property
    def delta_time(self) -> float:
        """
        Returns the time in seconds it took to complete the last frame,
        multiplied by the time_scale.
        Use this for all movement and physics calculations.
        """
        return self._delta_time * self.time_scale

    @property
    def raw_delta_time(self) -> float:
        """
        Returns the unscaled delta time. 
        Use this for UI animations or systems that shouldn't be affected by slow motion.
        """
        return self._delta_time

    @property
    def fps(self) -> int:
        """Returns the calculated Frames Per Second."""
        return self._current_fps
    

class TimeSystem(System):
    def update(self, resources: ResourceManager):
        time_manager: Optional[TimeManager] = resources.get(TimeManager)
        if time_manager:
            time_manager.update()


class TimePlugin(Plugin):
    def build(self, app):
        app.resources.add(TimeManager())
        app.scheduler.add(SchedulerType.Update, TimeSystem())
        