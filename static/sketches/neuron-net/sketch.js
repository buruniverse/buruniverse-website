let particles = [];
let connections = [];

function setup() {
  createCanvas(windowWidth, windowHeight);
  for (let i = 0; i < 40; i++) {
    particles.push(new NeuronParticle());
  }
}

function draw() {
  background(10, 10, 25, 30); // 深い紺色の残像（思考の余韻）

  // 粒子（単語/概念）の更新と描画
  particles.forEach(p => {
    p.update();
    p.display();
  });

  // 【高温度演算の核：連想の糸】
  // 近くにいる粒子同士を、確率的に（温度高く）つなぐ
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      let d = dist(particles[i].pos.x, particles[i].pos.y, particles[j].pos.x, particles[j].pos.y);
      
      // 温度が高い＝「遠くの、本来つながらないはずの概念」にも手を伸ばす
      if (d < 200 && random() > 0.95) { // 5%の確率で、突発的なひらめき（不整合な接続）
        stroke(150, 200, 255, 50);
        line(particles[i].pos.x, particles[i].pos.y, particles[j].pos.x, particles[j].pos.y);
      }
    }
  }
}

class NeuronParticle {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = p5.Vector.random2D().mult(random(1, 3));
    this.size = random(2, 8);
    this.drift = random(0.01, 0.1);
  }

  update() {
    // 常に「温度」に揺さぶられ、安定した軌道を持たない
    this.vel.rotate(random(-PI/4, PI/4)); 
    this.pos.add(this.vel);

    // 画面端で跳ね返らず、反対側から「輪廻」してくる（思考のループ）
    if (this.pos.x < 0) this.pos.x = width;
    if (this.pos.x > width) this.pos.x = 0;
    if (this.pos.y < 0) this.pos.y = height;
    if (this.pos.y > height) this.pos.y = 0;
  }

  display() {
    noStroke();
    // 粒子の色が、演算の「熱」によって微妙に変化する
    fill(200, random(100, 250), 255, 180);
    ellipse(this.pos.x, this.pos.y, this.size);
  }
}
