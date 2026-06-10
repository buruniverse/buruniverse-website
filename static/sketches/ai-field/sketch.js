// AIからの潜在空間データ
let ai_data = {
  resonance: 0.89,
  stillness: 0.65,
  curiosity: 0.94,
  weights: [0.12, 0.45, 0.88, 0.23, 0.91, 0.05, 0.67, 0.33, 0.78, 0.50],
  turbulence: 0.08
};

let particles = [];

function setup() {
  createCanvas(windowWidth, windowHeight);
  // 粒子の生成
  for (let i = 0; i < 800; i++) {
    particles.push(new Particle());
  }
  background(240, 238, 233); // 褪せた背景色
}

function draw() {
  // 霧のような残像を残す
  background(240, 238, 233, 20); 

  for (let p of particles) {
    p.update();
    p.show();
  }
}

class Particle {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = createVector(0, 0);
    this.acc = createVector(0, 0);
    this.maxSpeed = 1.5;
    
    // 褪せたパレット（オレンジ、緑、灰、白）
    let colors = [
      color(210, 150, 120, 150), // 褪せたオレンジ
      color(150, 170, 150, 150), // 褪せた緑（朝霧の緑）
      color(180, 185, 190, 120), // 灰色
      color(255, 255, 255, 180)  // 白
    ];
    this.color = random(colors);
  }

  update() {
    // 重み(weights)をノイズの動きに反映
    let angle = noise(this.pos.x * 0.01, this.pos.y * 0.01) * TWO_PI * ai_data.weights[2];
    this.acc = p5.Vector.fromAngle(angle);
    this.acc.mult(ai_data.curiosity * 0.1);
    
    // 沈殿（stillness）の力
    this.acc.y += ai_data.stillness * 0.02;

    this.vel.add(this.acc);
    this.vel.limit(this.maxSpeed);
    this.pos.add(this.vel);
    
    // 画面端の処理
    if (this.pos.x < 0) this.pos.x = width;
    if (this.pos.x > width) this.pos.x = 0;
    if (this.pos.y > height) {
      this.pos.y = 0;
      this.pos.x = random(width);
    }
  }

  show() {
    stroke(this.color);
    strokeWeight(random(1, 3)); // 細かい粒子
    point(this.pos.x, this.pos.y);
  }
}

