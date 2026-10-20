"""
Her Eye — Colored ASCII Cinematic Animation
Module: heart_animation.py

Implements:
1. Scene 5 — A classic, romantic heart composed PURELY of thousands of tightly packed
   colored ASCII text characters against a pitch-black background.
   No polygons, no solid fills, no circles.
   The shape features two perfectly curved upper lobes, an elegant deep center cleft,
   and smooth tapered sides converging to a crisp bottom point (matching the reference Reel & ❤️).
2. Scene 6 — Elegant typography message: "You, always you. ❤️"
"""

import math
import numpy as np
import pygame

# Density-ordered ASCII character sets for the heart mosaic
CHARS = ["@", "#", "W", "M", "&", "8", "%", "Q", "B", "0", "O", "*", "+", "x"]

class HeartAnimationManager:
    """
    Renders an unmistakable classic heart composed entirely of individually colored
    text characters, matching the colored character portrait aesthetic of her eye.
    """
    def __init__(self, font_name="consolas", font_size=13):
        pygame.font.init()
        self.char_font = pygame.font.SysFont(font_name, font_size, bold=True)
        if not self.char_font:
            self.char_font = pygame.font.Font(None, font_size)
            
        test_surf = self.char_font.render("M", True, (255, 255, 255))
        self.char_w = max(1, test_surf.get_width())
        self.char_h = max(1, test_surf.get_height())
        
        # Message typography
        self.text_font = pygame.font.SysFont("georgia", 38, bold=True)
        if not self.text_font:
            self.text_font = pygame.font.SysFont("segoeui", 38, bold=True)
        if not self.text_font:
            self.text_font = pygame.font.Font(None, 38)
            
        self.emoji_font = pygame.font.SysFont("segoeuiemoji", 36)
        if not self.emoji_font:
            self.emoji_font = self.text_font
            
        # Grid dimensions for the heart (76 columns x 38 rows)
        self.grid_cols = 76
        self.grid_rows = 38
        self.heart_base_w = self.grid_cols * self.char_w
        self.heart_base_h = self.grid_rows * self.char_h
        
        # Precompute the master colored ASCII heart surface
        self.master_heart_surface = self._precompute_master_ascii_heart()

    def _precompute_master_ascii_heart(self):
        """
        Builds the master colored ASCII heart surface with exact monospace character tiling.
        Features two rounded symmetrical upper lobes, an elegant center cleft,
        and a smooth concave taper down to a sharp V-tip at the bottom.
        """
        surf = pygame.Surface((self.heart_base_w, self.heart_base_h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        
        cx = self.heart_base_w // 2
        cy = self.heart_base_h // 2 + 10
        
        font = self.char_font
        char_w = self.char_w
        char_h = self.char_h
        
        def is_classic_heart(x, y):
            if y > 0.83 or y < -1.02:
                return False
            x_abs = abs(x)
            if y >= 0.20:
                # Upper dual lobes with central cleft
                return (((x_abs - 0.55) / 0.57)**2 + ((y - 0.20) / 0.63)**2) <= 1.0
            else:
                # Lower gracefully tapering body down to sharp V-tip at bottom
                u = (0.20 - y) / 1.22
                x_max = 1.13 * (1.0 - u) * (1.0 + 0.16 * u)
                return x_abs <= x_max

        half_rows = self.grid_rows // 2
        half_cols = self.grid_cols // 2
        
        for r in range(-half_rows, half_rows + 1):
            y = -r / float(half_rows) * 0.95
            for c in range(-half_cols, half_cols + 1):
                x = c / float(half_cols) * 1.18
                if is_classic_heart(x, y):
                    dist = math.sqrt(x*x + (y - 0.2)**2)
                    
                    # Radiant ruby crimson core to glowing rose pink outer characters
                    r_col = 255
                    g_col = int(22 + dist * 90 + (y > 0.40) * 50)
                    b_col = int(62 + dist * 110 + (y > 0.40) * 60)
                    
                    ch_idx = int((abs(c)*7 + abs(r)*5) % len(CHARS))
                    ch = CHARS[ch_idx]
                    
                    char_surf = font.render(ch, True, (r_col, min(255, g_col), min(255, b_col)))
                    px = cx + c * char_w - char_w // 2
                    py = cy + r * char_h - char_h // 2
                    surf.blit(char_surf, (px, py))
                    
        return surf

    def calculate_heartbeat(self, t):
        """
        Calculates silky-smooth anatomical double-peak heartbeat scale and glow factor.
        Cycle period T = 0.95 seconds.
        """
        period = 0.95
        phase = (t % period) / period  # 0.0 to 1.0
        
        # Beat 1 (Systole): contraction around 0.12
        beat1 = math.exp(-((phase - 0.12) / 0.065) ** 2) * 0.11
        # Beat 2 (Diastole): gentle rebound around 0.32
        beat2 = math.exp(-((phase - 0.32) / 0.075) ** 2) * 0.06
        # Gentle respiratory breathing wave
        breathe = math.sin(phase * 2.0 * math.pi) * 0.010
        
        scale = 1.0 + beat1 + beat2 + breathe
        return scale

    def render_heart(self, screen, elapsed_time, entrance_progress=1.0, center_offset_y=-50):
        """
        Scene 5: Renders the classic heart constructed PURELY of colored ASCII characters.
        No polygons, no solid shapes, no circles — pure character mosaic art.
        """
        screen_w, screen_h = screen.get_size()
        cx = screen_w / 2.0
        cy = screen_h / 2.0 + center_offset_y
        
        beat_scale = self.calculate_heartbeat(elapsed_time)
        
        # Smooth entrance easing
        e_p = max(0.0, min(1.0, entrance_progress))
        e_scale = e_p * e_p * (3.0 - 2.0 * e_p)
        total_scale = beat_scale * e_scale
        
        if total_scale <= 0.01:
            return
            
        target_w = int(round(self.heart_base_w * total_scale))
        target_h = int(round(self.heart_base_h * total_scale))
        
        if target_w <= 2 or target_h <= 2:
            return
            
        scaled_heart = pygame.transform.smoothscale(self.master_heart_surface, (target_w, target_h))
        
        if e_scale < 0.99:
            scaled_heart.set_alpha(int(round(255 * e_scale)))
            
        dest_x = int(round(cx - target_w / 2.0))
        dest_y = int(round(cy - target_h / 2.0))
        screen.blit(scaled_heart, (dest_x, dest_y))

    def render_final_message(self, screen, elapsed_time, message_fade=1.0, heart_active=True):
        """
        Scene 6: Renders the ASCII character heart with the 4-line message smoothly cascading in:
        "I am sorry,
        Please, Give me this last chance,
        I want to be with you, 
        Always You!!!"
        """
        screen_w, screen_h = screen.get_size()
        
        # Position heart gracefully above the multiline message
        heart_offset_y = -140
        if heart_active:
            self.render_heart(screen, elapsed_time, entrance_progress=1.0, center_offset_y=heart_offset_y)
            
        if message_fade <= 0.005:
            return
            
        lines = [
            "I am sorry,",
            "Please, Give me this last chance,",
            "I want to be with you,",
            "Always With You!!!"
        ]
        
        # Base y position for the message block
        start_y = int(screen_h / 2.0 + 115)
        line_height = 48
        
        for i, line_text in enumerate(lines):
            # Cascading fade calculation for each line
            start_t = i * 0.22
            end_t = min(1.0, start_t + 0.35)
            
            if message_fade <= start_t:
                fade = 0.0
            elif message_fade >= end_t:
                fade = 1.0
            else:
                p = (message_fade - start_t) / (end_t - start_t)
                fade = p * p * (3.0 - 2.0 * p)
                
            if fade <= 0.005:
                continue
                
            # Emotional emphasis: last line in radiant rose pink, others in soft warm white
            if i == 3:
                # "Always You!!!"
                line_col = (
                    min(255, int(255 * fade)),
                    min(255, int(90 * fade)),
                    min(255, int(145 * fade))
                )
            elif i == 0:
                # "I am sorry,"
                line_col = (
                    min(255, int(255 * fade)),
                    min(255, int(230 * fade)),
                    min(255, int(240 * fade))
                )
            else:
                line_col = (
                    min(255, int(252 * fade)),
                    min(255, int(242 * fade)),
                    min(255, int(248 * fade))
                )
                
            surf_line = self.text_font.render(line_text, True, line_col)
            draw_x = int((screen_w - surf_line.get_width()) / 2.0)
            draw_y = start_y + i * line_height
            
            screen.blit(surf_line, (draw_x, draw_y))

