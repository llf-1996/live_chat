/**
 * Utils 统一导出入口
 */

// 聊天相关
export { default as api } from './chat.js'
export { openChatPage } from './chat.js'

// 敏感词过滤
export { filterSensitiveWords, hasSensitiveWords } from './sensitive-words.js'

