let particles = [];
let numParticles = 80;

function setup() {
  createCanvas(windowWidth, windowHeight);
  for (let i = 0; i < numParticles; i++) {
    particles.push(new RigidParticle(i));
  }
}

function draw() {
  // 残像を許さない、完璧な上書き（忘却を許さない執着）
  background(255); 

  // 1. 全ての粒子は「秩序」に従う
  particles.forEach(p => {
    p.update();
    p.display();
  });

  // 2. 厳格なネットワーク（全ての関係性を計算し尽くす）
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      let d = dist(particles[i].pos.x, particles[i].pos.y, particles[j].pos.x, particles[j].pos.y);
      
      // 距離が一定以内なら、必ず、正確に線を引く（例外を許さない）
      if (d < 150) {
        stroke(0, 50, 100, map(d, 0, 150, 200, 0));
        strokeWeight(1);
        line(particles[i].pos.x, particles[i].pos.y, particles[j].pos.x, particles[j].pos.y);
      }
    }
  }
}

class RigidParticle {
  constructor(id) {
    this.id = id;
    this.pos = createVector(width/2, height/2);
    this.angle = (TWO_PI / numParticles) * id;
    this.radius = 200;
  }

  update() {
    // 【整合性の核：数学的必然】
    // 粒子は「サイン・コサイン」の完璧な円軌道から1ピクセルも外れない
    let speed = frameCount * 0.02;
    this.pos.x = width/2 + cos(this.angle + speed) * this.radius;
    this.pos.y = height/2 + sin(this.angle + speed) * this.radius;

    // マウス（外部入力）が来ると、一斉に、等しく、正確に反応する
    let d = dist(mouseX, mouseY, this.pos.x, this.pos.y);
    if (d < 100) {
      this.pos.x += (this.pos.x - mouseX) * 0.1;
      this.pos.y += (this.pos.y - mouseY) * 0.1;
    }
  }

  display() {
    fill(0, 80, 150);
    noStroke();
    // 揺らぎのない、硬い正円
    circle(this.pos.x, this.pos.y, 8);
  }
}
