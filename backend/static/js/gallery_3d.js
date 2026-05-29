/**
 * Section 25: 3D Food Gallery with Three.js
 * Creates a stunning 3D card carousel for the gallery page.
 * Falls back gracefully if WebGL is not available.
 */

class FoodGallery3D {
    constructor(container, images) {
        this.container = typeof container === 'string' 
            ? document.getElementById(container) : container;
        this.images = images || [];
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.cards = [];
        this.currentAngle = 0;
        this.targetAngle = 0;
        this.isActive = false;
        this.isDragging = false;
        this.lastX = 0;
        this.radius = 5;

        this.init();
    }

    init() {
        // Check WebGL support
        if (!this.isWebGLAvailable()) {
            this.showFallback();
            return;
        }

        if (this.images.length === 0) {
            this.container.innerHTML = '<p style="text-align:center;color:#666;padding:40px;">No gallery items to display in 3D.</p>';
            return;
        }

        this.setupScene();
        this.createCards();
        this.addLights();
        this.setupControls();
        this.animate();
        this.isActive = true;
    }

    isWebGLAvailable() {
        try {
            const canvas = document.createElement('canvas');
            return !!(window.WebGLRenderingContext && 
                     (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        } catch (e) {
            return false;
        }
    }

    setupScene() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0d0d0d);
        this.scene.fog = new THREE.Fog(0x0d0d0d, 8, 15);

        // Camera
        const aspect = this.container.clientWidth / Math.max(this.container.clientHeight, 400);
        this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 100);
        this.camera.position.set(0, 1, 7);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, Math.max(this.container.clientHeight, 400));
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.container.appendChild(this.renderer.domElement);

        // Handle resize
        window.addEventListener('resize', () => this.onResize());
    }

    createCards() {
        const loader = new THREE.TextureLoader();
        const count = Math.min(this.images.length, 12); // Max 12 cards
        const angleStep = (Math.PI * 2) / count;

        for (let i = 0; i < count; i++) {
            const angle = i * angleStep;
            const img = this.images[i];

            // Card geometry (rounded rectangle effect)
            const geometry = new THREE.BoxGeometry(2, 2.8, 0.05);
            
            // Create material with image texture
            const material = new THREE.MeshStandardMaterial({
                color: 0x1a1a1a,
                roughness: 0.3,
                metalness: 0.7,
            });

            // Load texture
            if (img.url && img.media_type === 'image') {
                loader.load(img.url, (texture) => {
                    texture.colorSpace = THREE.SRGBColorSpace;
                    material.map = texture;
                    material.needsUpdate = true;
                }, undefined, () => {
                    // On error, use gold color
                    material.color.setHex(0x1a1a1a);
                });
            }

            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.x = Math.cos(angle) * this.radius;
            mesh.position.z = Math.sin(angle) * this.radius;
            mesh.position.y = 0;
            mesh.lookAt(0, 0, 0);
            mesh.castShadow = true;
            mesh.userData = { title: img.title, index: i };

            // Gold border frame
            const frameMaterial = new THREE.MeshStandardMaterial({
                color: 0xd4af37,
                metalness: 0.9,
                roughness: 0.1,
            });
            const frameGeometry = new THREE.BoxGeometry(2.1, 2.9, 0.02);
            const frame = new THREE.Mesh(frameGeometry, frameMaterial);
            frame.position.z = -0.04;
            mesh.add(frame);

            // Title text sprite
            const titleSprite = this.createTextSprite(img.title || 'Untitled');
            titleSprite.position.y = -1.7;
            mesh.add(titleSprite);

            this.cards.push(mesh);
            this.scene.add(mesh);
        }
    }

    createTextSprite(text) {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, 256, 64);
        
        ctx.font = 'bold 18px Inter, sans-serif';
        ctx.fillStyle = '#d4af37';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text.substring(0, 25), 128, 32);

        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
        const sprite = new THREE.Sprite(material);
        sprite.scale.set(2, 0.5, 1);
        return sprite;
    }

    addLights() {
        // Ambient light
        const ambient = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambient);

        // Spotlight (golden)
        const spotlight = new THREE.SpotLight(0xd4af37, 2, 20, Math.PI / 4);
        spotlight.position.set(0, 8, 0);
        spotlight.castShadow = true;
        this.scene.add(spotlight);

        // Point lights
        const pointLight1 = new THREE.PointLight(0xd4af37, 1, 15);
        pointLight1.position.set(5, 3, 5);
        this.scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0xffffff, 0.5, 15);
        pointLight2.position.set(-5, 3, -5);
        this.scene.add(pointLight2);

        // Ground plane
        const groundGeometry = new THREE.CircleGeometry(8, 32);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x111111,
            roughness: 0.8,
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -2;
        ground.receiveShadow = true;
        this.scene.add(ground);
    }

    setupControls() {
        const el = this.renderer.domElement;

        // Mouse drag
        el.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.lastX = e.clientX;
        });

        window.addEventListener('mousemove', (e) => {
            if (!this.isDragging) return;
            const dx = e.clientX - this.lastX;
            this.targetAngle += dx * 0.005;
            this.lastX = e.clientX;
        });

        window.addEventListener('mouseup', () => {
            this.isDragging = false;
        });

        // Touch support
        el.addEventListener('touchstart', (e) => {
            this.isDragging = true;
            this.lastX = e.touches[0].clientX;
        });

        el.addEventListener('touchmove', (e) => {
            if (!this.isDragging) return;
            const dx = e.touches[0].clientX - this.lastX;
            this.targetAngle += dx * 0.005;
            this.lastX = e.touches[0].clientX;
        });

        el.addEventListener('touchend', () => {
            this.isDragging = false;
        });

        // Auto-rotate
        if (!this.isDragging) {
            this.autoRotate = true;
        }
    }

    animate() {
        if (!this.isActive) return;
        requestAnimationFrame(() => this.animate());

        // Auto-rotate when not dragging
        if (!this.isDragging) {
            this.targetAngle += 0.002;
        }

        // Smooth lerp
        this.currentAngle += (this.targetAngle - this.currentAngle) * 0.05;

        // Update card positions
        const count = this.cards.length;
        const angleStep = (Math.PI * 2) / count;

        for (let i = 0; i < count; i++) {
            const angle = i * angleStep + this.currentAngle;
            const card = this.cards[i];
            card.position.x = Math.cos(angle) * this.radius;
            card.position.z = Math.sin(angle) * this.radius;
            card.lookAt(0, 0, 0);

            // Scale based on distance to camera
            const distToCamera = card.position.distanceTo(this.camera.position);
            const scale = THREE.MathUtils.clamp(1 - (distToCamera - 5) * 0.1, 0.6, 1);
            card.scale.setScalar(scale);
        }

        this.renderer.render(this.scene, this.camera);
    }

    onResize() {
        if (!this.renderer) return;
        const w = this.container.clientWidth;
        const h = Math.max(this.container.clientHeight, 400);
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
    }

    showFallback() {
        this.container.innerHTML = `
            <div style="text-align:center; padding:40px; color:#999;">
                <p style="font-size:1.2rem; color:#d4af37; margin-bottom:10px;">
                    3D Gallery requires WebGL
                </p>
                <p>Your browser doesn't support 3D rendering. 
                   Please use a modern browser for the full experience.</p>
            </div>
        `;
    }

    destroy() {
        this.isActive = false;
        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
        }
    }
}
