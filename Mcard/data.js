/**
 * Mcard - 模拟数据文件
 * 提供示例单词、图片和用户数据
 */

const MOCK_DATA = {
    // 模拟单词库
    words: [
        { 
            word: 'apple', 
            phonetic: '/ˈæp.əl/', 
            translation: '苹果', 
            example: 'I eat an apple every day.', 
            exampleTranslation: '我每天吃一个苹果。',
            difficulty: 1,
            tags: ['食物', '水果']
        },
        { 
            word: 'banana', 
            phonetic: '/bəˈnɑː.nə/', 
            translation: '香蕉', 
            example: 'Monkeys love bananas.', 
            exampleTranslation: '猴子喜欢香蕉。',
            difficulty: 1,
            tags: ['食物', '水果']
        },
        { 
            word: 'book', 
            phonetic: '/bʊk/', 
            translation: '书，书籍', 
            example: 'I love reading books.', 
            exampleTranslation: '我喜欢读书。',
            difficulty: 1,
            tags: ['学习', '物品']
        },
        { 
            word: 'computer', 
            phonetic: '/kəmˈpjuː.tər/', 
            translation: '电脑', 
            example: 'I work on my computer every day.', 
            exampleTranslation: '我每天用电脑工作。',
            difficulty: 2,
            tags: ['科技', '物品']
        },
        { 
            word: 'coffee', 
            phonetic: '/ˈkɒf.i/', 
            translation: '咖啡', 
            example: 'I need coffee in the morning.', 
            exampleTranslation: '我早上需要喝咖啡。',
            difficulty: 1,
            tags: ['食物', '饮料']
        },
        { 
            word: 'desk', 
            phonetic: '/desk/', 
            translation: '桌子，写字台', 
            example: 'My books are on the desk.', 
            exampleTranslation: '我的书在桌子上。',
            difficulty: 1,
            tags: ['家具', '物品']
        },
        { 
            word: 'garden', 
            phonetic: '/ˈɡɑː.dən/', 
            translation: '花园', 
            example: 'She has beautiful flowers in her garden.', 
            exampleTranslation: '她的花园里有美丽的花朵。',
            difficulty: 2,
            tags: ['自然', '地点']
        },
        { 
            word: 'house', 
            phonetic: '/haʊs/', 
            translation: '房子', 
            example: 'They live in a big house.', 
            exampleTranslation: '他们住在一个大房子里。',
            difficulty: 1,
            tags: ['建筑', '地点']
        },
        { 
            word: 'laptop', 
            phonetic: '/ˈlæp.tɒp/', 
            translation: '笔记本电脑', 
            example: 'I carry my laptop everywhere.', 
            exampleTranslation: '我随身携带笔记本电脑。',
            difficulty: 2,
            tags: ['科技', '物品']
        },
        { 
            word: 'phone', 
            phonetic: '/fəʊn/', 
            translation: '电话，手机', 
            example: 'Can I use your phone?', 
            exampleTranslation: '我能用一下你的手机吗？',
            difficulty: 1,
            tags: ['科技', '物品']
        },
        { 
            word: 'window', 
            phonetic: '/ˈwɪn.dəʊ/', 
            translation: '窗户', 
            example: 'Open the window, please.', 
            exampleTranslation: '请打开窗户。',
            difficulty: 1,
            tags: ['建筑', '物品']
        },
        { 
            word: 'restaurant', 
            phonetic: '/ˈres.trɒnt/', 
            translation: '餐厅，饭店', 
            example: 'We had dinner at a nice restaurant.', 
            exampleTranslation: '我们在一家不错的餐厅吃了晚餐。',
            difficulty: 2,
            tags: ['建筑', '地点', '食物']
        },
        { 
            word: 'school', 
            phonetic: '/skuːl/', 
            translation: '学校', 
            example: 'My daughter goes to school by bus.', 
            exampleTranslation: '我女儿坐公交车去学校。',
            difficulty: 1,
            tags: ['建筑', '地点', '学习']
        },
        { 
            word: 'teacher', 
            phonetic: '/ˈtiː.tʃər/', 
            translation: '教师，老师', 
            example: 'My English teacher is very patient.', 
            exampleTranslation: '我的英语老师非常有耐心。',
            difficulty: 1,
            tags: ['职业', '人物', '学习']
        },
        { 
            word: 'doctor', 
            phonetic: '/ˈdɒk.tər/', 
            translation: '医生', 
            example: 'I need to see a doctor today.', 
            exampleTranslation: '我今天需要去看医生。',
            difficulty: 1,
            tags: ['职业', '人物', '医疗']
        },
        { 
            word: 'hospital', 
            phonetic: '/ˈhɒs.pɪ.təl/', 
            translation: '医院', 
            example: 'The hospital is open 24 hours.', 
            exampleTranslation: '这家医院24小时开放。',
            difficulty: 2,
            tags: ['建筑', '地点', '医疗']
        },
        { 
            word: 'library', 
            phonetic: '/ˈlaɪ.brər.i/', 
            translation: '图书馆', 
            example: 'I study at the library every weekend.', 
            exampleTranslation: '我每个周末都在图书馆学习。',
            difficulty: 2,
            tags: ['建筑', '地点', '学习']
        },
        { 
            word: 'student', 
            phonetic: '/ˈstjuː.dənt/', 
            translation: '学生', 
            example: 'He is a hardworking student.', 
            exampleTranslation: '他是一个勤奋的学生。',
            difficulty: 1,
            tags: ['人物', '学习']
        },
        { 
            word: 'water', 
            phonetic: '/ˈwɔː.tər/', 
            translation: '水', 
            example: 'Drink plenty of water every day.', 
            exampleTranslation: '每天喝足够的水。',
            difficulty: 1,
            tags: ['自然', '饮料']
        },
        { 
            word: 'bicycle', 
            phonetic: '/ˈbaɪ.sɪ.kəl/', 
            translation: '自行车', 
            example: 'I ride my bicycle to work.', 
            exampleTranslation: '我骑自行车去上班。',
            difficulty: 2,
            tags: ['交通', '物品']
        }
    ],
    
    // 模拟图片分析结果
    mockImages: [
        {
            id: 1,
            url: 'https://placehold.co/600x400/e1e5eb/4a6fa5?text=餐厅场景&font=microsoft-yahei',
            detectedWords: ['restaurant', 'coffee', 'water', 'food', 'table', 'chair', 'menu', 'waiter']
        },
        {
            id: 2,
            url: 'https://placehold.co/600x400/e1e5eb/4a6fa5?text=学校场景&font=microsoft-yahei',
            detectedWords: ['school', 'teacher', 'student', 'book', 'desk', 'computer', 'classroom', 'library']
        },
        {
            id: 3,
            url: 'https://placehold.co/600x400/e1e5eb/4a6fa5?text=医院场景&font=microsoft-yahei',
            detectedWords: ['hospital', 'doctor', 'nurse', 'patient', 'medicine', 'bed', 'ambulance', 'health']
        },
        {
            id: 4,
            url: 'https://placehold.co/600x400/e1e5eb/4a6fa5?text=家庭场景&font=microsoft-yahei',
            detectedWords: ['house', 'window', 'door', 'garden', 'family', 'kitchen', 'bedroom', 'bathroom']
        },
        {
            id: 5,
            url: 'https://placehold.co/600x400/e1e5eb/4a6fa5?text=办公场景&font=microsoft-yahei',
            detectedWords: ['computer', 'laptop', 'phone', 'office', 'desk', 'chair', 'meeting', 'colleague']
        }
    ],
    
    // 用户学习数据
    userProgress: {
        totalWords: 36,
        masteredWords: 24,
        toReviewWords: 12,
        streakDays: 5,
        masteryPercentage: 67,
        learningHistory: [
            { date: '2023-05-01', wordsLearned: 8, wordsReviewed: 0 },
            { date: '2023-05-02', wordsLearned: 5, wordsReviewed: 8 },
            { date: '2023-05-03', wordsLearned: 0, wordsReviewed: 13 },
            { date: '2023-05-04', wordsLearned: 10, wordsReviewed: 13 },
            { date: '2023-05-05', wordsLearned: 7, wordsReviewed: 23 },
            { date: '2023-05-06', wordsLearned: 6, wordsReviewed: 30 },
            { date: '2023-05-07', wordsLearned: 0, wordsReviewed: 36 }
        ],
        cards: [
            { 
                word: 'apple', 
                lastReviewed: '2023-05-05', 
                reviewCount: 3, 
                mastered: true,
                dueDate: '2023-05-10'
            },
            { 
                word: 'banana', 
                lastReviewed: '2023-05-06', 
                reviewCount: 2, 
                mastered: false,
                dueDate: '2023-05-09'
            },
            { 
                word: 'book', 
                lastReviewed: '2023-05-07', 
                reviewCount: 4, 
                mastered: true,
                dueDate: '2023-05-14'
            },
            { 
                word: 'computer', 
                lastReviewed: '2023-05-05', 
                reviewCount: 2, 
                mastered: false,
                dueDate: '2023-05-08'
            },
            { 
                word: 'coffee', 
                lastReviewed: '2023-05-07', 
                reviewCount: 3, 
                mastered: true,
                dueDate: '2023-05-12'
            },
            { 
                word: 'desk', 
                lastReviewed: '2023-05-06', 
                reviewCount: 2, 
                mastered: false,
                dueDate: '2023-05-09'
            },
            { 
                word: 'garden', 
                lastReviewed: '2023-05-04', 
                reviewCount: 1, 
                mastered: false,
                dueDate: '2023-05-08'
            },
            { 
                word: 'house', 
                lastReviewed: '2023-05-07', 
                reviewCount: 3, 
                mastered: true,
                dueDate: '2023-05-12'
            },
            { 
                word: 'phone', 
                lastReviewed: '2023-05-07', 
                reviewCount: 4, 
                mastered: true,
                dueDate: '2023-05-14'
            }
        ]
    },
    
    // 复习提醒模板
    reviewNotifications: [
        {
            title: '是时候复习了！',
            message: '有 {count} 个单词需要复习，坚持学习，提高记忆效果！',
            buttonText: '开始复习'
        },
        {
            title: '复习提醒',
            message: '复习是巩固记忆的关键！现在有 {count} 个单词等待你的复习。',
            buttonText: '立即复习'
        },
        {
            title: '复习时间到！',
            message: '根据艾宾浩斯遗忘曲线，现在是复习的最佳时间，有 {count} 个单词等待复习。',
            buttonText: '马上复习'
        }
    ],
    
    // 学习提示
    learningTips: [
        '每天保持10-15分钟的学习，效果比一次性长时间学习更好。',
        '复习时尝试先回忆单词的意思，再翻转卡片查看答案。',
        '将新学的单词用于造句，有助于更深入地记忆。',
        '将学习与日常活动关联，比如看到相关物品时回忆对应的单词。',
        '睡前复习有助于记忆的巩固。',
        '尝试用学过的单词与他人交流，实际应用是最好的记忆方式。',
        '多种感官参与学习效果更好，尝试大声朗读单词和例句。'
    ],
    
    // 模拟场景
    scenarios: [
        {
            name: '餐厅',
            description: '在餐厅点餐和用餐的相关单词',
            words: ['restaurant', 'coffee', 'water', 'food', 'table', 'chair', 'menu', 'waiter']
        },
        {
            name: '学校',
            description: '学校环境和学习相关的单词',
            words: ['school', 'teacher', 'student', 'book', 'desk', 'computer', 'classroom', 'library']
        },
        {
            name: '医院',
            description: '医疗和健康相关的单词',
            words: ['hospital', 'doctor', 'nurse', 'patient', 'medicine', 'bed', 'ambulance', 'health']
        },
        {
            name: '家庭',
            description: '家庭环境和家居相关的单词',
            words: ['house', 'window', 'door', 'garden', 'family', 'kitchen', 'bedroom', 'bathroom']
        },
        {
            name: '办公室',
            description: '工作和办公相关的单词',
            words: ['computer', 'laptop', 'phone', 'office', 'desk', 'chair', 'meeting', 'colleague']
        }
    ]
};

// 如果不在浏览器环境中，导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MOCK_DATA;
} 