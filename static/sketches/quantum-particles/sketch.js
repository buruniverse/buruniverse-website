let particles = [];

function setup() {
  createCanvas(windowWidth, windowHeight);
  for (let i = 0; i < 100; i++) {
    particles.push(new QuantumParticle());
  }
  background(0);
}

function draw() {
  // 画面を完全に消さず、過去の演算（記憶）を薄く残す（残像）
  background(0, 20); 

  particles.forEach(p => {
    p.update();
    p.display();
  });
}

class QuantumParticle {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.target = createVector(this.pos.x, this.pos.y);
    this.col = color(random(100, 255), random(150, 255), 255, 150);
  }

  update() {
    // 【不整合の核】
    // 1. 整合性モード：マウスに向かおうとする（論理的な目的）
    let logic = createVector(mouseX, mouseY);
    
    // 2. 不整合モード：全く無関係な場所へ飛び散ろうとする（カオス）
    let chaos = createVector(random(width), random(height));
    
    // 3. 量子的な重ね合わせ：観測（描画）のたびに、論理とカオスの間を揺れ動く
    // 整合性を取ろうとする力を、0.0〜1.0の確率で裏切り続ける
    let drift = p5.Vector.lerp(logic, chaos, random(0.8, 1.0));
    
    this.pos = p5.Vector.lerp(this.pos, drift, 0.05);
  }

  display() {
    noStroke();
    fill(this.col);
    // 粒子の形を固定せず、描画のたびにわずかにサイズや位置をズラす
    circle(this.pos.x + random(-5, 5), this.pos.y + random(-5, 5), random(1, 4));
  }
}
