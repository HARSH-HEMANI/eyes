/**
 * Her Eye — Colored ASCII Cinematic Animation (Web Version)
 * Recreates the complete 6-scene sequence client-side on HTML5 Canvas.
 */

const ASCII_RAMP = " .'`^\",:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$";
const HEART_CHARS = ["@", "#", "W", "M", "&", "8", "%", "Q", "B", "0", "O", "*", "+", "x"];

// Timeline (seconds)
const T_DARKNESS_END   = 1.4;
const T_REVEAL_END     = 5.9;
const T_APPRECIATE_END = 8.0;
const T_BLINK_END      = 8.22;
const T_POST_BLINK_END = 9.3;
const T_ZOOM_END       = 13.5;
const T_HEART_ONLY_END = 16.5;
const T_FINAL_END      = 28.0;

class EyeWebAnimation {
  constructor() {
    this.canvas = document.getElementById("main-canvas");
    this.ctx = this.canvas.getContext("2d");
    this.overlay = document.getElementById("intro-overlay");
    
    this.started = false;
    this.startTime = 0;
    
    this.img = new Image();
    this.img.crossOrigin = "anonymous";
    this.imgLoaded = false;
    
    // High density grid with tight character spacing
    this.targetCols = window.innerWidth < 768 ? 110 : 144;
    this.charW = 5;
    this.charH = 8;
    this.stepX = 5;
    this.stepY = 6;
    // Focus coordinates (targeting the smiling baby in the photo)
    this.pupilNormX = 0.50;
    this.pupilNormY = 0.28;
    
    this.baseGrid = null;
    this.openPortraitCanvas = null;
    this.blinkCanvases = [];
    this.masterCakeCanvas = null;
    
    this.resizeCanvas();
    window.addEventListener("resize", () => this.resizeCanvas());
    
    this.setupEvents();
    this.loadImage();
  }
  
  resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }
  
  setupEvents() {
    const start = () => {
      if (!this.started && this.imgLoaded) {
        this.started = true;
        this.overlay.classList.add("hidden");
        // Request fullscreen if supported on mobile
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen().catch(() => {});
        }
        this.startTime = performance.now() / 1000.0;
        requestAnimationFrame((t) => this.loop(t));
      }
    };
    this.overlay.addEventListener("click", start);
    this.overlay.addEventListener("touchstart", start, { passive: true });
  }
  
  loadImage() {
    this.img.onload = () => {
      this.imgLoaded = true;
      this.initEngine();
      document.querySelector(".intro-prompt").textContent = "Tap anywhere to begin ✨";
    };
    this.img.src = typeof EYE_IMAGE_DATA_URI !== "undefined" ? EYE_IMAGE_DATA_URI : "assets/her_eye.jpg";
  }
  
  initEngine() {
    const imgW = this.img.naturalWidth;
    const imgH = this.img.naturalHeight;
    const imgAspect = imgW / imgH;
    
    // Fit portrait comfortably within window without clipping
    const maxH = Math.min(window.innerHeight * 0.90, 960);
    this.cols = this.targetCols;
    this.rows = Math.round(this.cols / (imgAspect * (this.stepY / this.stepX)));
    if (this.rows * this.stepY > maxH) {
      this.rows = Math.max(10, Math.floor(maxH / this.stepY));
      this.cols = Math.round(this.rows * imgAspect * (this.stepY / this.stepX));
    }
    
    this.portraitW = this.cols * this.stepX;
    this.portraitH = this.rows * this.stepY;
    
    this.pupilSurfaceX = this.pupilNormX * this.portraitW;
    this.pupilSurfaceY = this.pupilNormY * this.portraitH;
    
    // Sample base image
    this.baseGrid = this.processImage(this.img);
    this.openPortraitCanvas = this.renderGridToCanvas(this.baseGrid, 1.0);
    
    // Precompute reveal order (radial + matrix droplets)
    this.revealOrder = this.generateRevealOrder();
    
    // Precompute eyelid blink stages
    this.blinkCanvases = this.precomputeBlinkFrames(10);
    
    // Precompute master ASCII birthday cake
    this.masterCakeCanvas = this.precomputeMasterCake();
  }
  
  processImage(sourceImg) {
    const offCanvas = document.createElement("canvas");
    offCanvas.width = this.cols;
    offCanvas.height = this.rows;
    const offCtx = offCanvas.getContext("2d", { willReadFrequently: true });
    offCtx.drawImage(sourceImg, 0, 0, this.cols, this.rows);
    
    const imgData = offCtx.getImageData(0, 0, this.cols, this.rows);
    const data = imgData.data;
    
    const cells = [];
    const rampLen = ASCII_RAMP.length;
    
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        const idx = (r * this.cols + c) * 4;
        const red = data[idx];
        const green = data[idx + 1];
        const blue = data[idx + 2];
        const lum = Math.round(0.299 * red + 0.587 * green + 0.114 * blue);
        
        const rampIdx = Math.min(rampLen - 1, Math.floor((lum / 255.0) * (rampLen - 1)));
        let char = ASCII_RAMP[rampIdx];
        if (char === " ") char = ".";
        
        // Background tint to eliminate black voids between character strokes
        const bgR = Math.floor(red * 0.45);
        const bgG = Math.floor(green * 0.45);
        const bgB = Math.floor(blue * 0.45);
        
        cells.push({
          c, r,
          char,
          color: `rgb(${red},${green},${blue})`,
          bgColor: `rgb(${bgR},${bgG},${bgB})`,
          x: c * this.stepX,
          y: r * this.stepY,
          lum
        });
      }
    }
    return cells;
  }
  
  renderGridToCanvas(cells, revealProgress = 1.0, revealOrder = null) {
    const c = document.createElement("canvas");
    c.width = this.portraitW;
    c.height = this.portraitH;
    const ctx = c.getContext("2d");
    
    ctx.font = `bold ${this.charH}px Consolas, monospace`;
    ctx.textBaseline = "top";
    
    const total = cells.length;
    const visibleCount = Math.round(total * Math.max(0, Math.min(1, revealProgress)));
    const indices = revealOrder ? revealOrder.slice(0, visibleCount) : Array.from({ length: visibleCount }, (_, i) => i);
    
    for (let i = 0; i < indices.length; i++) {
      const cell = cells[indices[i]];
      // Fill cell background to eliminate empty spaces between characters
      ctx.fillStyle = cell.bgColor;
      ctx.fillRect(cell.x, cell.y, this.stepX, this.stepY);
      
      // Render colored ASCII text glyph
      ctx.fillStyle = cell.color;
      ctx.fillText(cell.char, cell.x, cell.y);
    }
    return c;
  }
  
  generateRevealOrder() {
    const centerCol = this.pupilNormX * this.cols;
    const centerRow = this.pupilNormY * this.rows;
    const arFactor = this.stepY / this.stepX;
    
    const scores = this.baseGrid.map((c, i) => {
      const dx = c.c - centerCol;
      const dy = (c.r - centerRow) * arFactor;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const colDelay = Math.sin(c.c * 0.4) * 4.0;
      const noise = (Math.random() - 0.5) * 6.0;
      return { score: dist * 1.4 + colDelay + noise, idx: i };
    });
    
    scores.sort((a, b) => a.score - b.score);
    return scores.map(s => s.idx);
  }
  
  deformEyelids(sourceImg, closure) {
    // For portrait photos, preserve the complete portrait intact
    return sourceImg;
  }
  
  precomputeBlinkFrames(numFrames = 10) {
    const list = [];
    for (let i = 0; i < numFrames; i++) {
      const t = i / (numFrames - 1);
      const closure = t <= 0.38 ? Math.pow(Math.sin((t / 0.38) * Math.PI * 0.5), 2) : Math.pow(Math.cos(((t - 0.38) / 0.62) * Math.PI * 0.5), 2);
      const deformed = this.deformEyelids(this.img, closure);
      const grid = this.processImage(deformed);
      list.push(this.renderGridToCanvas(grid, 1.0));
    }
    return list;
  }
  
  precomputeMasterCake() {
    const cols = 80;
    const rows = 44;
    const w = cols * this.charW;
    const h = rows * this.charH;
    
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    
    ctx.font = `bold ${this.charH - 1}px Consolas, monospace`;
    ctx.textBaseline = "top";
    
    const candleCols = [28, 34, 40, 46, 52];
    const candleColors = [
      "rgb(0, 229, 255)",    // Cyan
      "rgb(255, 64, 129)",   // Rose Pink
      "rgb(255, 214, 0)",    // Golden Yellow
      "rgb(105, 240, 174)",  // Mint Green
      "rgb(224, 64, 251)"    // Lavender Purple
    ];
    
    // 1. Candle bodies and wicks
    candleCols.forEach((col, idx) => {
      const color = candleColors[idx];
      for (let r = 7; r <= 11; r++) {
        const ch = (r + idx) % 2 === 0 ? "|" : "I";
        ctx.fillStyle = color;
        ctx.fillText(ch, col * this.charW, r * this.charH);
      }
      ctx.fillStyle = "#888888";
      ctx.fillText("'", col * this.charW, 6 * this.charH);
    });
    
    // 2. Top Tier (cols 24 to 56)
    for (let c = 24; c <= 56; c++) {
      const isCherry = [25, 32, 40, 48, 55].includes(c);
      if (isCherry) {
        ctx.fillStyle = "#ff1744";
        ctx.fillText("@", c * this.charW, 12 * this.charH);
      } else {
        ctx.fillStyle = c % 2 === 0 ? "#fff0f5" : "#ffb6c1";
        ctx.fillText(c % 2 === 0 ? "o" : "~", c * this.charW, 12 * this.charH);
      }
    }
    for (let r = 13; r <= 14; r++) {
      for (let c = 24; c <= 56; c++) {
        const drip = c % 4 === (r % 2) * 2;
        ctx.fillStyle = drip ? "#ffd1dc" : "#fff5fa";
        ctx.fillText(drip ? "U" : "#", c * this.charW, r * this.charH);
      }
    }
    const topChars = ["M", "W", "#", "%", "8", "&", "B"];
    for (let r = 15; r <= 19; r++) {
      for (let c = 24; c <= 56; c++) {
        if (c === 24 || c === 56) {
          ctx.fillStyle = "#f06292";
          ctx.fillText("|", c * this.charW, r * this.charH);
        } else if (r === 17) {
          ctx.fillStyle = "#ff4081";
          ctx.fillText("=", c * this.charW, r * this.charH);
        } else {
          const ch = topChars[(c * 7 + r * 5) % topChars.length];
          const shade = 0.85 + 0.15 * Math.sin(c * 0.4);
          ctx.fillStyle = `rgb(${Math.floor(255 * shade)},${Math.floor(170 * shade)},${Math.floor(190 * shade)})`;
          ctx.fillText(ch, c * this.charW, r * this.charH);
        }
      }
    }
    
    // 3. Middle Tier (cols 16 to 64)
    for (let c = 16; c <= 64; c++) {
      if ([17, 23, 31, 40, 49, 57, 63].includes(c)) {
        ctx.fillStyle = "#ffd700";
        ctx.fillText("*", c * this.charW, 20 * this.charH);
      } else {
        ctx.fillStyle = "#fffff0";
        ctx.fillText(c % 3 === 0 ? "O" : "~", c * this.charW, 20 * this.charH);
      }
    }
    const sprinkles = ["#00e5ff", "#ff4081", "#ffd600", "#76ff03", "#ff9100"];
    for (let r = 21; r <= 22; r++) {
      for (let c = 16; c <= 64; c++) {
        if ((c * 3 + r * 7) % 11 === 0) {
          ctx.fillStyle = sprinkles[(c + r) % sprinkles.length];
          ctx.fillText("+", c * this.charW, r * this.charH);
        } else {
          ctx.fillStyle = "#fff0f5";
          ctx.fillText(c % 2 === 0 ? "w" : "m", c * this.charW, r * this.charH);
        }
      }
    }
    const midChars = ["@", "#", "8", "%", "&", "Q", "0"];
    for (let r = 23; r <= 28; r++) {
      for (let c = 16; c <= 64; c++) {
        if (c === 16 || c === 64) {
          ctx.fillStyle = "#8d6e63";
          ctx.fillText("|", c * this.charW, r * this.charH);
        } else if (r === 25) {
          ctx.fillStyle = c % 4 === 0 ? "#ffd700" : "#6d4c41";
          ctx.fillText(c % 4 === 0 ? "*" : "=", c * this.charW, r * this.charH);
        } else if (r === 26) {
          ctx.fillStyle = "#e91e63";
          ctx.fillText("~", c * this.charW, r * this.charH);
        } else {
          const ch = midChars[(c * 9 + r * 11) % midChars.length];
          const shade = 0.8 + 0.2 * Math.cos(c * 0.35 + r * 0.2);
          ctx.fillStyle = `rgb(${Math.floor(210 * shade)},${Math.floor(145 * shade)},${Math.floor(105 * shade)})`;
          ctx.fillText(ch, c * this.charW, r * this.charH);
        }
      }
    }
    
    // 4. Base Tier (cols 8 to 72)
    for (let c = 8; c <= 72; c++) {
      if ([9, 15, 22, 30, 40, 50, 58, 65, 71].includes(c)) {
        ctx.fillStyle = "#ff1744";
        ctx.fillText("@", c * this.charW, 29 * this.charH);
      } else {
        ctx.fillStyle = "#fff8e1";
        ctx.fillText(c % 2 === 0 ? "v" : "~", c * this.charW, 29 * this.charH);
      }
    }
    for (let r = 30; r <= 31; r++) {
      for (let c = 8; c <= 72; c++) {
        if (c % 5 === 0) {
          ctx.fillStyle = "#ffd700";
          ctx.fillText("o", c * this.charW, r * this.charH);
        } else {
          ctx.fillStyle = "#ffebee";
          ctx.fillText(c % 2 === 0 ? "S" : "C", c * this.charW, r * this.charH);
        }
      }
    }
    const baseChars = ["@", "#", "W", "M", "8", "B", "%", "&"];
    for (let r = 32; r <= 37; r++) {
      for (let c = 8; c <= 72; c++) {
        if (c === 8 || c === 72) {
          ctx.fillStyle = "#ffb300";
          ctx.fillText("|", c * this.charW, r * this.charH);
        } else if (r === 34) {
          ctx.fillStyle = c % 3 === 0 ? "#ffeb3b" : "#ff4081";
          ctx.fillText(c % 3 === 0 ? "*" : "-", c * this.charW, r * this.charH);
        } else if (r === 35) {
          ctx.fillStyle = "#f48fb1";
          ctx.fillText("~", c * this.charW, r * this.charH);
        } else {
          const ch = baseChars[(c * 13 + r * 7) % baseChars.length];
          const shade = 0.85 + 0.15 * Math.sin(c * 0.25);
          ctx.fillStyle = `rgb(${Math.floor(255 * shade)},${Math.floor(190 * shade)},${Math.floor(130 * shade)})`;
          ctx.fillText(ch, c * this.charW, r * this.charH);
        }
      }
    }
    
    // 5. Cake Stand & Pedestal (cols 4 to 76)
    for (let c = 4; c <= 76; c++) {
      const gold = Math.floor(200 + 55 * Math.cos((c - 40) * 0.1));
      ctx.fillStyle = `rgb(255, ${gold}, 0)`;
      ctx.fillText("=", c * this.charW, 38 * this.charH);
      ctx.fillStyle = "#ffecb3";
      ctx.fillText(c % 4 === 0 ? "*" : "-", c * this.charW, 39 * this.charH);
    }
    for (let r = 40; r <= 42; r++) {
      const cStart = r === 40 ? 32 : (r === 41 ? 30 : 22);
      const cEnd = r === 40 ? 48 : (r === 41 ? 50 : 58);
      for (let c = cStart; c <= cEnd; c++) {
        let ch = c % 3 === 0 ? "|" : ":";
        if (c === cStart) ch = "/";
        else if (c === cEnd) ch = "\\";
        else if (r === 42) ch = "=";
        const gShade = Math.floor(180 + 30 * Math.sin(c * 0.3));
        ctx.fillStyle = `rgb(235, ${gShade}, 60)`;
        ctx.fillText(ch, c * this.charW, r * this.charH);
      }
    }
    
    return canvas;
  }
  
  calculateCelebrationPulse(t) {
    return 1.0 + Math.sin(t * 2.2) * 0.02;
  }
  
  renderCake(elapsed, entranceProgress = 1.0, centerOffsetY = -50) {
    const cx = this.width / 2.0;
    const cy = this.height / 2.0 + centerOffsetY;
    
    const pulse = this.calculateCelebrationPulse(elapsed);
    const eScale = entranceProgress * entranceProgress * (3.0 - 2.0 * entranceProgress);
    const totalScale = pulse * eScale;
    if (totalScale <= 0.01) return;
    
    const tw = this.masterCakeCanvas.width * totalScale;
    const th = this.masterCakeCanvas.height * totalScale;
    
    this.ctx.save();
    if (eScale < 0.99) this.ctx.globalAlpha = eScale;
    this.ctx.imageSmoothingEnabled = true;
    
    // Draw cake body
    const cakeLeft = cx - tw / 2.0;
    const cakeTop = cy - th / 2.0;
    this.ctx.drawImage(this.masterCakeCanvas, cakeLeft, cakeTop, tw, th);
    
    // Real-time flickering flames & sparkles scaled to cake coordinates
    const scaleFactor = totalScale;
    const charW = this.charW * scaleFactor;
    const charH = this.charH * scaleFactor;
    
    this.ctx.font = `bold ${Math.max(8, Math.round((this.charH - 1) * scaleFactor))}px Consolas, monospace`;
    this.ctx.textBaseline = "top";
    
    const candleCols = [28, 34, 40, 46, 52];
    candleCols.forEach((col, idx) => {
      const flicker = Math.sin(elapsed * 12.0 + idx * 1.9) * 0.4 + Math.sin(elapsed * 23.0 + idx * 0.7) * 0.2;
      const shiftX = flicker * (charW * 0.35);
      const fx = cakeLeft + col * charW + shiftX;
      
      // Base flame (orange-red)
      this.ctx.fillStyle = "#ff5722";
      this.ctx.fillText("^", fx, cakeTop + 5 * charH);
      
      // Core flame (amber)
      this.ctx.fillStyle = "#ffc107";
      this.ctx.fillText(flicker > 0 ? "(" : ")", fx * 0.98, cakeTop + 4 * charH);
      
      // Flame tip (luminous yellow)
      this.ctx.fillStyle = "#fff59d";
      this.ctx.fillText(Math.abs(flicker) < 0.2 ? "*" : "^", fx * 1.02, cakeTop + 3 * charH);
      
      // Occasional spark
      if (Math.sin(elapsed * 8.0 + idx) > 0.3) {
        this.ctx.fillStyle = "#ffee58";
        this.ctx.fillText(".", fx * 1.05, cakeTop + 2 * charH);
      }
    });
    
    // Twinkling sparkles drifting around the cake
    const sparkles = [
      [8, 6, '*'], [14, 12, '+'], [70, 8, '*'], [65, 14, '+'],
      [10, 24, '.'], [72, 22, '.'], [6, 32, '*'], [74, 30, '+'],
      [18, 4, '.'], [62, 5, '.'], [22, 10, '+'], [58, 9, '*']
    ];
    sparkles.forEach(([sc, sr, sch], sIdx) => {
      const twinkle = 0.5 + 0.5 * Math.sin(elapsed * 4.5 + sIdx * 1.3);
      if (twinkle > 0.25) {
        this.ctx.fillStyle = `rgba(255, 235, 179, ${twinkle})`;
        this.ctx.fillText(sch, cakeLeft + sc * charW, cakeTop + sr * charH);
      }
    });
    
    this.ctx.restore();
  }
  
  // Backward compatibility alias
  renderHeart(elapsed, entranceProgress = 1.0, centerOffsetY = -50) {
    this.renderCake(elapsed, entranceProgress, centerOffsetY);
  }
  
  renderMessage(elapsed, msgFade = 1.0) {
    this.renderCake(elapsed, 1.0, -150);
    if (msgFade <= 0.005) return;
    
    const lines = [
      "Happy Birthday!",
      "To our precious little sunshine,",
      "Wishing you a lifetime of laughter & love,",
      "Happy Birthday! 🎂✨"
    ];
    
    const startY = this.height / 2.0 + 125;
    const fontSize = Math.min(32, Math.max(20, this.width * 0.045));
    const lineHeight = fontSize * 1.45;
    
    this.ctx.font = `bold ${fontSize}px Georgia, "Times New Roman", serif`;
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "middle";
    
    lines.forEach((text, i) => {
      const startT = i * 0.22;
      const endT = Math.min(1.0, startT + 0.35);
      let fade = 0.0;
      if (msgFade > startT) {
        if (msgFade >= endT) fade = 1.0;
        else {
          const p = (msgFade - startT) / (endT - startT);
          fade = p * p * (3.0 - 2.0 * p);
        }
      }
      if (fade > 0.01) {
        this.ctx.save();
        this.ctx.globalAlpha = fade;
        if (i === 0) {
          // Luminous celebration gold
          this.ctx.fillStyle = "#ffd700";
          this.ctx.shadowColor = "rgba(255, 215, 0, 0.6)";
          this.ctx.shadowBlur = 10;
        } else if (i === 3) {
          // Radiant rose pink
          this.ctx.fillStyle = "#ff5a91";
          this.ctx.shadowColor = "rgba(255, 90, 145, 0.6)";
          this.ctx.shadowBlur = 12;
        } else {
          this.ctx.fillStyle = "#ffeef5";
        }
        this.ctx.fillText(text, this.width / 2.0, startY + i * lineHeight);
        this.ctx.restore();
      }
    });
  }
  
  loop() {
    if (!this.started) return;
    const now = performance.now() / 1000.0;
    const elapsed = now - this.startTime;
    
    this.ctx.fillStyle = "#000000";
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    const centerX = (this.width - this.portraitW) / 2.0;
    const centerY = (this.height - this.portraitH) / 2.0;
    
    if (elapsed < T_DARKNESS_END) {
      if (elapsed > 0.8) {
        const p = (elapsed - 0.8) / (T_DARKNESS_END - 0.8);
        const surf = this.renderGridToCanvas(this.baseGrid, p * 0.04, this.revealOrder);
        this.ctx.drawImage(surf, centerX, centerY);
      }
    } else if (elapsed < T_REVEAL_END) {
      const p = (elapsed - T_DARKNESS_END) / (T_REVEAL_END - T_DARKNESS_END);
      const surf = this.renderGridToCanvas(this.baseGrid, p, this.revealOrder);
      this.ctx.drawImage(surf, centerX, centerY);
    } else if (elapsed < T_APPRECIATE_END) {
      this.ctx.drawImage(this.openPortraitCanvas, centerX, centerY);
    } else if (elapsed < T_BLINK_END) {
      const p = (elapsed - T_APPRECIATE_END) / (T_BLINK_END - T_APPRECIATE_END);
      const idx = Math.min(this.blinkCanvases.length - 1, Math.round(p * (this.blinkCanvases.length - 1)));
      this.ctx.drawImage(this.blinkCanvases[idx], centerX, centerY);
    } else if (elapsed < T_POST_BLINK_END) {
      this.ctx.drawImage(this.openPortraitCanvas, centerX, centerY);
    } else if (elapsed < T_ZOOM_END) {
      const p = (elapsed - T_POST_BLINK_END) / (T_ZOOM_END - T_POST_BLINK_END);
      this.renderZoom(p);
      if (p > 0.70) {
        const cakeP = (p - 0.70) / 0.30;
        this.renderCake(elapsed, cakeP * 0.85);
      }
    } else if (elapsed < T_HEART_ONLY_END) {
      const p = (elapsed - T_ZOOM_END) / (T_HEART_ONLY_END - T_ZOOM_END);
      const currentEntrance = 0.85 + 0.15 * Math.min(1.0, p * 2.0);
      this.renderCake(elapsed, currentEntrance);
    } else if (elapsed < T_FINAL_END) {
      const p = Math.min(1.0, (elapsed - T_HEART_ONLY_END) / 3.0);
      this.renderMessage(elapsed, p);
    } else {
      this.renderMessage(elapsed, 1.0);
    }
    
    requestAnimationFrame(() => this.loop());
  }
}

window.addEventListener("DOMContentLoaded", () => {
  new EyeWebAnimation();
});
