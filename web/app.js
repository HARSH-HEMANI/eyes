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
    
    // Grid parameters
    this.targetCols = window.innerWidth < 768 ? 140 : 200;
    this.charW = 6;
    this.charH = 11;
    this.pupilNormX = 0.4629;
    this.pupilNormY = 0.4115;
    
    this.baseGrid = null;
    this.openPortraitCanvas = null;
    this.blinkCanvases = [];
    this.masterHeartCanvas = null;
    
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
    
    this.cols = this.targetCols;
    this.rows = Math.max(10, Math.round(this.cols / (imgAspect * (this.charH / this.charW))));
    
    this.portraitW = this.cols * this.charW;
    this.portraitH = this.rows * this.charH;
    
    this.pupilSurfaceX = this.pupilNormX * this.portraitW;
    this.pupilSurfaceY = this.pupilNormY * this.portraitH;
    
    // Sample base image
    this.baseGrid = this.processImage(this.img);
    this.openPortraitCanvas = this.renderGridToCanvas(this.baseGrid, 1.0);
    
    // Precompute reveal order (radial + matrix droplets)
    this.revealOrder = this.generateRevealOrder();
    
    // Precompute eyelid blink stages
    this.blinkCanvases = this.precomputeBlinkFrames(10);
    
    // Precompute master ASCII heart
    this.masterHeartCanvas = this.precomputeMasterHeart();
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
        
        let char = " ";
        if (lum > 14) {
          const rampIdx = Math.min(rampLen - 1, Math.floor((lum / 255.0) * (rampLen - 1)));
          char = ASCII_RAMP[rampIdx];
        }
        
        cells.push({
          c, r,
          char,
          color: `rgb(${red},${green},${blue})`,
          x: c * this.charW,
          y: r * this.charH,
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
    
    ctx.font = `bold ${this.charH - 1}px Consolas, monospace`;
    ctx.textBaseline = "top";
    
    const total = cells.length;
    const visibleCount = Math.round(total * Math.max(0, Math.min(1, revealProgress)));
    const indices = revealOrder ? revealOrder.slice(0, visibleCount) : Array.from({ length: visibleCount }, (_, i) => i);
    
    for (let i = 0; i < indices.length; i++) {
      const cell = cells[indices[i]];
      if (cell.char !== " ") {
        ctx.fillStyle = cell.color;
        ctx.fillText(cell.char, cell.x, cell.y);
      }
    }
    return c;
  }
  
  generateRevealOrder() {
    const centerCol = this.pupilNormX * this.cols;
    const centerRow = this.pupilNormY * this.rows;
    const arFactor = this.charH / this.charW;
    
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
    if (closure <= 0.005) return sourceImg;
    
    const w = sourceImg.naturalWidth || sourceImg.width;
    const h = sourceImg.naturalHeight || sourceImg.height;
    
    const offCanvas = document.createElement("canvas");
    offCanvas.width = w;
    offCanvas.height = h;
    const ctx = offCanvas.getContext("2d");
    ctx.drawImage(sourceImg, 0, 0, w, h);
    
    // Draw smooth eyelid skin descent across eye opening
    const cx = this.pupilNormX * w;
    const cy = this.pupilNormY * h;
    const rx = 0.34 * w;
    const topY = cy - 0.12 * h;
    const botY = cy + 0.24 * h;
    
    const targetLidY = topY + closure * (botY - topY);
    
    // Stretch eyelid skin
    const skinSrcY = Math.max(0, topY - 0.20 * h);
    const skinH = Math.max(1, topY - skinSrcY);
    
    ctx.save();
    ctx.beginPath();
    ctx.ellipse(cx, targetLidY, rx, (targetLidY - skinSrcY) * 0.6, 0, 0, Math.PI * 2);
    ctx.clip();
    ctx.drawImage(sourceImg, 0, skinSrcY, w, skinH, 0, skinSrcY, w, targetLidY - skinSrcY + 5);
    ctx.restore();
    
    // Eyelash contour line
    ctx.strokeStyle = `rgba(30, 20, 25, ${0.7 * closure})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(cx, targetLidY, rx, 10, 0, 0, Math.PI);
    ctx.stroke();
    
    return offCanvas;
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
  
  precomputeMasterHeart() {
    const cols = 76;
    const rows = 38;
    const w = cols * this.charW;
    const h = rows * this.charH;
    
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    
    ctx.font = `bold ${this.charH - 1}px Consolas, monospace`;
    ctx.textBaseline = "top";
    
    const cx = w / 2;
    const cy = h / 2 + 10;
    
    function isClassicHeart(x, y) {
      if (y > 0.83 || y < -1.02) return false;
      const xAbs = Math.abs(x);
      if (y >= 0.20) {
        return (Math.pow((xAbs - 0.55) / 0.57, 2) + Math.pow((y - 0.20) / 0.63, 2)) <= 1.0;
      } else {
        const u = (0.20 - y) / 1.22;
        const xMax = 1.13 * (1.0 - u) * (1.0 + 0.16 * u);
        return xAbs <= xMax;
      }
    }
    
    const halfRows = rows / 2;
    const halfCols = cols / 2;
    
    for (let r = -halfRows; r <= halfRows; r++) {
      const y = (-r / halfRows) * 0.95;
      for (let c = -halfCols; c <= halfCols; c++) {
        const x = (c / halfCols) * 1.18;
        if (isClassicHeart(x, y)) {
          const dist = Math.sqrt(x * x + Math.pow(y - 0.2, 2));
          const red = 255;
          const green = Math.min(255, Math.floor(22 + dist * 90 + (y > 0.4 ? 50 : 0)));
          const blue = Math.min(255, Math.floor(62 + dist * 110 + (y > 0.4 ? 60 : 0)));
          
          const chIdx = Math.abs(c * 7 + r * 5) % HEART_CHARS.length;
          const ch = HEART_CHARS[chIdx];
          
          ctx.fillStyle = `rgb(${red},${green},${blue})`;
          ctx.fillText(ch, cx + c * this.charW - this.charW / 2, cy + r * this.charH - this.charH / 2);
        }
      }
    }
    return canvas;
  }
  
  calculateHeartbeat(t) {
    const period = 0.95;
    const phase = (t % period) / period;
    const beat1 = Math.exp(-Math.pow((phase - 0.12) / 0.065, 2)) * 0.11;
    const beat2 = Math.exp(-Math.pow((phase - 0.32) / 0.075, 2)) * 0.06;
    const breathe = Math.sin(phase * 2.0 * Math.PI) * 0.010;
    return 1.0 + beat1 + beat2 + breathe;
  }
  
  renderZoom(progress) {
    const p = Math.max(0, Math.min(1, progress));
    const t = p * p * p * (p * (p * 6.0 - 15.0) + 10.0);
    const currentScale = 1.0 + 27.0 * Math.pow(t, 1.8);
    
    const focusBlend = Math.min(1.0, t * 1.5);
    const focusX = (1.0 - focusBlend) * (this.portraitW / 2.0) + focusBlend * this.pupilSurfaceX;
    const focusY = (1.0 - focusBlend) * (this.portraitH / 2.0) + focusBlend * this.pupilSurfaceY;
    
    const viewW = Math.max(4.0, this.width / currentScale);
    const viewH = Math.max(4.0, this.height / currentScale);
    const srcX = focusX - viewW / 2.0;
    const srcY = focusY - viewH / 2.0;
    
    let alpha = 1.0;
    if (p > 0.65) {
      alpha = Math.max(0, 1.0 - (p - 0.65) / 0.35);
    }
    
    this.ctx.save();
    this.ctx.globalAlpha = alpha;
    this.ctx.imageSmoothingEnabled = currentScale < 3.0;
    this.ctx.drawImage(this.openPortraitCanvas, srcX, srcY, viewW, viewH, 0, 0, this.width, this.height);
    this.ctx.restore();
  }
  
  renderHeart(elapsed, entranceProgress = 1.0, centerOffsetY = -50) {
    const cx = this.width / 2.0;
    const cy = this.height / 2.0 + centerOffsetY;
    
    const beat = this.calculateHeartbeat(elapsed);
    const eScale = entranceProgress * entranceProgress * (3.0 - 2.0 * entranceProgress);
    const totalScale = beat * eScale;
    if (totalScale <= 0.01) return;
    
    const tw = this.masterHeartCanvas.width * totalScale;
    const th = this.masterHeartCanvas.height * totalScale;
    
    this.ctx.save();
    if (eScale < 0.99) this.ctx.globalAlpha = eScale;
    this.ctx.imageSmoothingEnabled = true;
    this.ctx.drawImage(this.masterHeartCanvas, cx - tw / 2, cy - th / 2, tw, th);
    this.ctx.restore();
  }
  
  renderMessage(elapsed, msgFade = 1.0) {
    this.renderHeart(elapsed, 1.0, -130);
    if (msgFade <= 0.005) return;
    
    const lines = [
      "I am sorry,",
      "Please, Give me this last chance,",
      "I want to be with you,",
      "Always With You!!!"
    ];
    
    const startY = this.height / 2.0 + 120;
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
        if (i === 3) {
          this.ctx.fillStyle = "#ff5a91";
          this.ctx.shadowColor = "rgba(255, 90, 145, 0.6)";
          this.ctx.shadowBlur = 12;
        } else if (i === 0) {
          this.ctx.fillStyle = "#ffeef5";
        } else {
          this.ctx.fillStyle = "#fcf2f8";
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
        const heartP = (p - 0.70) / 0.30;
        this.renderHeart(elapsed, heartP * 0.85);
      }
    } else if (elapsed < T_HEART_ONLY_END) {
      const p = (elapsed - T_ZOOM_END) / (T_HEART_ONLY_END - T_ZOOM_END);
      const currentEntrance = 0.85 + 0.15 * Math.min(1.0, p * 2.0);
      this.renderHeart(elapsed, currentEntrance);
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
