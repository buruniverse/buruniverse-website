let particlesA = []; 
let particlesB = []; 
const numA = 800;
const spacing = 20;  // 修正：間隔を40から20へ（密度4倍）

function setup() {
  createCanvas(windowWidth, windowHeight);
  background(245, 245, 240);

  for (let i = 0; i < numA; i++) {
    particlesA.push(new ParticleA());
  }

  // メッシュを細密化（spacing=20）
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

class ParticleB {
  constructor(x, y) {
    this.pos = createVector(x, y);
    this.glowLevel = 0;
    this.baseColor = color(200, 200, 200, 255 * 0.35);
  }

  interact(others) {
    for (let i = 0; i < others.length; i += 15) { 
      let dSq = (this.pos.x - others[i].pos.x)**2 + (this.pos.y - others[i].pos.y)**2;
      if (dSq < 800) { // 密度向上に合わせて検知範囲を微調整
        this.glowLevel = 255;
        break;
      }
    }
    this.glowLevel *= 0.92;
  }

  connectAllDirections(allB, myIndex) {
    if (this.glowLevel < 30) return;

    // 密度4倍に伴い探索範囲を調整
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
          
          // 指定：線の透明度
          if (dx > 0 && dy > 0) {
            stroke(170, 170, 170, 255 * 0.09 * alphaBase); // 斜め (線の基本を半分に)
          } else if (dy === 0) {
            stroke(170, 170, 170, 255 * 0.08 * alphaBase); // 横
          } else if (dx === 0) {
            stroke(170, 170, 170, 255 * 0.3 * alphaBase);  // 縦
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

// ParticleA, windowResized は変更なし
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
