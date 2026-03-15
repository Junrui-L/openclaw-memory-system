/**
 * 倒计时模块
 * 计算并格式化时间差
 */

const Countdown = (function() {
    'use strict';
    
    /**
     * 解析日期字符串
     * @param {string} dateStr - 日期字符串 (YYYY-MM-DD)
     * @returns {Date} Date 对象
     */
    function parseDate(dateStr) {
        if (!dateStr) return null;
        const parts = dateStr.split('-');
        if (parts.length !== 3) return null;
        
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1; // 月份从0开始
        const day = parseInt(parts[2], 10);
        
        return new Date(year, month, day);
    }
    
    /**
     * 计算两个日期之间的差值
     * @param {Date} startDate - 开始日期
     * @param {Date} endDate - 结束日期（默认为现在）
     * @returns {Object} 时间差对象
     */
    function calculate(startDate, endDate = new Date()) {
        if (!startDate) return null;
        
        const diff = endDate.getTime() - startDate.getTime();
        
        if (diff < 0) {
            return {
                days: 0,
                hours: 0,
                minutes: 0,
                seconds: 0,
                totalSeconds: 0,
                isFuture: true
            };
        }
        
        const totalSeconds = Math.floor(diff / 1000);
        const days = Math.floor(totalSeconds / (24 * 60 * 60));
        const hours = Math.floor((totalSeconds % (24 * 60 * 60)) / (60 * 60));
        const minutes = Math.floor((totalSeconds % (60 * 60)) / 60);
        const seconds = totalSeconds % 60;
        
        return {
            days,
            hours,
            minutes,
            seconds,
            totalSeconds,
            isFuture: false
        };
    }
    
    /**
     * 格式化倒计时显示
     * @param {Object} diff - 时间差对象
     * @param {string} format - 格式类型
     * @returns {string} 格式化后的字符串
     */
    function format(diff, format = CONFIG.countdown.format) {
        if (!diff) return '';
        
        const { days, hours, minutes, seconds } = diff;
        const prefix = CONFIG.countdown.prefix || '';
        const suffix = CONFIG.countdown.suffix || '';
        
        if (format === 'simple') {
            // 简单格式: X天
            return `${prefix}${days}天${suffix}`;
        }
        
        // 完整格式: X天 X小时 X分 X秒
        let result = prefix;
        
        if (days > 0) {
            result += `${days}天 `;
        }
        if (days > 0 || hours > 0) {
            result += `${String(hours).padStart(2, '0')}时 `;
        }
        result += `${String(minutes).padStart(2, '0')}分 `;
        result += `${String(seconds).padStart(2, '0')}秒`;
        
        if (suffix) {
            result += suffix;
        }
        
        return result;
    }
    
    /**
     * 获取生日倒计时
     * @returns {Object} 距离下一个生日的倒计时
     */
    function getBirthdayCountdown() {
        const birthday = parseDate(CONFIG.person.birthday);
        if (!birthday) return null;
        
        const now = new Date();
        const currentYear = now.getFullYear();
        
        // 今年的生日
        let nextBirthday = new Date(currentYear, birthday.getMonth(), birthday.getDate());
        
        // 如果今年的生日已过，计算明年的
        if (nextBirthday < now) {
            nextBirthday = new Date(currentYear + 1, birthday.getMonth(), birthday.getDate());
        }
        
        const diff = nextBirthday.getTime() - now.getTime();
        
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        return {
            days,
            hours,
            minutes,
            seconds,
            nextBirthday,
            isToday: days === 0 && hours === 0 && minutes === 0
        };
    }
    
    /**
     * 获取年龄
     * @returns {number} 年龄
     */
    function getAge() {
        const birthday = parseDate(CONFIG.person.birthday);
        if (!birthday) return null;
        
        const now = new Date();
        let age = now.getFullYear() - birthday.getFullYear();
        
        // 如果今年的生日还没到，减1岁
        const currentBirthday = new Date(now.getFullYear(), birthday.getMonth(), birthday.getDate());
        if (now < currentBirthday) {
            age--;
        }
        
        return age;
    }
    
    /**
     * 获取当前时间格式化
     * @returns {string} 格式化的时间字符串
     */
    function getCurrentTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    }
    
    /**
     * 获取当前日期
     * @returns {string} 格式化的日期字符串
     */
    function getCurrentDate() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${year}年${month}月${day}日`;
    }
    
    /**
     * 检查今天是否是生日
     * @returns {boolean}
     */
    function isBirthdayToday() {
        const birthday = parseDate(CONFIG.person.birthday);
        if (!birthday) return false;
        
        const now = new Date();
        return now.getMonth() === birthday.getMonth() && 
               now.getDate() === birthday.getDate();
    }
    
    // 公开 API
    return {
        parseDate: parseDate,
        calculate: calculate,
        format: format,
        getBirthdayCountdown: getBirthdayCountdown,
        getAge: getAge,
        getCurrentTime: getCurrentTime,
        getCurrentDate: getCurrentDate,
        isBirthdayToday: isBirthdayToday
    };
})();