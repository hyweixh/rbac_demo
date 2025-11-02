<template>
  <el-dropdown>
    <span class="el-dropdown-link">
      <el-avatar shape="square" :size="35" :src="avatarUrl"/>
      <span v-if="authStore.user" style="margin-left: 10px">
        {{ authStore.user.realname }}
      </span>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item divided @click="onExit">退出登录</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

</template>

<script setup>
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore() // 用户属性

// 定义一个响应式引用来存储头像的URL
const avatarUrl = import.meta.env.VITE_BASE_URL+"/media/userAvatar/" + authStore.user.avatar;
// const avatarUrl = "/media/userAvatar/" + authStore.user.avatar;


//退出登录，删除token
const onExit = () => {
  localStorage.removeItem('tabs') // 清除标签页状态
  localStorage.removeItem('activeTab') // 清除活跃的标签页状态
  authStore.clearUserToken()
  router.push({ name: 'login' })
}

</script>

<style scoped>
.el-dropdown-link {
  display: flex;
  align-items: center;
  /* 鼠标悬停黑款取消 */
  outline: none;
}
</style>
