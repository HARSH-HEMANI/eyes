# Her Eye — Colored ASCII Cinematic Animation ✨

A fullscreen, cinematic Python application that transforms an eye photograph into a high-density, photorealistic colored character mosaic portrait and animates it through a continuous emotional narrative.

Inspired by the reference Instagram Reel ([https://www.instagram.com/reel/DeshX7jIyXP/](https://www.instagram.com/reel/DeshX7jIyXP/)), the application renders thousands of tiny, individually colored text characters with aspect ratio correction, natural biomechanical blinking, camera flight deep into the pupil, a beating ASCII heart, and the final message.

---

## 🎬 Cinematic Animation Sequence

The animation plays seamlessly across 6 scenes:

| Scene | Duration | Description |
|---|---|---|
| **Scene 1 — Darkness** | ~1.4s | Starts in pure pitch black. Faint colored character embers begin to kindle in the void. |
| **Scene 2 — Eye Formation** | ~4.5s | Characters stream and assemble radially from the pupil, resolving over 13,000 tiny colored text glyphs into the photorealistic eye portrait. |
| **Scene 3 — Natural Human Blink** | ~0.2s | The eye pauses so the viewer can appreciate it, then blinks naturally: the upper eyelid margin and lashes descend smoothly over the cornea and reopen. |
| **Scene 4 — Zoom Into Pupil** | ~4.2s | The camera glides progressively toward the center of her pupil. The characters grow larger as the camera plunges into the dark abyss of the pupil. |
| **Scene 5 — Heart Reveal** | ~2.5s | Deep inside the pupil, a glowing red & soft rose ASCII character heart appears and pulses with an anatomical *lub-dub* resting heartbeat. |
| **Scene 6 — Final Message** | ~7.5s | Beneath the beating heart, the message smoothly cascades in line-by-line: <br> `I am sorry,` <br> `Please, Give me this last chance,` <br> `I want to be with you,` <br> `Always You!!!` <br> Held in elegant typography before clean exit. |

---

## 🚀 Quick Start (Windows)

### Option 1: Double-Click Batch File (Recommended)
Simply double-click:
```bat
run.bat
```
This automatically finds the virtual environment or system Python and launches the fullscreen sequence.

### Option 2: Running via Terminal
1. Activate the environment or use Python 3.10+:
   ```bash
   .venv\Scripts\activate
   ```
2. Run `main.py`:
   ```bash
   python main.py
   ```

---

## 📦 Requirements & Installation

If setting up in a fresh Python environment:
```bash
pip install -r requirements.txt
```
Dependencies:
- `pygame >= 2.5.0` (GPU-accelerated surface rendering, display management, timing)
- `pillow >= 10.0.0` (Image loading and color conversion)
- `numpy >= 1.24.0` (Fast array operations and geometric mesh grids)
- `opencv-python >= 4.8.0` (Color space transformations, Sobel gradient edge detection, eyelid displacement warping)

---

## 🛠️ Architecture & Modules

```
d:\eyes\
├── assets/
│   ├── her_eye.jpg         # Primary source photograph (252 x 108 or custom)
│   ├── her_eye.png         # Uncompressed reference
│   └── her_eye_wide.jpg    # Extended border variation
├── ascii_renderer.py       # Colored ASCII mosaic engine with font aspect ratio correction
├── eye_animation.py        # Progressive reveal, biomechanical eyelid blink, pupil zoom
├── heart_animation.py      # Pulsing ASCII heart and elegant message rendering
├── main.py                 # Application controller, 60 FPS clock loop, scene choreographer
├── run.bat                 # One-click Windows launcher
├── requirements.txt        # Python package dependencies
└── README.md               # Documentation & technical details
```

### Key Technical Highlights
1. **Aspect Ratio Correction**:
   Monospace font characters are taller than they are wide ($\approx 6 \times 11\text{ px}$). The renderer computes:
   $$\text{rows} = \text{cols} \times \left(\frac{H_{img}}{W_{img}}\right) \times \left(\frac{\text{char\_w}}{\text{char\_h}}\right)$$
   This guarantees that the rendered eye preserves its exact natural proportions with zero vertical stretching.
2. **True RGB Color Sampling**:
   Every character samples the exact RGB color of its corresponding image cell, rendering against a pitch-black background for an iridescent, glowing mosaic effect.
3. **Biomechanical Eyelid Blinking**:
   Unlike simple vertical image scaling or random character flickering, the blink physically simulates the descent of the upper eyelid and eyelash margin down to the lower lid line, with upper eyelid skin stretching down to realistically cover the iris and pupil.
4. **Cinematic Pupil Flight**:
   The camera smoothly transitions its focal anchor from the portrait center onto the exact pupil coordinates (`norm_x: 0.78, norm_y: 0.54`) using quintic smootherstep easing, ensuring zero jump at the start of the zoom.
5. **60 FPS Performance Caching**:
   Character layouts and blink stages are precomputed into native Pygame surfaces at launch ($< 1$ second), allowing real-time rendering at a rock-solid 60 FPS.

---

## ⌨️ Controls

- **`ESC`**: Exit the animation cleanly at any point.
- **`F` / `F11`**: Toggle between Fullscreen and Windowed mode.
