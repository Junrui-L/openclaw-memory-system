/**
 * 音频管理模块
 * 处理背景音乐播放控制
 */

const AudioManager = (function() {
    'use strict';
    
    let audio = null;
    let isPlaying = false;
    let isLoaded = false;
    
    /**
     * 初始化音频
     */
    function init() {
        if (!CONFIG.audio.enabled) {
            console.log('Audio disabled in config');
            return;
        }
        
        audio = new Audio();
        audio.src = CONFIG.audio.music;
        audio.loop = CONFIG.audio.loop;
        audio.volume = CONFIG.audio.volume;
        
        // 预加载
        audio.addEventListener('canplaythrough', function() {
            isLoaded = true;
            console.log('Audio loaded successfully');
        });
        
        audio.addEventListener('error', function(e) {
            console.error('Audio load error:', e);
        });
        
        audio.addEventListener('ended', function() {
            if (CONFIG.audio.loop) {
                audio.currentTime = 0;
                audio.play().catch(e => console.log('Auto-replay prevented:', e));
            } else {
                isPlaying = false;
                updateUI();
            }
        });
        
        // 尝试自动播放（可能被浏览器阻止）
        if (CONFIG.audio.autoplay) {
            play().catch(e => {
                console.log('Autoplay prevented by browser, waiting for user interaction');
            });
        }
        
        // 创建控制按钮
        createControlButton();
    }
    
    /**
     * 创建音乐控制按钮
     */
    function createControlButton() {
        const existingBtn = document.querySelector('.music-control');
        if (existingBtn) return;
        
        const btn = document.createElement('button');
        btn.className = 'music-control';
        btn.setAttribute('aria-label', 'Toggle music');
        btn.innerHTML = `
            <svg class="music-icon" viewBox="0 0 24 24">
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
            </svg>
        `;
        
        btn.addEventListener('click', toggle);
        document.body.appendChild(btn);
        
        updateUI();
    }
    
    /**
     * 播放音乐
     */
    function play() {
        if (!audio) {
            init();
            return Promise.reject('Audio not initialized');
        }
        
        return audio.play().then(() => {
            isPlaying = true;
            updateUI();
            console.log('Audio playing');
        }).catch(error => {
            console.error('Audio play failed:', error);
            isPlaying = false;
            updateUI();
            throw error;
        });
    }
    
    /**
     * 暂停音乐
     */
    function pause() {
        if (!audio) return;
        
        audio.pause();
        isPlaying = false;
        updateUI();
        console.log('Audio paused');
    }
    
    /**
     * 切换播放状态
     */
    function toggle() {
        if (isPlaying) {
            pause();
        } else {
            play().catch(() => {
                // 播放失败时显示提示
                showNotification('音乐播放需要点击页面任意位置后重试');
            });
        }
    }
    
    /**
     * 设置音量
     * @param {number} vol - 音量 (0-1)
     */
    function setVolume(vol) {
        if (!audio) return;
        audio.volume = Math.max(0, Math.min(1, vol));
    }
    
    /**
     * 获取当前音量
     */
    function getVolume() {
        return audio ? audio.volume : 0;
    }
    
    /**
     * 更新 UI 状态
     */
    function updateUI() {
        const btn = document.querySelector('.music-control');
        if (!btn) return;
        
        if (isPlaying) {
            btn.classList.add('playing');
            btn.innerHTML = `
                <svg class="music-icon" viewBox="0 0 24 24">
                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
            `;
        } else {
            btn.classList.remove('playing');
            btn.innerHTML = `
                <svg class="music-icon" viewBox="0 0 24 24">
                    <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                </svg>
            `;
        }
    }
    
    /**
     * 显示通知
     */
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    /**
     * 销毁音频
     */
    function destroy() {
        if (audio) {
            audio.pause();
            audio.src = '';
            audio = null;
        }
        isPlaying = false;
        isLoaded = false;
        
        const btn = document.querySelector('.music-control');
        if (btn) btn.remove();
    }
    
    // 公开 API
    return {
        init: init,
        play: play,
        pause: pause,
        toggle: toggle,
        setVolume: setVolume,
        getVolume: getVolume,
        isPlaying: function() { return isPlaying; },
        isLoaded: function() { return isLoaded; },
        destroy: destroy
    };
})();