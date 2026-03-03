const canvas = document.getElementById('magic-canvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = [];

const colors = [
    '#eef4e5', '#67c69e', '#fedf74', '#80acc9',
    '#f7a4b0', '#f8d17f', '#73a8d2', '#c9a3d0',
    '#b6d7a8', '#f4cccc', '#c9daf8', '#d9ead3'
];

class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = Math.random() * 7 + 3;
        this.speedX = Math.random() * 3 - 1.5;
        this.speedY = Math.random() * 3 - 1.5;
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.life = 1;
        this.decay = 0.02;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        this.life -= this.decay;
        if (this.size > 0.2) {
            this.size -= 0.1;
        }
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.life;
        ctx.shadowBlur = 15;
        ctx.shadowColor = this.color;
        ctx.fill();
        ctx.closePath();
    }
}

function handleParticles(e) {
    for (let i = 0; i < 5; i++) {
        particles.push(new Particle(e.x, e.y));
    }
}

function animate() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.shadowBlur = 0;

    for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();

        if (particles[i].life <= 0 || particles[i].size <= 0.2) {
            particles.splice(i, 1);
            i--;
        }
    }

    requestAnimationFrame(animate);
}

window.addEventListener('mousemove', handleParticles);


function handleTouch(e) {
   
    const touches = e.changedTouches;
    for (let i = 0; i < touches.length; i++) {
        const touch = touches[i];
        handleParticles({ x: touch.clientX, y: touch.clientY });
    }
}

window.addEventListener('touchstart', handleTouch, { passive: false });
window.addEventListener('touchmove', handleTouch, { passive: false });

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

animate();
