let groupA = []; 
let groupB = []; 
const numA = 4500; 
const spacing = 18; 

function setup() {
  createCanvas(windowWidth, windowHeight);
  for (let i = 0; i < numA; i++) groupA.push(new ParticleA());
  
  // グリッドを2次元配列的に管理できるよう配置
  for (let x = spacing/2; x < width; x += spacing) {
    for (let y = spacing/2; y < height; y += spacing) {
      groupB.push(new ParticleB(x, y));
    }
  }
}

function draw() {
  background(245, 245, 240, 20); 

  groupA.forEach(a => {
    a.update();
    a.display();
  });

  groupB.forEach((b, index) => {
    b.interact(groupA);
    // 発火レベルが高い時だけ、全方位の近隣を探索
    if (b.glowLevel > 40) {
      b.connectAllDirections(groupB, index);
    }
    b.display();
  });
}

class ParticleA {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = p5.Vector.random2D();
    this.acc = createVector(0, 0); // 初期化を確実に
    this.maxSpeed = 3.2;
    let palette = [
      color(220, 80, 70, 180),  color(230, 190, 80, 180), 
      color(130, 130, 140, 180), color(60, 90, 140, 180)
    ];
    this.color = random(palette);
    this.size = random(1.2, 1.8);
  }

  update() {
    let center = createVector(width/2, height/2);
    let toCenter = p5.Vector.sub(center, this.pos);
    
    // 渦の力を安全に計算
    let orbit = createVector(-toCenter.y, toCenter.x);
    orbit.normalize();
    orbit.mult(0.55);
    this.acc.add(orbit);
    
    let pulse = sin(frameCount * 0.015) * 0.22;
    let pForce = toCenter.copy().normalize().mult(pulse);
    this.acc.add(pForce);

    let n = noise(this.pos.x * 0.006, this.pos.y * 0.006, frameCount * 0.01);
    let nVec = p5.Vector.fromAngle(n * TWO_PI * 2.5).mult(0.35);
    this.acc.add(nVec);

    this.vel.add(this.acc).limit(this.maxSpeed);
    this.pos.add(this.vel);
    this.acc.mult(0);

    if (this.pos.x < 0) this.pos.x = width;
    if (this.pos.x > width) this.pos.x = 0;
    if (this.pos.y < 0) this.pos.y = height;
    if (this.pos.y > height) this.pos.y = 0;
  }

  display() {
    noStroke();
    fill(this.color);
    ellipse(this.pos.x, this.pos.y, this.size);
  }
}

class ParticleB {
  constructor(x, y) {
    this.pos = createVector(x, y);
    this.glowLevel = 0;
    this.baseColor = color(200, 200, 200, 35);
  }

  interact(others) {
    for (let i = 0; i < others.length; i += 120) { 
      let dSq = (this.pos.x - others[i].pos.x)**2 + (this.pos.y - others[i].pos.y)**2;
      if (dSq < 1200) { 
        this.glowLevel = 255;
        break;
      }
    }
    this.glowLevel *= 0.9;
  }

  // 全方位（縦横斜め）を探索する新しいメソッド
  connectAllDirections(allB, myIndex) {
    // 1次元配列の中で「物理的に近い」点を探すために探索範囲を広げる
    let searchRange = 60; 
    let start = max(0, myIndex - searchRange);
    let end = min(allB.length, myIndex + searchRange);

    for (let i = start; i < end; i++) {
      if (i === myIndex) continue;
      let other = allB[i];
      let d = dist(this.pos.x, this.pos.y, other.pos.x, other.pos.y);
      
      // 隣接ノード（斜め含む）に限定して線を引く
      if (d < spacing * 1.5 && other.glowLevel > 30) {
        stroke(170, 170, 170, this.glowLevel * 0.5);
        strokeWeight(0.4);
        line(this.pos.x, this.pos.y, other.pos.x, other.pos.y);
        
        if (this.glowLevel > 220) other.glowLevel += 2;
      }
    }
  }

  display() {
    noStroke();
    if (this.glowLevel > 10) {
      fill(140, 140, 140, this.glowLevel);
      ellipse(this.pos.x, this.pos.y, 1.8);
    } else {
      fill(this.baseColor);
      ellipse(this.pos.x, this.pos.y, 0.8);
    }
  }
}
