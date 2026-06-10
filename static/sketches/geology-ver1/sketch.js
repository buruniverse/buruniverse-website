let data = {
  "turbulence": 0.65,
  "inertia": 0.80,
  "crystallization": 0.70,
  "permeability": 0.30,
  "phase_transition": 0.55
};

let particles = [];
let t = 0;

function setup() {
  createCanvas(windowWidth, windowHeight);
  // 粒子数を少し調整（ブラウザの負荷を考慮）
  for (let i = 0; i < 200; i++) {
    particles.push(new Particle());
  }
}

function draw() {
  // Permeability（透過性）による「澱（おり）」の蓄積
  let alpha = map(data.permeability, 0, 1, 40, 5); 
  background(245, 245, 240, alpha); 

  // 相転移：臨界点を超えると画面がフラッシュし、過去の澱をリセットする
  if (random() < data.phase_transition * 0.02) {
    background(255, 255, 255, 100); // 瞬間的なホワイトアウト
  }

  t += 0.005;

  for (let i = 0; i < particles.length; i++) {
    particles[i].update();
    particles[i].show();
    
    // PhaseTransitionが高いと、フラクタル構造が壊れやすくなる
    if (random() > data.phase_transition) {
      for (let j = i + 1; j < particles.length; j++) {
        let d = dist(particles[i].pos.x, particles[i].pos.y, particles[j].pos.x, particles[j].pos.y);
        
        // 修正点：変数名を threshold から limitDist に変更
        let limitDist = data.crystallization * 80;
        if (d < limitDist) {
          drawOrganicLink(particles[i].pos, particles[j].pos, d, 3);
        }
      }
    }
  }
}

function drawOrganicLink(p1, p2, d, level) {
  if (level <= 0) return;

  let mid = p5.Vector.lerp(p1, p2, 0.5);
  let offset = p5.Vector.random2D().mult(d * 0.2 * data.turbulence);
  mid.add(offset);

  // 透過性（Permeability）が低いほど、線も少し「濁った」色に
  let strokeColor = map(data.permeability, 0, 1, 30, 80);
  stroke(strokeColor, strokeColor, strokeColor + 10, map(d, 0, 100, 150, 0));
  strokeWeight(level * 0.5);
  line(p1.x, p1.y, mid.x, mid.y);
  line(p2.x, p2.y, mid.x, mid.y);

  if (data.crystallization > 0.6) {
    drawOrganicLink(p1, mid, d * 0.5, level - 1);
  }
}

class Particle {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = createVector(0, 0);
  }

  update() {
    let n = noise(this.pos.x * 0.005, this.pos.y * 0.005, t);
    let angle = n * TWO_PI * 2;
    let flow = p5.Vector.fromAngle(angle).mult(data.inertia);
    
    let friction = p5.Vector.random2D().mult(data.turbulence * 0.5);
    flow.add(friction);
    
    this.vel.add(flow);
    this.vel.limit(2); 
    this.pos.add(this.vel);

    if (this.pos.x > width) this.pos.x = 0;
    if (this.pos.x < 0) this.pos.x = width;
    if (this.pos.y > height) this.pos.y = 0;
    if (this.pos.y < 0) this.pos.y = height;
  }

  show() {
    noStroke();
    // Turbulenceが高いと、わずかに「熱」を感じる色味に
    let r = 50 + data.turbulence * 100;
    let g = 60 + data.inertia * 20;
    let b = 70 + data.crystallization * 30;
    fill(r, g, b, 180);
    ellipse(this.pos.x, this.pos.y, 2);
  }
}
