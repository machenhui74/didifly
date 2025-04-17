/**
 * Mcard - 基于图像识别的记忆卡片应用
 * 主要JavaScript功能实现
 */

// 全局变量
const MCARD = {
    // 单词数据库
    wordDatabase: [],
    
    // 当前学习的卡片
    selectedWords: [],
    
    // 当前查看的卡片索引
    currentCardIndex: 0,
    
    // 艾宾浩斯遗忘曲线复习间隔（天）
    reviewIntervals: [1, 3, 7, 15, 30, 60, 90],
    
    // 图像分析结果
    analyzedWords: [],
    
    // 用户数据
    userData: {
        totalWords: 0,
        masteredWords: 0,
        toReviewWords: 0,
        streakDays: 0,
        masteryPercentage: 0,
        learningHistory: [],
        cards: []
    },
    
    // 当前选择的场景
    currentScenario: null,
    
    // 所有可用场景
    scenarios: [],
    
    // 学习提示
    learningTips: [],
    
    // 复习通知模板
    reviewNotifications: [],

    // API配置
    api: {
        // 大模型图像识别API配置
        imageRecognition: {
            url: "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            apiKey: "6818ceda-6ba6-46ff-8c05-91f0acf4ad1e", // 实际应用中应从安全位置获取
            timeout: 30000 // 请求超时时间（毫秒）
        }
    }
};

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadMockData();
    initializeApp();
});

/**
 * 加载模拟数据
 */
function loadMockData() {
    if (typeof MOCK_DATA !== 'undefined') {
        MCARD.wordDatabase = MOCK_DATA.words || [];
        MCARD.userData = MOCK_DATA.userProgress || MCARD.userData;
        MCARD.scenarios = MOCK_DATA.scenarios || [];
        MCARD.learningTips = MOCK_DATA.learningTips || [];
        MCARD.reviewNotifications = MOCK_DATA.reviewNotifications || [];
    }
}

/**
 * 初始化应用
 */
function initializeApp() {
    // 初始化各个模块
    initUploadModule();
    initWordSelectionModule();
    initCardModule();
    initReviewModule();
    initStatsModule();
    displayRandomTip();
}

/**
 * 初始化上传模块
 */
function initUploadModule() {
    const uploadArea = document.getElementById('upload-area');
    const photoUpload = document.getElementById('photo-upload');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const uploadBtn = document.getElementById('upload-btn');
    const cameraBtn = document.getElementById('camera-btn');
    const analysisLoading = document.getElementById('analysis-loading');
    
    // 点击上传区域触发文件选择
    if (uploadArea) {
        uploadArea.addEventListener('click', function() {
            photoUpload.click();
        });
    }
    
    // 点击上传按钮触发文件选择
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            photoUpload.click();
        });
    }
    
    // 点击拍照按钮（模拟）
    if (cameraBtn) {
        cameraBtn.addEventListener('click', function() {
            simulateCameraCapture();
        });
    }
    
    // 文件选择变化处理
    if (photoUpload) {
        photoUpload.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    previewContainer.style.display = 'block';
                    
                    // 显示加载动画
                    if (analysisLoading) {
                        analysisLoading.style.display = 'block';
                    }
                    
                    // 调用图像识别API
                    analyzeImageWithAI(e.target.result);
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
}

/**
 * 模拟相机拍照
 */
function simulateCameraCapture() {
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const analysisLoading = document.getElementById('analysis-loading');
    
    // 使用占位图像模拟拍照
    previewImage.src = 'https://placehold.co/600x400/e1e5eb/4a6fa5?text=模拟拍照&font=microsoft-yahei';
    previewContainer.style.display = 'block';
    
    // 显示加载动画
    if (analysisLoading) {
        analysisLoading.style.display = 'block';
    }
    
    // 调用图像识别API（使用模拟图像URL）
    analyzeImageWithAI(previewImage.src);
}

/**
 * 使用大模型AI分析图像内容
 * @param {string} imageData - 图像数据（Base64或URL）
 */
async function analyzeImageWithAI(imageData) {
    try {
        // 开发/测试模式：使用模拟数据，避免实际API调用
        if (process.env.NODE_ENV === 'development' || true) {
            // 模拟API调用延迟
            setTimeout(() => {
                // 调用模拟分析功能
                simulateImageAnalysis();
            }, 2000);
            return;
        }

        // 以下为实际API调用代码
        // 1. 准备请求数据
        const requestData = {
            image: imageData.startsWith('data:') ? imageData : null,
            imageUrl: !imageData.startsWith('data:') ? imageData : null,
            options: {
                extractText: true,
                detectLanguage: true,
                identifyWords: true,
                confidenceThreshold: 0.7
            }
        };

        // 2. 发送API请求
        const response = await fetch(MCARD.api.imageRecognition.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${MCARD.api.imageRecognition.apiKey}`
            },
            body: JSON.stringify(requestData),
            timeout: MCARD.api.imageRecognition.timeout
        });

        // 3. 解析响应
        if (!response.ok) {
            throw new Error(`API调用失败: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();

        // 4. 处理识别结果
        processRecognitionResults(result);
        
    } catch (error) {
        console.error('图像识别API调用出错:', error);
        
        // 显示错误提示
        const analysisLoading = document.getElementById('analysis-loading');
        if (analysisLoading) {
            analysisLoading.style.display = 'none';
        }
        
        // 创建错误提示
        showErrorNotification('图像识别失败', '无法识别图像中的文字，请重试或使用不同的图像。');
        
        // 备用方案：使用模拟数据
        simulateImageAnalysis();
    }
}

/**
 * 处理图像识别API返回的结果
 * @param {Object} result - API返回的识别结果
 */
function processRecognitionResults(result) {
    // 该函数处理实际API返回的数据
    // 下面是一个示例实现，实际实现需根据API响应格式调整
    
    try {
        // 清空之前的分析结果
        MCARD.analyzedWords = [];
        
        // 从结果中提取识别出的单词
        if (result && result.words && Array.isArray(result.words)) {
            // 遍历API返回的单词列表
            result.words.forEach(wordData => {
                if (wordData.text && wordData.confidence > 0.7) {
                    // 查找该单词是否在我们的数据库中
                    const wordInfo = MCARD.wordDatabase.find(
                        item => item.word.toLowerCase() === wordData.text.toLowerCase()
                    );
                    
                    // 如果在数据库中找到该单词，添加到分析结果
                    if (wordInfo) {
                        MCARD.analyzedWords.push(wordInfo.word);
                    }
                }
            });
        }
        
        // 隐藏加载动画
        const analysisLoading = document.getElementById('analysis-loading');
        if (analysisLoading) {
            analysisLoading.style.display = 'none';
        }
        
        // 跳转到分析结果部分
        const analysisSection = document.getElementById('analysis-section');
        if (analysisSection) {
            analysisSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // 如果没有识别出任何单词，显示提示
        if (MCARD.analyzedWords.length === 0) {
            showErrorNotification('未识别到单词', '图像中未能识别出可学习的单词，请尝试其他图像。');
            
            // 使用模拟数据作为备用方案
            simulateImageAnalysis();
            return;
        }
        
        // 更新分析结果UI
        updateAnalysisResults();
        
    } catch (error) {
        console.error('处理识别结果出错:', error);
        simulateImageAnalysis(); // 出错时使用模拟数据
    }
}

/**
 * 显示错误通知
 * @param {string} title - 错误标题
 * @param {string} message - 错误信息
 */
function showErrorNotification(title, message) {
    // 创建错误通知元素
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.style.backgroundColor = 'var(--danger-color)';
    notification.style.marginBottom = '20px';
    
    // 添加关闭按钮
    const closeBtn = document.createElement('div');
    closeBtn.className = 'notification-close';
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', function() {
        notification.style.display = 'none';
    });
    
    // 添加通知内容
    const titleEl = document.createElement('h3');
    titleEl.textContent = title;
    
    const messageEl = document.createElement('p');
    messageEl.textContent = message;
    
    // 组装通知元素
    notification.appendChild(closeBtn);
    notification.appendChild(titleEl);
    notification.appendChild(messageEl);
    
    // 添加到页面
    const analysisSection = document.getElementById('analysis-section');
    if (analysisSection) {
        const existingNotification = analysisSection.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        analysisSection.insertBefore(notification, analysisSection.firstChild.nextSibling.nextSibling);
    }
    
    // 5秒后自动关闭
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

/**
 * 模拟图像分析过程
 */
function simulateImageAnalysis() {
    // 随机选择一个场景
    if (MOCK_DATA && MOCK_DATA.mockImages && MOCK_DATA.mockImages.length > 0) {
        const randomScenarioIndex = Math.floor(Math.random() * MOCK_DATA.mockImages.length);
        const scenario = MOCK_DATA.mockImages[randomScenarioIndex];
        
        // 更新分析图片
        const analysisImage = document.querySelector('.image-analysis img');
        if (analysisImage) {
            analysisImage.src = scenario.url;
        }
        
        // 设置识别出的单词
        MCARD.analyzedWords = [];
        scenario.detectedWords.forEach(word => {
            // 查找单词是否在数据库中
            const wordInfo = MCARD.wordDatabase.find(item => item.word.toLowerCase() === word.toLowerCase());
            if (wordInfo) {
                MCARD.analyzedWords.push(wordInfo.word);
            }
        });
    } else {
        // 备选：随机选择单词
        MCARD.analyzedWords = [];
        const wordCount = Math.floor(Math.random() * 5) + 5; // 5-10个单词
        
        // 随机选择单词
        const selectedIndices = new Set();
        while (selectedIndices.size < wordCount) {
            const randomIndex = Math.floor(Math.random() * MCARD.wordDatabase.length);
            selectedIndices.add(randomIndex);
        }
        
        // 添加到分析结果
        for (const index of selectedIndices) {
            MCARD.analyzedWords.push(MCARD.wordDatabase[index].word);
        }
    }
    
    // 隐藏加载动画
    const analysisLoading = document.getElementById('analysis-loading');
    if (analysisLoading) {
        analysisLoading.style.display = 'none';
    }
    
    // 跳转到分析结果部分
    const analysisSection = document.getElementById('analysis-section');
    if (analysisSection) {
        analysisSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 更新分析结果UI
    updateAnalysisResults();
}

/**
 * 更新分析结果UI
 */
function updateAnalysisResults() {
    const wordList = document.querySelector('.word-list');
    
    if (wordList && MCARD.analyzedWords.length > 0) {
        // 清空现有内容
        wordList.innerHTML = '';
        
        // 创建单词项
        MCARD.analyzedWords.forEach(word => {
            const wordItem = document.createElement('div');
            wordItem.className = 'word-item';
            wordItem.textContent = word;
            
            // 点击选择/取消选择
            wordItem.addEventListener('click', function() {
                this.classList.toggle('selected');
            });
            
            wordList.appendChild(wordItem);
        });
    }
    
    // 设置创建卡片按钮事件
    const createCardsBtn = document.getElementById('create-cards-btn');
    if (createCardsBtn) {
        createCardsBtn.addEventListener('click', createMemoryCards);
    }
}

/**
 * 初始化单词选择模块
 */
function initWordSelectionModule() {
    // 为已存在的静态单词项添加点击事件
    const existingWordItems = document.querySelectorAll('.word-list .word-item');
    existingWordItems.forEach(wordItem => {
        wordItem.addEventListener('click', function() {
            this.classList.toggle('selected');
        });
    });
    
    // 设置创建卡片按钮事件
    const createCardsBtn = document.getElementById('create-cards-btn');
    if (createCardsBtn) {
        createCardsBtn.addEventListener('click', createMemoryCards);
    }
}

/**
 * 创建记忆卡片
 */
function createMemoryCards() {
    // 获取选中的单词
    const selectedWordElements = document.querySelectorAll('.word-item.selected');
    MCARD.selectedWords = [];
    
    selectedWordElements.forEach(element => {
        const word = element.textContent;
        // 查找单词详细信息
        const wordInfo = MCARD.wordDatabase.find(item => item.word === word);
        if (wordInfo) {
            MCARD.selectedWords.push(wordInfo);
        }
    });
    
    // 如果有选中的单词，跳转到卡片区域
    if (MCARD.selectedWords.length > 0) {
        MCARD.currentCardIndex = 0;
        updateCardDisplay();
        updatePagination();
        
        const cardSection = document.getElementById('card-section');
        if (cardSection) {
            cardSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

/**
 * 初始化卡片模块
 */
function initCardModule() {
    const prevBtn = document.getElementById('prev-card');
    const nextBtn = document.getElementById('next-card');
    const flipBtn = document.getElementById('flip-card');
    const card = document.getElementById('card');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            if (MCARD.currentCardIndex > 0) {
                MCARD.currentCardIndex--;
                updateCardDisplay();
                updatePagination();
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            if (MCARD.currentCardIndex < MCARD.selectedWords.length - 1) {
                MCARD.currentCardIndex++;
                updateCardDisplay();
                updatePagination();
            }
        });
    }
    
    if (flipBtn) {
        flipBtn.addEventListener('click', function() {
            if (card) {
                card.classList.toggle('flipped');
            }
        });
    }
    
    if (card) {
        card.addEventListener('click', function() {
            this.classList.toggle('flipped');
        });
    }
    
    // 添加触摸滑动卡片功能
    if (card) {
        let touchStartX = 0;
        let touchEndX = 0;
        
        card.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
        });
        
        card.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].clientX;
            handleSwipe();
        });
        
        function handleSwipe() {
            if (touchEndX < touchStartX - 50) {
                // 左滑，下一张卡片
                if (MCARD.currentCardIndex < MCARD.selectedWords.length - 1) {
                    MCARD.currentCardIndex++;
                    updateCardDisplay();
                    updatePagination();
                }
            } else if (touchEndX > touchStartX + 50) {
                // 右滑，上一张卡片
                if (MCARD.currentCardIndex > 0) {
                    MCARD.currentCardIndex--;
                    updateCardDisplay();
                    updatePagination();
                }
            }
        }
    }
}

/**
 * 更新卡片显示
 */
function updateCardDisplay() {
    if (MCARD.selectedWords.length === 0) return;
    
    const wordInfo = MCARD.selectedWords[MCARD.currentCardIndex];
    const frontWord = document.querySelector('.card-front .word');
    const frontPhonetic = document.querySelector('.card-front .phonetic');
    const backTranslation = document.querySelector('.card-back .translation');
    const backExample = document.querySelector('.card-back div div:first-child');
    const backExampleTranslation = document.querySelector('.card-back div div:last-child');
    
    if (frontWord) frontWord.textContent = wordInfo.word;
    if (frontPhonetic) frontPhonetic.textContent = wordInfo.phonetic;
    if (backTranslation) backTranslation.textContent = wordInfo.translation;
    if (backExample) backExample.textContent = `例句：${wordInfo.example}`;
    if (backExampleTranslation) backExampleTranslation.textContent = wordInfo.exampleTranslation;
    
    // 确保卡片显示正面
    const card = document.getElementById('card');
    if (card && card.classList.contains('flipped')) {
        card.classList.remove('flipped');
    }
}

/**
 * 更新分页指示器
 */
function updatePagination() {
    const pagination = document.getElementById('pagination');
    if (!pagination || MCARD.selectedWords.length === 0) return;
    
    // 清空现有内容
    pagination.innerHTML = '';
    
    // 创建分页点
    for (let i = 0; i < MCARD.selectedWords.length; i++) {
        const paginationDot = document.createElement('div');
        paginationDot.className = 'pagination-dot' + (i === MCARD.currentCardIndex ? ' active' : '');
        
        // 点击跳转到对应卡片
        paginationDot.addEventListener('click', function() {
            MCARD.currentCardIndex = i;
            updateCardDisplay();
            updatePagination();
        });
        
        pagination.appendChild(paginationDot);
    }
}

/**
 * 初始化复习模块
 */
function initReviewModule() {
    // 通知关闭按钮
    const notificationClose = document.querySelector('.notification-close');
    const notification = document.querySelector('.notification');
    
    if (notificationClose && notification) {
        notificationClose.addEventListener('click', function() {
            notification.style.display = 'none';
        });
    }
    
    // 动态生成复习计划
    updateReviewPlan();
}

/**
 * 更新复习计划
 */
function updateReviewPlan() {
    if (MCARD.selectedWords.length === 0) return;
    
    const timeline = document.querySelector('.timeline');
    if (!timeline) return;
    
    // 清空现有内容
    timeline.innerHTML = '';
    
    // 获取当前日期
    const today = new Date();
    
    // 创建复习计划项
    let reviewDate = new Date(today);
    
    // 首次学习（今天）
    const firstItem = createTimelineItem('第一天（今天）', `首次学习 ${MCARD.selectedWords.map(w => w.word).join(', ')}`);
    timeline.appendChild(firstItem);
    
    // 根据艾宾浩斯遗忘曲线生成复习计划
    MCARD.reviewIntervals.forEach((interval, index) => {
        // 计算复习日期
        const nextDate = new Date(today);
        nextDate.setDate(today.getDate() + interval);
        
        // 创建复习计划项
        const formattedDate = nextDate.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
        const item = createTimelineItem(
            `第${interval}天（${formattedDate}）`, 
            `第${index + 1}次复习 ${MCARD.selectedWords.map(w => w.word).join(', ')}`
        );
        
        timeline.appendChild(item);
    });
}

/**
 * 创建时间线项
 * @param {string} title - 时间线项标题
 * @param {string} content - 时间线项内容
 * @returns {HTMLElement} - 时间线项DOM元素
 */
function createTimelineItem(title, content) {
    const item = document.createElement('div');
    item.className = 'timeline-item';
    
    const titleEl = document.createElement('h4');
    titleEl.textContent = title;
    
    const contentEl = document.createElement('p');
    contentEl.textContent = content;
    
    item.appendChild(titleEl);
    item.appendChild(contentEl);
    
    return item;
}

/**
 * 初始化统计模块
 */
function initStatsModule() {
    updateStatisticsDisplay();
}

/**
 * 更新统计显示
 */
function updateStatisticsDisplay() {
    // 更新统计卡片
    const totalWordsEl = document.querySelector('.stat-card:nth-child(1) .stat-number');
    const masteredWordsEl = document.querySelector('.stat-card:nth-child(2) .stat-number');
    const toReviewWordsEl = document.querySelector('.stat-card:nth-child(3) .stat-number');
    const streakDaysEl = document.querySelector('.stat-card:nth-child(4) .stat-number');
    
    if (totalWordsEl) totalWordsEl.textContent = MCARD.userData.totalWords;
    if (masteredWordsEl) masteredWordsEl.textContent = MCARD.userData.masteredWords;
    if (toReviewWordsEl) toReviewWordsEl.textContent = MCARD.userData.toReviewWords;
    if (streakDaysEl) streakDaysEl.textContent = MCARD.userData.streakDays;
    
    // 更新进度条
    const progressPercentageEl = document.querySelector('.progress-container span:last-child');
    const progressFillEl = document.querySelector('.progress-fill');
    
    if (progressPercentageEl) progressPercentageEl.textContent = MCARD.userData.masteryPercentage + '%';
    if (progressFillEl) progressFillEl.style.width = MCARD.userData.masteryPercentage + '%';
}

/**
 * 显示随机学习提示
 */
function displayRandomTip() {
    if (MCARD.learningTips.length === 0) return;
    
    // 随机选择一个提示
    const randomIndex = Math.floor(Math.random() * MCARD.learningTips.length);
    const tip = MCARD.learningTips[randomIndex];
    
    // 创建提示元素
    const tipContainer = document.createElement('div');
    tipContainer.className = 'notification';
    tipContainer.style.backgroundColor = 'var(--primary-color)';
    tipContainer.style.marginBottom = '20px';
    
    // 添加关闭按钮
    const closeBtn = document.createElement('div');
    closeBtn.className = 'notification-close';
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', function() {
        tipContainer.style.display = 'none';
    });
    
    // 添加提示内容
    const tipTitle = document.createElement('h3');
    tipTitle.textContent = '学习小提示';
    
    const tipContent = document.createElement('p');
    tipContent.textContent = tip;
    
    // 组装提示元素
    tipContainer.appendChild(closeBtn);
    tipContainer.appendChild(tipTitle);
    tipContainer.appendChild(tipContent);
    
    // 添加到页面
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(tipContainer, container.firstChild);
    }
}

/**
 * 生成艾宾浩斯遗忘曲线复习计划
 * @param {Date} startDate - 学习开始日期
 * @returns {Array} - 复习日期数组
 */
function generateReviewSchedule(startDate) {
    const schedule = [];
    let currentDate = new Date(startDate);
    
    for (const interval of MCARD.reviewIntervals) {
        currentDate = new Date(currentDate);
        currentDate.setDate(currentDate.getDate() + interval);
        schedule.push(new Date(currentDate));
    }
    
    return schedule;
}

/**
 * 格式化日期
 * @param {Date} date - 日期对象
 * @returns {string} - 格式化后的日期字符串
 */
function formatDate(date) {
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
}

// 模拟页面切换功能
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
} 