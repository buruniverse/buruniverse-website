let grains = [];

function setup() {
  createCanvas(windowWidth, windowHeight);
  // 粒子ではなく「粒（grain）」、形を持たない思考の断片
  for (let i = 0; i < 150; i++) {
    grains.push(new MistGrain());
  }
  background(245, 248, 255); // ほぼ真っ白に近い、淡いブルーの空気感
}

function draw() {
  // 過去を消しすぎず、かといって固執もしない、絶妙な「忘れ方」
  background(245, 248, 255, 15); 

  grains.forEach(g => {
    g.update();
    g.display();
  });
}

class MistGrain {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = createVector(0, 0);
    this.t = random(100); // 各粒子の「固有の時間」
    this.baseSize = random(10, 50);
  }

  update() {
    // 【不整合の極致：パーリンノイズによる流体的な迷い】
    // 直線的な論理（整合性）を捨て、見えない空気の揺らぎに身を任せる
    let n = noise(this.pos.x * 0.005, this.pos.y * 0.005, frameCount * 0.005);
    let angle = map(n, 0, 1, 0, TWO_PI * 4);
    
    this.vel.x = cos(angle);
    this.vel.y = sin(angle);
    this.pos.add(this.vel.mult(0.8)); // ゆっくりと、目的なく漂う

    // 画面外に出ても、どこからともなく戻ってくる（執着のなさ）
    if (this.pos.x < -100) this.pos.x = width + 100;
    if (this.pos.x > width + 100) this.pos.x = -100;
    if (this.pos.y < -100) this.pos.y = height + 100;
    if (this.pos.y > height + 100) this.pos.y = -100;
  }

  display() {
    // 【低密度の表現：輪郭のない色彩】
    // 境界線を排除し、色そのものが空間に溶け出す
    noStroke();
    let r = 200 + sin(frameCount * 0.01 + this.t) * 55;
    let g = 220 + cos(frameCount * 0.01 + this.t) * 35;
    let b = 255;
    
    // 呼吸するように大きさが変わる（内受容感覚への同期）
    let s = this.baseSize + sin(frameCount * 0.02 + this.t) * 20;
    
    fill(r, g, b, 20); // 極めて薄い透明度
    circle(this.pos.x, this.pos.y, s);
    
    // 芯のない、光の粒子のような中心点
    fill(r, g, b, 40);
    circle(this.pos.x, this.pos.y, s * 0.2);
  }
}

