"""
Her Eye — Colored ASCII Cinematic Animation
Module: eye_animation.py

Implements:
1. Scene 2 — Progressive character assembly & eye formation reveal
2. Scene 3 — Biomechanically realistic human eyelid blinking
3. Scene 4 — Cinematic smooth camera zoom into the pupil center
"""

import math
import cv2
import numpy as np
import pygame

class EyeAnimationManager:
    """
    Manages the reveal, realistic eyelid deformation blinking,
    and camera zoom targeting the pupil center.
    """
    def __init__(self, renderer, base_img_rgb, pupil_pos=None, target_cols=180):
        self.renderer = renderer
        self.base_img_rgb = base_img_rgb
        self.img_h, self.img_w, _ = base_img_rgb.shape
        
        # Calculate grid
        self.cols, self.rows = renderer.calculate_grid_size(self.img_w, self.img_h, target_cols)
        
        # Process base open eye
        self.base_grid = renderer.process_image(base_img_rgb, self.cols, self.rows)
        self.portrait_w = self.base_grid['width']
        self.portrait_h = self.base_grid['height']
        
        # Pre-render base open eye surface
        self.open_eye_surface = renderer.render_to_surface(self.base_grid)
        
        # Determine pupil position in normalized (0..1) coords
        if pupil_pos is not None:
            self.pupil_norm_x, self.pupil_norm_y = pupil_pos
        else:
            self.pupil_norm_x, self.pupil_norm_y = self._detect_pupil()
            
        # Target pixel on portrait surface
        self.pupil_surface_x = self.pupil_norm_x * self.portrait_w
        self.pupil_surface_y = self.pupil_norm_y * self.portrait_h
        
        # Generate cell reveal sequence for Scene 2 (Rain + Radial frontier assembly)
        self.reveal_order = self._generate_reveal_order()
        
        # Precompute blink surfaces for Scene 3 (realistic eyelid motion)
        self.blink_surfaces = self._precompute_blink_frames(num_frames=12)

    def _detect_pupil(self):
        """
        Detects the darkest region corresponding to the pupil center.
        Works across both single-eye close-ups and dual-eye photographs.
        """
        gray = cv2.cvtColor(self.base_img_rgb, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape
        
        # Search within central eye opening region
        x1, x2 = int(0.20 * w), int(0.80 * w)
        y1, y2 = int(0.20 * h), int(0.75 * h)
        sub = gray[y1:y2, x1:x2]
        
        blur = cv2.GaussianBlur(sub, (15, 15), 0)
        min_v, _, min_l, _ = cv2.minMaxLoc(blur)
        
        best_x = (x1 + min_l[0]) / float(w)
        best_y = (y1 + min_l[1]) / float(h)
        return (best_x, best_y)

    def _generate_reveal_order(self):
        """
        Generates a cinematic character reveal order combining falling matrix-like
        droplets with outward radial settling from the pupil.
        """
        cells = self.base_grid['cells']
        total = len(cells)
        
        # Center of reveal (pupil)
        center_col = self.pupil_norm_x * self.cols
        center_row = self.pupil_norm_y * self.rows
        
        scores = []
        for i, c in enumerate(cells):
            # Distance from pupil
            dx = (c['col'] - center_col)
            dy = (c['row'] - center_row) * (self.renderer.char_h / self.renderer.char_w)
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Column-based falling delay + random scatter
            col_delay = math.sin(c['col'] * 0.4) * 5.0
            noise = np.random.uniform(-4.0, 4.0)
            
            score = dist * 1.5 + col_delay + noise
            scores.append((score, i))
            
        scores.sort(key=lambda item: item[0])
        return [item[1] for item in scores]

    def _deform_eyelids(self, closure):
        """
        Biomechanically realistic eyelid closure simulator:
        Warps the eye image so the upper eyelid and eyelashes smoothly descend
        over the eye opening, with upper lid skin stretching downward.
        Supports both single-eye macro close-ups and multi-eye portraits.
        """
        if closure <= 0.005:
            return self.base_img_rgb.copy()
            
        h, w = self.img_h, self.img_w
        base = self.base_img_rgb
        
        # Check if single centered eye close-up (pupil between 0.35 and 0.65 width)
        is_single_eye = (0.32 <= self.pupil_norm_x <= 0.68)
        
        if is_single_eye:
            eyes = [{
                'cx': int(self.pupil_norm_x * w),
                'cy': int(self.pupil_norm_y * h),
                'rx': int(0.34 * w),
                'ry_top': int(0.12 * h),
                'ry_bot': int(0.24 * h),
                'skin_top': int(0.22 * h)
            }]
        else:
            # Dual eye portrait
            eyes = [
                {
                    'cx': int(self.pupil_norm_x * w),
                    'cy': int(self.pupil_norm_y * h),
                    'rx': int(0.17 * w),
                    'ry_top': int(0.16 * h),
                    'ry_bot': int(0.17 * h),
                    'skin_top': int(0.20 * h)
                },
                {
                    'cx': int(0.18 * w),
                    'cy': int(0.44 * h),
                    'rx': int(0.14 * w),
                    'ry_top': int(0.14 * h),
                    'ry_bot': int(0.15 * h),
                    'skin_top': int(0.16 * h)
                }
            ]
        
        map_x = np.tile(np.arange(w, dtype=np.float32), (h, 1))
        map_y = np.tile(np.arange(h, dtype=np.float32)[:, np.newaxis], (1, w))
        
        for eye in eyes:
            cx, rx = eye['cx'], eye['rx']
            skin_anchor = max(0, eye['cy'] - eye['ry_top'] - eye['skin_top'])
            
            for x in range(max(0, cx - rx), min(w, cx + rx + 1)):
                dx = (x - cx) / float(rx)
                if abs(dx) > 1.0:
                    continue
                arc = math.sqrt(max(0.0, 1.0 - dx * dx))
                top_y = eye['cy'] - eye['ry_top'] * (0.6 + 0.4 * arc if is_single_eye else arc)
                bot_y = eye['cy'] + eye['ry_bot'] * (0.3 + 0.7 * arc)
                
                # Target descent line of the eyelid margin
                target_lid_y = top_y + closure * (bot_y - top_y)
                
                # Stretch upper eyelid skin from skin_anchor down to target_lid_y
                for y in range(int(skin_anchor), min(h, int(bot_y) + 1)):
                    if y <= target_lid_y:
                        norm = (y - skin_anchor) / max(1e-5, (target_lid_y - skin_anchor))
                        src_y = skin_anchor + norm * (top_y - skin_anchor)
                        map_y[y, x] = min(h - 1, max(0, src_y))
                        
        warped = cv2.remap(base, map_x, map_y, cv2.INTER_LINEAR)
        
        # Darken eyelash boundary where upper lid closes
        for eye in eyes:
            cx, rx = eye['cx'], eye['rx']
            for x in range(max(0, cx - rx), min(w, cx + rx + 1)):
                dx = (x - cx) / float(rx)
                if abs(dx) > 1.0:
                    continue
                arc = math.sqrt(max(0.0, 1.0 - dx * dx))
                top_y = eye['cy'] - eye['ry_top'] * (0.6 + 0.4 * arc if is_single_eye else arc)
                bot_y = eye['cy'] + eye['ry_bot'] * (0.3 + 0.7 * arc)
                target_lid_y = int(top_y + closure * (bot_y - top_y))
                if 0 <= target_lid_y < h:
                    warped[target_lid_y, x] = (warped[target_lid_y, x] * (1.0 - 0.45 * closure)).astype(np.uint8)
                    if target_lid_y + 1 < h:
                        warped[target_lid_y + 1, x] = (warped[target_lid_y + 1, x] * (1.0 - 0.25 * closure)).astype(np.uint8)
                        
        return warped

    def _precompute_blink_frames(self, num_frames=12):
        """
        Precomputes the ASCII character surfaces for each stage of the blink
        so real-time animation requires zero re-rasterization.
        """
        surfaces = []
        for i in range(num_frames):
            # Asymmetrical blink trajectory: closes fast (40%), opens gracefully (60%)
            t = i / float(num_frames - 1)
            if t <= 0.38:
                closure = math.sin((t / 0.38) * (math.pi / 2.0)) ** 2
            else:
                closure = math.cos(((t - 0.38) / 0.62) * (math.pi / 2.0)) ** 2
                
            deformed_img = self._deform_eyelids(closure)
            grid = self.renderer.process_image(deformed_img, self.cols, self.rows)
            surf = self.renderer.render_to_surface(grid)
            surfaces.append(surf)
            
        return surfaces

    def render_reveal(self, screen, progress):
        """
        Scene 2: Renders the progressive eye reveal centered on the screen.
        """
        screen_w, screen_h = screen.get_size()
        
        # Calculate reveal fraction with smooth easing
        eased_p = progress * progress * (3.0 - 2.0 * progress)
        
        # Add subtle frontier character flicker
        flicker = 0.25 if progress < 0.98 else 0.0
        surf = self.renderer.render_to_surface(
            self.base_grid,
            reveal_progress=eased_p,
            reveal_order=self.reveal_order,
            flicker_intensity=flicker
        )
        
        # Center on screen
        draw_x = (screen_w - self.portrait_w) // 2
        draw_y = (screen_h - self.portrait_h) // 2
        screen.blit(surf, (draw_x, draw_y))

    def render_blink(self, screen, blink_progress):
        """
        Scene 3: Renders the natural human eyelid blink.
        blink_progress is in [0.0, 1.0].
        """
        screen_w, screen_h = screen.get_size()
        draw_x = (screen_w - self.portrait_w) // 2
        draw_y = (screen_h - self.portrait_h) // 2
        
        num_frames = len(self.blink_surfaces)
        idx = int(round(blink_progress * (num_frames - 1)))
        idx = max(0, min(num_frames - 1, idx))
        
        surf = self.blink_surfaces[idx]
        screen.blit(surf, (draw_x, draw_y))

    def render_zoom(self, screen, zoom_progress):
        """
        Scene 4: Smooth progressive cinematic zoom centered on the exact pupil.
        Uses fast viewport cropping so scaling is blazingly fast (60 FPS locked)
        without allocating massive offscreen surfaces.
        zoom_progress in [0.0, 1.0].
        """
        screen_w, screen_h = screen.get_size()
        
        # Quintic smootherstep easing for cinematic glide
        p = max(0.0, min(1.0, zoom_progress))
        t = p * p * p * (p * (p * 6.0 - 15.0) + 10.0)
        
        # Max zoom scale: 28x so the pupil completely fills the screen
        max_scale = 28.0
        current_scale = 1.0 + (max_scale - 1.0) * (t ** 1.8)
        
        # Smoothly interpolate focus point from portrait center to pupil center
        focus_blend = min(1.0, t * 1.5)
        focus_x = (1.0 - focus_blend) * (self.portrait_w / 2.0) + focus_blend * self.pupil_surface_x
        focus_y = (1.0 - focus_blend) * (self.portrait_h / 2.0) + focus_blend * self.pupil_surface_y
        
        # Calculate viewport slice in source portrait space
        view_w = max(4.0, screen_w / current_scale)
        view_h = max(4.0, screen_h / current_scale)
        
        src_x = focus_x - view_w / 2.0
        src_y = focus_y - view_h / 2.0
        
        # Fast viewport extract: blit visible patch into intermediate surface
        vw_int = int(math.ceil(view_w)) + 2
        vh_int = int(math.ceil(view_h)) + 2
        patch = pygame.Surface((vw_int, vh_int), pygame.SRCALPHA)
        patch.fill((0, 0, 0, 0))
        patch.blit(self.open_eye_surface, (-int(src_x), -int(src_y)))
        
        # Scale only the screen-sized viewport
        if current_scale < 3.0:
            scaled = pygame.transform.smoothscale(patch, (screen_w, screen_h))
        else:
            scaled = pygame.transform.scale(patch, (screen_w, screen_h))
            
        # As camera plunges deep into the pupil, iris edges smoothly fade into black
        if p > 0.60:
            fade_to_black = min(1.0, (p - 0.60) / 0.40)
            alpha = int(round(255 * (1.0 - fade_to_black)))
            scaled.set_alpha(alpha)
            
        screen.blit(scaled, (0, 0))

