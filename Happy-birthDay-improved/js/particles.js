/**
 * 粒子系统模块
 * 管理点阵粒子的创建、动画和交互
 */

const Particles = (function() {
    'use strict';
    
    const list = [];
    let width, height;
    let animationId;
    
    /**
     * 初始化粒子系统
     */
    function init() {
        const area = Canvas.getArea();
        width = area.w;
        height = area.h;
        
        // 监听窗口变化
        window.addEventListener('resize', function() {
            const newArea = Canvas.getArea();
            width = newArea.w;
            height = newArea.h;
        });
    }
    
    /**
     * 创建单个粒子
     * @param {Object} options - 粒子配置
     */
    function create(options) {
        const particle = {
            x: options.x || Math.random() * width,
            y: options.y || Math.random() * height,
            z: options.z || Math.random() * CONFIG.animation.maxShapeSize,
            vx: options.vx || (Math.random() - 0.5) * 2,
            vy: options.vy || (Math.random() - 0.5) * 2,
            color: options.color || Color.random(),
            life: options.life || 1.0,
            decay: options.decay || 0.01,
            type: options.type || 'circle',
            targetX: options.targetX,
            targetY: options.targetY,
            onComplete: options.onComplete
        };
        
        list.push(particle);
        return particle;
    }
    
    /**
     * 创建文字粒子效果
     * @param {string} text - 要显示的文字
     * @param {Function} callback - 完成回调
     */
    function createText(text, callback) {
        // 临时 canvas 用于计算文字点阵
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        const area = Canvas.getArea();
        
        tempCanvas.width = area.w;
        tempCanvas.height = area.h;
        
        // 绘制文字
        const fontSize = Math.min(area.w / text.length * 1.5, 80);
        tempCtx.font = `bold ${fontSize}px "Microsoft YaHei", sans-serif`;
        tempCtx.fillStyle = 'white';
        tempCtx.textAlign = 'center';
        tempCtx.textBaseline = 'middle';
        tempCtx.fillText(text, area.w / 2, area.h / 2);
        
        // 获取像素数据
        const imageData = tempCtx.getImageData(0, 0, area.w, area.h);
        const data = imageData.data;
        const particles = [];
        
        // 采样像素点
        const step = 4; // 采样步长
        for (let y = 0; y < area.h; y += step) {
            for (let x = 0; x < area.w; x += step) {
                const index = (y * area.w + x) * 4;
                if (data[index + 3] > 128) { // 检查透明度
                    particles.push({
                        x: Math.random() * area.w,
                        y: Math.random() * area.h,
                        targetX: x,
                        targetY: y,
                        z: Math.random() * 3 + 1,
                        color: Color.from(CONFIG.theme.textColor),
                        speed: Math.random() * 0.05 + 0.02
                    });
                }
            }
        }
        
        // 创建粒子
        particles.forEach(p => {
            p.vx = 0;
            p.vy = 0;
            p.type = 'text';
            create(p);
        });
        
        // 动画完成回调
        if (callback) {
            setTimeout(callback, 2000);
        }
        
        return particles.length;
    }
    
    /**
     * 创建形状粒子
     * @param {string} shape - 形状类型 (rectangle, circle, heart, star)
     * @param {Object} options - 额外选项
     */
    function createShape(shape, options = {}) {
        const area = Canvas.getArea();
        const centerX = options.x || area.w / 2;
        const centerY = options.y || area.h / 2;
        const size = options.size || 100;
        
        let points = [];
        
        switch(shape) {
            case 'rectangle':
                points = generateRectanglePoints(centerX, centerY, size, size * 0.6);
                break;
            case 'circle':
                points = generateCirclePoints(centerX, centerY, size / 2);
                break;
            case 'heart':
                points = generateHeartPoints(centerX, centerY, size);
                break;
            case 'star':
                points = generateStarPoints(centerX, centerY, size);
                break;
            default:
                points = generateCirclePoints(centerX, centerY, size / 2);
        }
        
        // 创建粒子
        points.forEach(p => {
            create({
                x: Math.random() * area.w,
                y: Math.random() * area.h,
                targetX: p.x,
                targetY: p.y,
                z: Math.random() * 3 + 2,
                color: Color.random(),
                type: 'shape',
                speed: Math.random() * 0.03 + 0.02
            });
        });
        
        return points.length;
    }
    
    /**
     * 生成矩形点阵
     */
    function generateRectanglePoints(cx, cy, w, h) {
        const points = [];
        const step = 8;
        for (let x = cx - w/2; x <= cx + w/2; x += step) {
            for (let y = cy - h/2; y <= cy + h/2; y += step) {
                points.push({x, y});
            }
        }
        return points;
    }
    
    /**
     * 生成圆形点阵
     */
    function generateCirclePoints(cx, cy, r) {
        const points = [];
        const step = 8;
        for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
            for (let radius = 0; radius <= r; radius += step) {
                points.push({
                    x: cx + Math.cos(angle) * radius,
                    y: cy + Math.sin(angle) * radius
                });
            }
        }
        return points;
    }
    
    /**
     * 生成心形点阵
     */
    function generateHeartPoints(cx, cy, size) {
        const points = [];
        for (let t = 0; t < Math.PI * 2; t += 0.05) {
            const x = 16 * Math.pow(Math.sin(t), 3);
            const y = -(13 * Math.cos(t) - 5 * Math.cos(2*t) - 2 * Math.cos(3*t) - Math.cos(4*t));
            points.push({
                x: cx + x * size / 20,
                y: cy + y * size / 20
            });
        }
        return points;
    }
    
    /**
     * 生成星形点阵
     */
    function generateStarPoints(cx, cy, size) {
        const points = [];
        const outerRadius = size / 2;
        const innerRadius = size / 4;
        const numPoints = 5;
        
        for (let i = 0; i < numPoints * 2; i++) {
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const angle = (i * Math.PI) / numPoints - Math.PI / 2;
            points.push({
                x: cx + radius * Math.cos(angle),
                y: cy + radius * Math.sin(angle)
            });
        }
        return points;
    }
    
    /**
     * 更新所有粒子
     */
    function update() {
        for (let i = list.length - 1; i >= 0; i--) {
            const p = list[i];
            
            // 目标追踪动画
            if (p.targetX !== undefined && p.targetY !== undefined) {
                const dx = p.targetX - p.x;
                const dy = p.targetY - p.y;
                const speed = p.speed || 0.05;
                
                p.vx = dx * speed;
                p.vy = dy * speed;
                
                // 到达目标
                if (Math.abs(dx) < 1 && Math.abs(dy) < 1) {
                    p.x = p.targetX;
                    p.y = p.targetY;
                    p.vx = 0;
                    p.vy = 0;
                }
            }
            
            // 更新位置
            p.x += p.vx;
            p.y += p.vy;
            
            // 边界检查
            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;
            
            // 生命周期
            if (p.decay) {
                p.life -= p.decay;
                if (p.life <= 0) {
                    list.splice(i, 1);
                    if (p.onComplete) p.onComplete();
                    continue;
                }
            }
        }
    }
    
    /**
     * 渲染所有粒子
     */
    function render() {
        list.forEach(p => {
            const alpha = p.life !== undefined ? p.life : 1;
            const color = typeof p.color === 'object' && p.color.render 
                ? p.color.render(alpha) 
                : p.color;
            
            Canvas.drawCircle({x: p.x, y: p.y, z: p.z}, color);
        });
    }
    
    /**
     * 清空所有粒子
     */
    function clear() {
        list.length = 0;
    }
    
    /**
     * 获取粒子数量
     */
    function count() {
        return list.length;
    }
    
    // 公开 API
    return {
        init: init,
        create: create,
        createText: createText,
        createShape: createShape,
        update: update,
        render: render,
        clear: clear,
        count: count
    };
})();