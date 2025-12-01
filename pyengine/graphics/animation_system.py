from pyengine.ecs.entity_manager import EntityManager
from pyengine.graphics.sprite import SpriteSheet, Animator
from pyengine.core.time_manager import TimeManager

class AnimationSystem:
    def update(self, entity_manager: EntityManager, time_manager: TimeManager):
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
