"""
Birthday Cinematic Animation — Colored ASCII Art
Module: cake_animation.py

Implements:
1. Scene 5 — A magnificent, multi-tiered celebration birthday cake composed PURELY
   of thousands of individually colored ASCII text characters against a pitch-black background.
   Features:
   - 5 tall, colorful birthday candles with dynamically flickering ASCII flames
   - Scalloped creamy frosting with glazed cherries and sugar pearls
   - Multi-tiered sponge cake layers with candy sprinkles and decorative ribbons
   - Shimmering golden cake stand and footed pedestal
   - Twinkling celebratory sparkles and confetti drifting around the cake
2. Scene 6 — Heartfelt birthday message cascading in with glowing typography.
"""

import math
import pygame

# Character density sets for cake textures
CAKE_CHARS = ["@", "#", "W", "M", "&", "8", "%", "Q", "B", "0", "O", "*", "+", "x"]

# 5 Colorful Birthday Candles (columns in 80-col grid)
CANDLE_COLS = [28, 34, 40, 46, 52]
CANDLE_COLORS = [
    (0, 229, 255),    # Cyan
    (255, 64, 129),   # Rose Pink
    (255, 214, 0),    # Golden Yellow (Tallest Center Candle)
    (105, 240, 174),  # Mint Lime
    (224, 64, 251),   # Lavender Violet
]

# Sparkles drifting around the cake
SPARKLES = [
    (8, 6, '*'), (14, 12, '+'), (70, 8, '*'), (65, 14, '+'),
    (10, 24, '.'), (72, 22, '.'), (6, 32, '*'), (74, 30, '+'),
    (18, 4, '.'), (62, 5, '.'), (22, 10, '+'), (58, 9, '*')
]

# Default 4-line celebratory birthday message
DEFAULT_BIRTHDAY_LINES = [
    "Happy Birthday!",
    "to my sweetest sister! ❤️🎂,",
    "Keep smiling and shining forever,",
    "because you deserve all the beautiful",
    "things in this world! ✨💕",
    "Happy Birthday! 🎂✨"
]


class CakeAnimationManager:
    """
    Renders an unmistakable, glowing ASCII birthday cake composed of individually
    colored text characters, complete with animated flickering candle flames,
    celebratory sparkles, and elegant typography.
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
        self.text_font = pygame.font.SysFont("georgia", 36, bold=True)
        if not self.text_font:
            self.text_font = pygame.font.SysFont("segoeui", 36, bold=True)
        if not self.text_font:
            self.text_font = pygame.font.Font(None, 36)
            
        self.emoji_font = pygame.font.SysFont("segoeuiemoji", 34)
        if not self.emoji_font:
            self.emoji_font = self.text_font
            
        # Grid dimensions for the birthday cake (80 columns x 44 rows)
        self.grid_cols = 80
        self.grid_rows = 44
        self.cake_base_w = self.grid_cols * self.char_w
        self.cake_base_h = self.grid_rows * self.char_h
        
        # Precompute static cake body surface (tiers, stand, candles)
        # Animated elements (flames, sparkles, gentle pulse) are rendered dynamically
        self.static_cake_surface = self._precompute_static_cake()

    def _precompute_static_cake(self):
        """
        Builds the static colored ASCII cake surface with monospace character tiling:
        Tiers, frosting ruffles, cherry accents, sprinkles, and golden pedestal.
        """
        surf = pygame.Surface((self.cake_base_w, self.cake_base_h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        
        font = self.char_font
        char_w = self.char_w
        char_h = self.char_h
        
        # 1. Candle Bodies (Rows 7 to 11) & Wicks (Row 6)
        for c_idx, c_col in enumerate(CANDLE_COLS):
            c_color = CANDLE_COLORS[c_idx]
            for r in range(7, 12):
                ch = '|' if (r + c_idx) % 2 == 0 else 'I'
                wax_col = (
                    min(255, c_color[0] + 40),
                    min(255, c_color[1] + 40),
                    min(255, c_color[2] + 40)
                ) if (r % 2 == 0) else c_color
                csurf = font.render(ch, True, wax_col)
                surf.blit(csurf, (c_col * char_w, r * char_h))
                
            wick_surf = font.render("'", True, (90, 80, 80))
            surf.blit(wick_surf, (c_col * char_w, 6 * char_h))

        # 2. Top Tier (width: cols 24 to 56 = 33 cols wide)
        # Row 12: Frosting top border with ruby cherries
        for c in range(24, 57):
            is_cherry = (c in [25, 32, 40, 48, 55])
            if is_cherry:
                ch = '@'
                col = (255, 23, 68)  # Cherry Red
            elif c % 2 == 0:
                ch = 'o'
                col = (255, 240, 245) # Whipped cream
            else:
                ch = '~'
                col = (255, 182, 193) # Pastel strawberry frosting
            csurf = font.render(ch, True, col)
            surf.blit(csurf, (c * char_w, 12 * char_h))
            
        # Row 13-14: Scalloped Frosting Drips
        for r in range(13, 15):
            for c in range(24, 57):
                drip = (c % 4 == (r % 2) * 2)
                ch = 'U' if drip else '#'
                col = (255, 220, 230) if drip else (255, 245, 250)
                csurf = font.render(ch, True, col)
                surf.blit(csurf, (c * char_w, r * char_h))
                
        # Row 15-19: Top Tier Sponge Cake Body
        top_chars = ["M", "W", "#", "%", "8", "&", "B"]
        for r in range(15, 20):
            for c in range(24, 57):
                dist_edge = min(c - 24, 56 - c)
                if dist_edge == 0:
                    ch = '|'
                    col = (240, 98, 146)
                elif r == 17:
                    ch = '='
                    col = (255, 64, 129)
                else:
                    ch_idx = (c * 7 + r * 5) % len(top_chars)
                    ch = top_chars[ch_idx]
                    shade = 0.85 + 0.15 * math.sin(c * 0.4)
                    col = (
                        int(255 * shade),
                        int(170 * shade),
                        int(190 * shade)
                    )
                csurf = font.render(ch, True, col)
                surf.blit(csurf, (c * char_w, r * char_h))

        # 3. Middle Tier (width: cols 16 to 64 = 49 cols wide)
        # Row 20: Frosting shelf transition
        for c in range(16, 65):
            if c in [17, 23, 31, 40, 49, 57, 63]:
                ch = '*'
                col = (255, 215, 0) # Gold sugar star
            else:
                ch = 'O' if c % 3 == 0 else '~'
                col = (255, 255, 240) # Ivory cream
            csurf = font.render(ch, True, col)
            surf.blit(csurf, (c * char_w, 20 * char_h))
            
        # Row 21-22: Middle Tier Frosting Ruffles & Sprinkles
        sprinkle_colors = [
            (0, 229, 255), (255, 64, 129), (255, 214, 0), (118, 255, 3), (255, 145, 0)
        ]
        for r in range(21, 23):
            for c in range(16, 65):
                is_sprinkle = (c * 3 + r * 7) % 11 == 0
                if is_sprinkle:
                    ch = '+'
                    col = sprinkle_colors[(c + r) % len(sprinkle_colors)]
                else:
                    ch = 'w' if (c % 2 == 0) else 'm'
                    col = (255, 240, 245)
                csurf = font.render(ch, True, col)
                surf.blit(csurf, (c * char_w, r * char_h))

        # Row 23-28: Middle Tier Sponge Cake Body
        mid_chars = ["@", "#", "8", "%", "&", "Q", "0"]
        for r in range(23, 29):
            for c in range(16, 65):
                dist_edge = min(c - 16, 64 - c)
                if dist_edge == 0:
                    ch = '|'
                    col = (141, 110, 99)
                elif r == 25:
                    ch = '*' if c % 4 == 0 else '='
                    col = (255, 215, 0) if c % 4 == 0 else (109, 76, 65)
                elif r == 26:
                    ch = '~'
                    col = (233, 30, 99)
                else:
                    ch_idx = (c * 9 + r * 11) % len(mid_chars)
                    ch = mid_chars[ch_idx]
                    shade = 0.8 + 0.2 * math.cos(c * 0.35 + r * 0.2)
                    col = (
                        int(210 * shade),
                        int(145 * shade),
                        int(105 * shade)
                    )
                csurf = font.render(ch, True, col)
                surf.blit(csurf, (c * char_w, r * char_h))

        # 4. Base Tier (width: cols 8 to 72 = 65 cols wide)
        # Row 29: Shelf border
        for c in range(8, 73):
            if c in [9, 15, 22, 30, 40, 50, 58, 65, 71]:
                ch = '@'
                col = (255, 23, 68) # Ruby sugar berries
            else:
                ch = 'v' if c % 2 == 0 else '~'
                col = (255, 248, 225)
            csurf = font.render(ch, True, col)
            surf.blit(csurf, (c * char_w, 29 * char_h))

        # Row 30-31: Base Frosting Festoons
        for r in range(30, 32):
            for c in range(8, 73):
                is_pearl = (c % 5 == 0)
                if is_pearl:
                    ch = 'o'
                    col = (255, 215, 0) # Gold sugar pearls
                else:
                    ch = 'S' if (c % 2 == 0) else 'C'
                    col = (255, 235, 238)
                csurf = font.render(ch, True, col)
                surf.blit(csurf, (c * char_w, r * char_h))

        # Row 32-37: Base Tier Grand Celebration Sponge Body
        base_chars = ["@", "#", "W", "M", "8", "B", "%", "&"]
        for r in range(32, 38):
            for c in range(8, 73):
                dist_edge = min(c - 8, 72 - c)
                if dist_edge == 0:
                    ch = '|'
                    col = (255, 179, 0)
                elif r == 34:
                    ch = '*' if c % 3 == 0 else '-'
                    col = (255, 235, 59) if c % 3 == 0 else (255, 64, 129)
                elif r == 35:
                    ch = '~'
                    col = (244, 143, 177)
                else:
                    ch_idx = (c * 13 + r * 7) % len(base_chars)
                    ch = base_chars[ch_idx]
                    shade = 0.85 + 0.15 * math.sin(c * 0.25)
                    col = (
                        int(255 * shade),
                        int(190 * shade),
                        int(130 * shade)
                    )
                csurf = font.render(ch, True, col)
                surf.blit(csurf, (c * char_w, r * char_h))

        # 5. Cake Stand / Pedestal Platter
        # Row 38-39: Platter Rim (width: cols 4 to 76 = 73 cols wide)
        for c in range(4, 77):
            gold_shade = 0.8 + 0.2 * math.cos((c - 40) * 0.1)
            col = (
                int(255 * gold_shade),
                int(215 * gold_shade),
                int(0)
            )
            csurf = font.render('=', True, col)
            surf.blit(csurf, (c * char_w, 38 * char_h))
            csurf2 = font.render('*' if c % 4 == 0 else '-', True, (255, 236, 179))
            surf.blit(csurf2, (c * char_w, 39 * char_h))

        # Row 40-42: Pedestal Base
        for r in range(40, 43):
            if r == 40:
                c_start, c_end = 32, 48
            elif r == 41:
                c_start, c_end = 30, 50
            else:
                c_start, c_end = 22, 58
                
            for c in range(c_start, c_end + 1):
                if c == c_start:
                    ch = '/'
                elif c == c_end:
                    ch = '\\'
                elif r == 42:
                    ch = '='
                else:
                    ch = '|' if c % 3 == 0 else ':'
                col = (
                    int(235 + 20 * math.sin(c * 0.3)),
                    int(190 + 30 * math.sin(c * 0.3)),
                    60
                )
                csurf = font.render(ch, True, col)
                surf.blit(csurf, (c * char_w, r * char_h))
                
        return surf

    def calculate_celebration_pulse(self, t):
        """
        Calculates gentle celebration breathing scale.
        """
        breathe = math.sin(t * 2.2) * 0.02
        return 1.0 + breathe

    def render_cake(self, screen, elapsed_time, entrance_progress=1.0, center_offset_y=-50):
        """
        Scene 5: Renders the complete ASCII birthday cake with real-time flickering flames,
        twinkling celebration sparkles, and smooth entrance easing.
        """
        screen_w, screen_h = screen.get_size()
        cx = screen_w / 2.0
        cy = screen_h / 2.0 + center_offset_y
        
        pulse_scale = self.calculate_celebration_pulse(elapsed_time)
        e_p = max(0.0, min(1.0, entrance_progress))
        e_scale = e_p * e_p * (3.0 - 2.0 * e_p)
        total_scale = pulse_scale * e_scale
        
        if total_scale <= 0.01:
            return
            
        target_w = int(round(self.cake_base_w * total_scale))
        target_h = int(round(self.cake_base_h * total_scale))
        
        if target_w <= 2 or target_h <= 2:
            return

        # Frame surface with dynamic flames and sparkles blitted on top of static cake
        frame_surf = self.static_cake_surface.copy()
        font = self.char_font
        char_w = self.char_w
        char_h = self.char_h
        
        # 1. Render Sparkles
        for idx, (sc, sr, sch) in enumerate(SPARKLES):
            twinkle = 0.5 + 0.5 * math.sin(elapsed_time * 4.5 + idx * 1.3)
            if twinkle > 0.25:
                sp_color = (
                    int(255 * twinkle),
                    int(min(255, 220 + 35 * math.sin(idx))),
                    int(min(255, 180 + 75 * math.cos(idx)))
                )
                csurf = font.render(sch, True, sp_color)
                frame_surf.blit(csurf, (sc * char_w, sr * char_h))
                
        # 2. Render Real-Time Animated Candle Flames
        for c_idx, c_col in enumerate(CANDLE_COLS):
            flicker = math.sin(elapsed_time * 12.0 + c_idx * 1.9) * 0.4 + math.sin(elapsed_time * 23.0 + c_idx * 0.7) * 0.2
            flame_shift_x = flicker * (char_w * 0.35)
            
            # Row 5: Flame base (bright orange-red)
            base_flame = font.render('^', True, (255, 87, 34))
            frame_surf.blit(base_flame, (c_col * char_w + flame_shift_x, 5 * char_h))
            
            # Row 4: Flame core (golden amber)
            core_char = '(' if flicker > 0 else ')'
            core_flame = font.render(core_char, True, (255, 193, 7))
            frame_surf.blit(core_flame, (c_col * char_w + flame_shift_x * 0.8, 4 * char_h))
            
            # Row 3: Bright flame tip (brilliant luminous yellow)
            tip_char = '*' if abs(flicker) < 0.2 else '^'
            tip_flame = font.render(tip_char, True, (255, 245, 157))
            frame_surf.blit(tip_flame, (c_col * char_w + flame_shift_x * 1.2, 3 * char_h))
            
            # Row 2: Flame spark (occasional spark)
            if math.sin(elapsed_time * 8.0 + c_idx) > 0.3:
                spark_flame = font.render('.', True, (255, 238, 88))
                frame_surf.blit(spark_flame, (c_col * char_w + flame_shift_x * 1.5, 2 * char_h))

        # Scale cake to target size
        scaled_cake = pygame.transform.smoothscale(frame_surf, (target_w, target_h))
        
        if e_scale < 0.99:
            scaled_cake.set_alpha(int(round(255 * e_scale)))
            
        dest_x = int(round(cx - target_w / 2.0))
        dest_y = int(round(cy - target_h / 2.0))
        screen.blit(scaled_cake, (dest_x, dest_y))

    # Backward compatibility alias
    render_heart = render_cake

    def render_final_message(self, screen, elapsed_time, message_fade=1.0, heart_active=True, cake_active=True, custom_lines=None):
        """
        Scene 6: Renders the ASCII birthday cake with the 4-line celebratory message smoothly cascading in.
        """
        screen_w, screen_h = screen.get_size()
        
        # Position cake gracefully above the multiline message
        cake_offset_y = -165
        if cake_active or heart_active:
            self.render_cake(screen, elapsed_time, entrance_progress=1.0, center_offset_y=cake_offset_y)
            
        if message_fade <= 0.005:
            return
            
        lines = custom_lines if custom_lines else DEFAULT_BIRTHDAY_LINES
        
        # Base y position for the message block
        start_y = int(screen_h / 2.0 + 120)
        line_height = 48
        
        for i, line_text in enumerate(lines):
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
                
            # Line coloring:
            # First and last lines in festive luminous gold and radiant rose,
            # middle lines in elegant warm white
            if i == 0:
                # "Happy Birthday!" in golden celebration amber
                line_col = (
                    min(255, int(255 * fade)),
                    min(255, int(215 * fade)),
                    min(255, int(64 * fade))
                )
            elif i == 3:
                # "Happy Birthday! 🎂✨" in glowing rose pink
                line_col = (
                    min(255, int(255 * fade)),
                    min(255, int(105 * fade)),
                    min(255, int(180 * fade))
                )
            else:
                # Warm ivory cream
                line_col = (
                    min(255, int(255 * fade)),
                    min(255, int(245 * fade)),
                    min(255, int(235 * fade))
                )
                
            # Select font based on whether emoji is present
            has_emoji = any(ord(ch) > 0x2700 for ch in line_text)
            font_to_use = self.emoji_font if has_emoji else self.text_font
            surf_line = font_to_use.render(line_text, True, line_col)
            draw_x = int((screen_w - surf_line.get_width()) / 2.0)
            draw_y = start_y + i * line_height
            
            screen.blit(surf_line, (draw_x, draw_y))


# Maintain HeartAnimationManager symbol for 100% backward compatibility
HeartAnimationManager = CakeAnimationManager
