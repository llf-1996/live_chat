/**
 * Utils 统一导出入口
 */

// 聊天相关
export { default as api } from '@/utils/chat.js'
export { openChatPage } from '@/utils/chat.js'

// 敏感词过滤
export { filterSensitiveWords, hasSensitiveWords } from '@/utils/sensitive-words.js'

