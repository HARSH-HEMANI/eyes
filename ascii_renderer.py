"""
Her Eye / Birthday Animation — Colored ASCII Cinematic Animation
Module: ascii_renderer.py

Converts source photographs into photorealistic, highly recognizable colored
ASCII character portraits with aspect ratio correction, tight character spacing,
and true photograph color retention.
"""

import os
import cv2
import numpy as np
import pygame

# Rich character density ramp from darkest to brightest
ASCII_RAMP = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
ASCII_RAMP_REV = ASCII_RAMP[::-1]


class ASCIIRenderer:
    """
    Renders ultra-high density colored ASCII mosaics from images with aspect ratio
    correction, minimized character spacing, and cell background color filling for
    instant human recognition.
    """
    def __init__(self, font_name="consolas", font_size=8, bg_tint_ratio=0.45, vertical_overlap=2):
        pygame.font.init()
        self.font = pygame.font.SysFont(font_name, font_size, bold=True)
        if not self.font:
            self.font = pygame.font.Font(None, font_size)
            
        # Monospace metrics
        test_surf = self.font.render("M", True, (255, 255, 255))
        self.char_w = max(1, test_surf.get_width())
        self.char_h = max(1, test_surf.get_height())
        
        # Tight cell stepping (lowering the spaces between characters)
        self.step_x = self.char_w
        self.step_y = max(1, self.char_h - vertical_overlap)
        self.font_aspect = self.step_x / float(self.step_y)
        
        # Background tint ratio (0.0 = black void, 0.45 = photorealistic fill behind glyphs)
        self.bg_tint_ratio = bg_tint_ratio

    def calculate_grid_size(self, img_w, img_h, target_cols=144, max_height=960):
        """
        Calculates (cols, rows) such that on-screen display matches the original image's aspect ratio
        and fits comfortably within the target display window without vertical clipping.
        """
        img_aspect = img_w / float(max(1, img_h))
        cols = int(target_cols)
        rows = int(round(cols / (img_aspect * (self.step_y / float(self.step_x)))))
        
        # If portrait exceeds max_height, rescale gracefully so whole person is visible
        if rows * self.step_y > max_height:
            rows = max(10, max_height // self.step_y)
            cols = int(round(rows * img_aspect * (self.step_y / float(self.step_x))))
            
        rows = max(10, rows)
        cols = max(10, cols)
        return cols, rows

    def process_image(self, img_rgb, cols, rows):
        """
        Downsamples/samples the image to (cols, rows) and computes:
        - character indices based on luminance
        - true RGB colors
        - background cell tint to eliminate black voids
        Returns a dict of processed grid data.
        """
        resized = cv2.resize(img_rgb, (cols, rows), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
        
        cells = []
        ramp_len = len(ASCII_RAMP_REV)
        
        for r in range(rows):
            for c in range(cols):
                b = int(gray[r, c])
                col_rgb = (int(resized[r, c, 0]), int(resized[r, c, 1]), int(resized[r, c, 2]))
                
                # Select rich density character
                idx = int((b / 255.0) * (ramp_len - 1))
                char = ASCII_RAMP_REV[max(0, min(ramp_len - 1, idx))]
                if char == " ":
                    char = "."
                
                # Cell background tint to eliminate empty spaces between character strokes
                bg_col = (
                    int(col_rgb[0] * self.bg_tint_ratio),
                    int(col_rgb[1] * self.bg_tint_ratio),
                    int(col_rgb[2] * self.bg_tint_ratio)
                )
                
                cells.append({
                    'col': c,
                    'row': r,
                    'char': char,
                    'color': col_rgb,
                    'bg_color': bg_col,
                    'brightness': b,
                    'x': c * self.step_x,
                    'y': r * self.step_y
                })
                
        return {
            'cols': cols,
            'rows': rows,
            'width': cols * self.step_x,
            'height': rows * self.step_y,
            'cells': cells,
            'resized_rgb': resized
        }

    def render_to_surface(self, grid_data, reveal_progress=1.0, reveal_order=None, flicker_intensity=0.0):
        """
        Renders the grid cells onto a Pygame surface.
        Fills character cell backgrounds and draws glyphs tightly to form a clear portrait.
        """
        surf = pygame.Surface((grid_data['width'], grid_data['height']), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        
        cells = grid_data['cells']
        total_cells = len(cells)
        visible_count = int(round(total_cells * max(0.0, min(1.0, reveal_progress))))
        
        if reveal_order is None:
            indices_to_draw = range(visible_count)
        else:
            indices_to_draw = reveal_order[:visible_count]
            
        font = self.font
        step_x = self.step_x
        step_y = self.step_y
        
        for idx in indices_to_draw:
            cell = cells[idx]
            ch = cell['char']
            px = cell['x']
            py = cell['y']
            
            color = cell['color']
            bg_col = cell['bg_color']
            
            if flicker_intensity > 0.0:
                flicker = 1.0 + np.random.uniform(-flicker_intensity, flicker_intensity)
                color = (
                    min(255, int(color[0] * flicker)),
                    min(255, int(color[1] * flicker)),
                    min(255, int(color[2] * flicker))
                )
                bg_col = (
                    min(255, int(bg_col[0] * flicker)),
                    min(255, int(bg_col[1] * flicker)),
                    min(255, int(bg_col[2] * flicker))
                )
            
            # 1. Fill background of cell to lower space between characters
            pygame.draw.rect(surf, bg_col, (px, py, step_x, step_y))
            
            # 2. Render colored ASCII text glyph
            char_surf = font.render(ch, True, color)
            surf.blit(char_surf, (px, py))
            
        return surf
