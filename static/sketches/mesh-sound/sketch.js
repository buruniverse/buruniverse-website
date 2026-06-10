let particlesA = []; 
let particlesB = []; 
const numA = 800;
const spacing = 20;
let polySynth; // 音声エンジン

let noiseOsc; // 風の音用

function setup() {
  createCanvas(windowWidth, windowHeight);
  background(245, 245, 240);
  
  // 1. 鈴虫の音（サイン波）の設定
  osc = new p5.Oscillator('sine');
  osc.amp(0);
  osc.start();

  // 2. 微風の音（低域のノイズ）の設定
  noiseOsc = new p5.Noise('brown'); // 柔らかいブラウンノイズ
  noiseOsc.amp(0.07); // 常に微かに鳴っている背景音
  noiseOsc.start();

  for (let i = 0; i < numA; i++) {
    particlesA.push(new ParticleA());
  }

  for (let y = 0; y <= height; y += spacing) {
    for (let x = 0; x <= width; x += spacing) {
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

// ユーザーが画面をクリックした際にオーディオコンテキストを開始
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
        // 修正：発火確率を10%に制限（10分の1に間引く）
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
    // 鈴虫っぽい高い周波数（2000Hz〜5000Hz）
    let freq = map(this.pos.y, height, 0, 200, 4000);
    osc.freq(freq);
    
    // 鈴虫の羽の震えをシミュレート（高速なエンベロープ）
    let time = 0.05; 
    // 音量をさらに控えめに（0.02程度）し、一瞬だけ鳴らす
    osc.amp(0.5, 0.01); 
    osc.amp(0, 0.05);    // 0.05秒で消音
    
    // 【修正】ここに書いてあった noiseOsc.amp(...) を削除しました。
    // これにより、風の音は setup で設定した一定音量（0.02）のままになります。
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
      // 修正：ドットの濃さを線の約2倍（0.6〜0.8）に強調
      fill(140, 140, 140, 255 * 0.9 * (this.glowLevel / 255)); 
      ellipse(this.pos.x, this.pos.y, 1.5);
    } else {
      fill(this.baseColor);
      ellipse(this.pos.x, this.pos.y, 0.6);
    }
  }
}

// ParticleA, windowResized は前回のまま
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
function windowResized() { resizeCanvas(windowWidth, windowHeight); }
