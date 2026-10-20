"""
Her Eye — Colored ASCII Cinematic Animation
Module: ascii_renderer.py

Converts source photographs into photorealistic colored ASCII character portraits.
Handles font aspect ratio correction, color sampling, brightness/texture character
selection, and fast surface rendering with caching.
"""

import os
import cv2
import numpy as np
import pygame

# Character density ramp from darkest (sparse/space) to brightest (dense)
ASCII_RAMP = " .'`^\",:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

class ASCIIRenderer:
    """
    Renders high-density colored ASCII mosaics from images with aspect ratio
    correction and character surface caching.
    """
    def __init__(self, font_name="consolas", font_size=11):
        pygame.font.init()
        # Find monospace font
        self.font = pygame.font.SysFont(font_name, font_size)
        if not self.font:
            self.font = pygame.font.Font(None, font_size)
            
        # Monospace metrics
        test_surf = self.font.render("M", True, (255, 255, 255))
        self.char_w = max(1, test_surf.get_width())
        self.char_h = max(1, test_surf.get_height())
        self.font_aspect = self.char_w / self.char_h  # typically ~0.55
        
        # Pre-render glyph textures in white for blitting with color mod if needed
        self.glyph_cache = {}
        for ch in ASCII_RAMP:
            self.glyph_cache[ch] = self.font.render(ch, True, (255, 255, 255))
        self.glyph_cache[" "] = pygame.Surface((self.char_w, self.char_h), pygame.SRCALPHA)

    def calculate_grid_size(self, img_w, img_h, target_cols=180):
        """
        Calculates (cols, rows) such that on-screen display matches the original image's aspect ratio.
        cols * char_w / (rows * char_h) == img_w / img_h
        rows = cols * (img_h / img_w) * (char_w / char_h)
        """
        img_aspect = img_w / max(1, img_h)
        cols = int(target_cols)
        rows = int(round(cols / (img_aspect * (self.char_h / self.char_w))))
        rows = max(10, rows)
        return cols, rows

    def process_image(self, img_rgb, cols, rows):
        """
        Downsamples/samples the image to (cols, rows) and computes:
        - character indices based on luminance and local gradient
        - true RGB colors
        - brightness values
        Returns a dict of processed grid data.
        """
        # Resize image to match grid
        resized = cv2.resize(img_rgb, (cols, rows), interpolation=cv2.INTER_AREA)
        
        # Grayscale for luminance
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
        
        # Sobel edge detection for directional characters
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        grad_dir = np.arctan2(grad_y, grad_x) * (180.0 / np.pi)  # -180 to 180
        
        cells = []
        ramp_len = len(ASCII_RAMP)
        
        for r in range(rows):
            for c in range(cols):
                b = int(gray[r, c])
                col_rgb = (int(resized[r, c, 0]), int(resized[r, c, 1]), int(resized[r, c, 2]))
                
                # Check for strong directional edge
                g_mag = grad_mag[r, c]
                g_ang = grad_dir[r, c]
                
                if b < 12:
                    char = " "
                elif g_mag > 65 and b > 40:
                    # Directional edge glyph
                    if -22.5 <= g_ang <= 22.5 or g_ang >= 157.5 or g_ang <= -157.5:
                        char = "|"
                    elif 22.5 < g_ang < 67.5 or -157.5 < g_ang < -112.5:
                        char = "/"
                    elif 67.5 <= g_ang <= 112.5 or -112.5 <= g_ang <= -67.5:
                        char = "-"
                    else:
                        char = "\\"
                else:
                    # Density ramp
                    ramp_idx = int((b / 255.0) * (ramp_len - 1))
                    ramp_idx = max(0, min(ramp_len - 1, ramp_idx))
                    char = ASCII_RAMP[ramp_idx]
                
                cells.append({
                    'col': c,
                    'row': r,
                    'char': char,
                    'color': col_rgb,
                    'brightness': b,
                    'x': c * self.char_w,
                    'y': r * self.char_h
                })
                
        return {
            'cols': cols,
            'rows': rows,
            'width': cols * self.char_w,
            'height': rows * self.char_h,
            'cells': cells,
            'resized_rgb': resized
        }

    def render_to_surface(self, grid_data, reveal_progress=1.0, reveal_order=None, flicker_intensity=0.0):
        """
        Renders the grid cells onto a Pygame surface.
        Supports reveal_progress (0.0 to 1.0) with custom cell reveal_order.
        """
        surf = pygame.Surface((grid_data['width'], grid_data['height']), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        
        cells = grid_data['cells']
        total_cells = len(cells)
        visible_count = int(round(total_cells * max(0.0, min(1.0, reveal_progress))))
        
        # If no custom order, order is simply linear
        if reveal_order is None:
            indices_to_draw = range(visible_count)
        else:
            indices_to_draw = reveal_order[:visible_count]
            
        font = self.font
        for idx in indices_to_draw:
            cell = cells[idx]
            ch = cell['char']
            if ch == " ":
                continue
                
            color = cell['color']
            if flicker_intensity > 0.0:
                # Subtle brightness flicker on frontier characters
                flicker = 1.0 + np.random.uniform(-flicker_intensity, flicker_intensity)
                color = (
                    min(255, int(color[0] * flicker)),
                    min(255, int(color[1] * flicker)),
                    min(255, int(color[2] * flicker))
                )
                
            char_surf = font.render(ch, True, color)
            surf.blit(char_surf, (cell['x'], cell['y']))
            
        return surf
