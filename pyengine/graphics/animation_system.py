from pyengine.ecs.entity_manager import EntityManager
from pyengine.graphics.sprite import SpriteSheet, Animator
from pyengine.core.time_manager import TimeManager
from pyengine.ecs.system import System
from pyengine.ecs.resource import ResourceManager

class Animation2dSystem(System):
    def update(self, resource: ResourceManager):
        entity_manager: EntityManager = resource.get(EntityManager)
        time_manager: TimeManager = resource.get(TimeManager)

        dt = time_manager.delta_time

        for _, (sprite, animator) in entity_manager.get_entities_with(SpriteSheet, Animator):
            if not animator.is_playing or not animator.current_anim_name:
                continue

            # Get animation data: [start, end, duration]
            animation = animator.animations[animator.current_anim_name]

            # Update timer
            animator.timer += dt

            if animator.timer >= animation.frame_duration_in_seconds:
                # Reset timer (keep remainder for smooth playback)
                animator.timer -= animation.frame_duration_in_seconds
                
                # Advance frame
                sprite.current_frame += 1
                
                # Check bounds
                if sprite.current_frame > animation.end_frame:
                    if animator.loop:
                        sprite.current_frame = animation.start_frame
                    else:
                        sprite.current_frame = animation.end_frame
                        animator.is_playing = False
