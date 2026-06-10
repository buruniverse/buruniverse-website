let particlesA = []; 
let particlesB = []; 
const numA = 800;
const spacing = 20;
let osc, noiseOsc; 

function setup() {
  // 【設定：画面サイズ】
  // YouTube(16:9)なら (1920, 1080)
  // スマホ(9:16)なら (1080, 1920) 
  // ブラウザいっぱいにしたいなら (windowWidth, windowHeight)
  createCanvas(windowWidth, windowHeight); 
  
  background(245, 245, 240);
  
  osc = new p5.Oscillator('sine');
  osc.amp(0);
  osc.start();

  noiseOsc = new p5.Noise('brown');
  noiseOsc.amp(0.02);
  noiseOsc.start();

  for (let i = 0; i < numA; i++) {
    particlesA.push(new ParticleA());
  }

  // 【修正：メッシュの生成範囲】
  // widthやheightにspacingを足すことで、画面端の描画漏れを防ぎます
  particlesB = []; // 初期化
  for (let y = 0; y <= height + spacing; y += spacing) {
    for (let x = 0; x <= width + spacing; x += spacing) {
      particlesB.push(new ParticleB(x, y));
    }
  }
}

function draw() {
  background(245, 245, 240, 25);

  particlesB.forEach((pb, index) => {
    pb.interact(particlesA);
    pb.connectAllDirections(particlesB, index);
    pb.display();
  });

  particlesA.forEach(pa => {
    pa.update();
    pa.display();
  });
}

// 【追加：キー操作による保存】
function keyPressed() {
  // キーボードの 's' を押すとPNG画像として保存（高解像度書き出し）
  if (key === 's' || key === 'S') {
    saveCanvas('exhaust_design_log', 'png');
  }
}

function mousePressed() {
  userStartAudio();
}

class ParticleB {
  constructor(x, y) {
    this.pos = createVector(x, y);
    this.glowLevel = 0;
    this.baseColor = color(200, 200, 200, 255 * 0.35);
  }

  interact(others) {
    for (let i = 0; i < others.length; i += 15) { 
      let dSq = (this.pos.x - others[i].pos.x)**2 + (this.pos.y - others[i].pos.y)**2;
      if (dSq < 800) { 
        if (this.glowLevel < 50 && random(1) < 0.005) { 
          this.playPulse();
        }
        this.glowLevel = 255;
        break;
      }
    }
    this.glowLevel *= 0.92;
  }

  playPulse() {
    let freq = map(this.pos.y, height, 0, 200, 4000);
    osc.freq(freq);
    osc.amp(0.05, 0.01); 
    osc.amp(0, 0.05);
  }

  connectAllDirections(allB, myIndex) {
    if (this.glowLevel < 30) return;
    let searchRange = 100; 
    let start = max(0, myIndex - searchRange);
    let end = min(allB.length, myIndex + searchRange);

    for (let i = start; i < end; i++) {
      let other = allB[i];
      let dx = abs(this.pos.x - other.pos.x);
      let dy = abs(this.pos.y - other.pos.y);
      if ((dx <= spacing + 1 && dy <= spacing + 1) && (dx > 0 || dy > 0)) {
        if (other.glowLevel > 30) {
          let alphaBase = this.glowLevel / 255;
          if (dx > 0 && dy > 0) {
            stroke(170, 170, 170, 255 * 0.09 * alphaBase); 
          } else if (dy === 0) {
            stroke(170, 170, 170, 255 * 0.08 * alphaBase); 
          } else if (dx === 0) {
            stroke(170, 170, 170, 255 * 0.3 * alphaBase);  
          }
          strokeWeight(0.4);
          line(this.pos.x, this.pos.y, other.pos.x, other.pos.y);
        }
      }
    }
  }

  display() {
    noStroke();
    if (this.glowLevel > 10) {
      fill(140, 140, 140, 255 * 0.9 * (this.glowLevel / 255)); 
      ellipse(this.pos.x, this.pos.y, 1.5);
    } else {
      fill(this.baseColor);
      ellipse(this.pos.x, this.pos.y, 0.6);
    }
  }
}

class ParticleA {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = createVector(random(-1, 1), random(-1, 1));
    this.acc = createVector(0, 0);
    this.maxSpeed = random(0.5, 2);
    let colors = [
      color(131, 164, 200, 150), color(201, 132, 131, 150), 
      color(200, 189, 147, 150), color(100, 100, 100, 120)
    ];
    this.color = random(colors);
    this.size = random(1, 3);
  }
  update() {
    let mouse = createVector(mouseX, mouseY);
    let dir = p5.Vector.sub(mouse, this.pos);
    if (dir.mag() < 200) { dir.setMag(0.05); this.acc.add(dir); }
    let angle = noise(this.pos.x * 0.005, this.pos.y * 0.005, frameCount * 0.01) * TWO_PI * 2;
    let nVec = p5.Vector.fromAngle(angle).mult(0.15);
    this.acc.add(nVec);
    this.vel.add(this.acc).limit(this.maxSpeed);
    this.pos.add(this.vel);
    this.acc.mult(0);
    if (this.pos.x < 0) this.pos.x = width; else if (this.pos.x > width) this.pos.x = 0;
    if (this.pos.y < 0) this.pos.y = height; else if (this.pos.y > height) this.pos.y = 0;
  }
  display() { noStroke(); fill(this.color); ellipse(this.pos.x, this.pos.y, this.size); }
}

// 【注意：解像度を固定する場合はこの関数を無効化（コメントアウト）しても良いです】
function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  // リサイズ時にメッシュを再生成しないとズレるのでsetupを呼び出すか、
  // もしくは静止画書き出し時は触らないのが無難です。
}
