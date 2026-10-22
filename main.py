"""
Her Eye — Colored ASCII Cinematic Animation
Main Application

Choreographs the complete 6-scene cinematic sequence inspired by the reference Reel:
1. Scene 1 — Darkness (Pure black, subtle character kindling)
2. Scene 2 — Eye Formation (Progressive character reveal over ~4.5s)
3. Scene 3 — Natural Human Eye Blinking (Realistic eyelid closure & reopening)
4. Scene 4 — Zoom Into Pupil (Smooth cinematic camera flight into pupil center)
5. Scene 5 — Heart Reveal (Pulsing ASCII character heart inside pupil)
6. Scene 6 — Final Message ("You, always you. ❤️", held for 6 seconds)

Controls:
- ESC: Exit animation
- F / F11: Toggle Fullscreen / Windowed
"""

import os
import sys
import time
import cv2
import pygame

from ascii_renderer import ASCIIRenderer
from eye_animation import EyeAnimationManager
from cake_animation import CakeAnimationManager

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Primary source image path (updated to user's given photo)
IMAGE_PATH = "assets/birthday_photo.jpg"

# Fallback paths if primary file is missing
FALLBACK_PATHS = [
    "assets/her_eye.jpg",
    "assets/her_eye.png",
    "assets/her_eye_wide.jpg",
    "../assets/birthday_photo.jpg",
    "../assets/her_eye.jpg"
]

# Focus center position in normalized coords (0.0 to 1.0)
# (0.50, 0.28) targets the smiling baby in the joyful embrace
PUPIL_NORMALIZED_COORDS = (0.50, 0.28)

# Target character density across width (144 columns gives exact 720x960 1080p fit)
GRID_COLUMNS = 144

# Target frame rate
TARGET_FPS = 60

# Fullscreen by default (set to False for fixed window testing)
START_FULLSCREEN = True
FALLBACK_WINDOW_SIZE = (1920, 1080)

# ==============================================================================
# SCENE TIMELINE DEFINITIONS (in cumulative seconds)
# ==============================================================================
T_DARKNESS_END   = 1.4    # Scene 1: Initial darkness & faint kindling
T_REVEAL_END     = 5.9    # Scene 2: Portrait formation completes (4.5s reveal)
T_APPRECIATE_END = 8.0    # Hold open for viewer appreciation (~2.1s)
T_BLINK_END      = 8.20   # Scene 3: Natural portrait appreciation pause
T_POST_BLINK_END = 9.3    # Settle before camera movement (1.1s)
T_ZOOM_END       = 13.5   # Scene 4: Cinematic zoom into smile (4.2s zoom)
T_CAKE_ONLY_END  = 16.0   # Scene 5: Birthday Cake reveal & candle flicker (2.5s)
T_FINAL_END      = 26.0   # Scene 6: 4-line celebratory message held for reading


def find_image_path():
    """Locates the source image from primary or fallback paths."""
    if os.path.exists(IMAGE_PATH):
        return IMAGE_PATH
    for path in FALLBACK_PATHS:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"Image not found at '{IMAGE_PATH}'. Please ensure birthday_photo.jpg is placed in the assets/ directory."
    )


def main():
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Birthday Celebration — Colored ASCII Cinematic Animation ✨")
    
    # Query display resolution
    display_info = pygame.display.Info()
    screen_w = display_info.current_w if display_info.current_w > 0 else FALLBACK_WINDOW_SIZE[0]
    screen_h = display_info.current_h if display_info.current_h > 0 else FALLBACK_WINDOW_SIZE[1]
    
    # Create window
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    if START_FULLSCREEN:
        try:
            screen = pygame.display.set_mode((screen_w, screen_h), flags | pygame.FULLSCREEN)
        except Exception:
            screen = pygame.display.set_mode((min(1920, screen_w), min(1080, screen_h)), flags)
    else:
        screen = pygame.display.set_mode((min(1920, screen_w), min(1080, screen_h)), flags)
        
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    
    # Load and verify image
    image_file = find_image_path()
    print(f"[Loading] Source photograph: {image_file}")
    
    img_bgr = cv2.imread(image_file)
    if img_bgr is None:
        raise ValueError(f"Could not decode image at {image_file}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Initialize animation engines
    print("[Initializing] Colored ASCII renderer (high density, tight spacing)...")
    renderer = ASCIIRenderer(font_name="consolas", font_size=8, bg_tint_ratio=0.45, vertical_overlap=2)
    
    print("[Precomputing] Colored ASCII portrait frames...")
    eye_mgr = EyeAnimationManager(
        renderer=renderer,
        base_img_rgb=img_rgb,
        pupil_pos=PUPIL_NORMALIZED_COORDS,
        target_cols=GRID_COLUMNS
    )
    
    print("[Initializing] Birthday Cake animation manager...")
    cake_mgr = CakeAnimationManager(font_name="consolas", font_size=13)
    
    print("[Ready] Starting cinematic sequence. Press ESC to exit.")
    
    start_time = time.time()
    running = True
    is_fullscreen = START_FULLSCREEN
    
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0
        elapsed = time.time() - start_time
        
        # Handle user events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_f, pygame.K_F11):
                    # Toggle Fullscreen
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((screen_w, screen_h), flags | pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((min(1920, screen_w), min(1080, screen_h)), flags)
                    pygame.mouse.set_visible(False)
                    
        # Clear screen to pure black
        screen.fill((0, 0, 0))
        
        # ======================================================================
        # SCENE CHOREOGRAPHY
        # ======================================================================
        if elapsed < T_DARKNESS_END:
            # ------------------------------------------------------------------
            # SCENE 1: Darkness & Subtle Initial Appearance
            # ------------------------------------------------------------------
            if elapsed > 0.8:
                # Faint characters begin to kindle in the void
                p = (elapsed - 0.8) / (T_DARKNESS_END - 0.8)
                eye_mgr.render_reveal(screen, progress=p * 0.04)
            # Otherwise stay in pure pitch black
            
        elif elapsed < T_REVEAL_END:
            # ------------------------------------------------------------------
            # SCENE 2: Eye Formation
            # ------------------------------------------------------------------
            p = (elapsed - T_DARKNESS_END) / (T_REVEAL_END - T_DARKNESS_END)
            eye_mgr.render_reveal(screen, progress=p)
            
        elif elapsed < T_APPRECIATE_END:
            # Hold the fully assembled eye portrait so viewer can appreciate it
            eye_mgr.render_blink(screen, blink_progress=0.0)
            
        elif elapsed < T_BLINK_END:
            # ------------------------------------------------------------------
            # SCENE 3: Natural Human Eye Blinking
            # ------------------------------------------------------------------
            p = (elapsed - T_APPRECIATE_END) / (T_BLINK_END - T_APPRECIATE_END)
            eye_mgr.render_blink(screen, blink_progress=p)
            
        elif elapsed < T_POST_BLINK_END:
            # Eye remains open naturally before camera starts moving
            eye_mgr.render_blink(screen, blink_progress=0.0)
            
        elif elapsed < T_ZOOM_END:
            # ------------------------------------------------------------------
            # SCENE 4: Zoom Into the Pupil Center
            # ------------------------------------------------------------------
            p = (elapsed - T_POST_BLINK_END) / (T_ZOOM_END - T_POST_BLINK_END)
            eye_mgr.render_zoom(screen, zoom_progress=p)
            
            # Seamless cinematic blend: as zoom plunges into void, birthday cake emerges
            if p > 0.70:
                cake_p = (p - 0.70) / 0.30
                cake_mgr.render_cake(screen, elapsed_time=elapsed, entrance_progress=cake_p * 0.85)
            
        elif elapsed < T_CAKE_ONLY_END:
            # ------------------------------------------------------------------
            # SCENE 5: Birthday Cake Reveal With Flickering Candles
            # ------------------------------------------------------------------
            p = (elapsed - T_ZOOM_END) / (T_CAKE_ONLY_END - T_ZOOM_END)
            # Smoothly transition to 1.0 full entrance
            current_entrance = 0.85 + 0.15 * min(1.0, p * 2.0)
            cake_mgr.render_cake(screen, elapsed_time=elapsed, entrance_progress=current_entrance)
            
        elif elapsed < T_FINAL_END:
            # ------------------------------------------------------------------
            # SCENE 6: Final 4-Line Celebratory Birthday Message
            # ------------------------------------------------------------------
            p = (elapsed - T_CAKE_ONLY_END) / 3.0  # smooth 3.0s cascading fade-in
            msg_fade = min(1.0, p)
            cake_mgr.render_final_message(screen, elapsed_time=elapsed, message_fade=msg_fade, cake_active=True)

            
        else:
            # Sequence complete: hold final message gently
            cake_mgr.render_final_message(screen, elapsed_time=elapsed, message_fade=1.0, cake_active=True)
            # Exit automatically after holding
            if elapsed > T_FINAL_END + 0.5:
                running = False
                
        pygame.display.flip()
        
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
