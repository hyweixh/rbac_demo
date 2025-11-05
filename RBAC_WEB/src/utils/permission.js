import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

/**
 * ① 老函数：带权限校验 + 无权限弹窗
 * @param {string} permission  权限标识，如 'user:delete'
 * @param {Function} callback  通过校验后执行的回调
 */
export const checkPermission = (permission, callback) => {
  const authStore = useAuthStore()
  if (authStore.permissions.includes(permission)) {
    callback()
  } else {
    ElMessage.error('您没有该操作的权限')
  }
}


// ① 模块级缓存
let permsCache = null
/**
 * 只返回权限数组，不弹窗、不回调
 * 第一次会把 Pinia 数据缓存下来，后续直接读缓存
 */
export function getPerms() {
    // 如果已有缓存，直接返回  
    if (permsCache !== null) return permsCache

    // 第一次：真正去 store 里拿
    const authStore = useAuthStore()
    permsCache = authStore.permissions || []
    // 保留原来的调试日志（只打一次）
    console.log('当前用户权限-1105：', permsCache)
    return permsCache
}

/**
 * 如果登录后权限有变动，手动清一下缓存即可
 */
export function clearPermsCache() {
  permsCache = null
}