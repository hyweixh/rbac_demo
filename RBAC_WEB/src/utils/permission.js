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

/**
 * ② 新函数：只返回权限数组，不弹窗、不回调
 * 适合模板 v-if / 指令里多次调用
 * @returns {string[]} 例如 ["user:list","user:edit"]
 */
export function getPerms() {
  const authStore = useAuthStore()
  // console.log("当前用户权限：", authStore.permissions) 
  return authStore.permissions || []
}