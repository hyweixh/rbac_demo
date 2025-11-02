<script setup>
import { useAuthStore } from '@/stores/auth';

const AuthStore = useAuthStore(); // 用户属性


const props = defineProps({
  isCollapse: {
    type: Boolean,
    default: false
  },
  defaultActive:{
    type:String
  }
});

</script>

<template>
    <el-menu :router="true" active-text-color="#0DBC79" background-color="#212222" :default-active="props.defaultActive"  text-color="#fff" :collapse="props.isCollapse" :collapse-transition="false">
    <!-- 固定主页菜单 -->
    <!-- <el-menu-item v-if="!props.isCollapse" index="home" :route="{ name: 'home' }">
      <el-icon>
        <SvgIcon name="home" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
      </el-icon>
      <span>主页</span>
    </el-menu-item>

    <el-tooltip v-if="props.isCollapse" content="主页" placement="right">
      <el-menu-item index="home" :route="{ name: 'home' }">
        <el-icon>
          <SvgIcon name="home" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
        </el-icon>
        <span>主页</span>
      </el-menu-item>
    </el-tooltip> -->

    <template v-for="menu in AuthStore.menu" :key="menu.id">
      <!-- 导航栏收缩时提示框 -->
      <el-tooltip v-if="!menu.children && props.isCollapse" :content="menu.text" placement="right">
        <el-menu-item :index="menu.path" :route="{ path: menu.path }">
          <!-- 一级菜单收缩状态 -->
          <el-icon>
            <SvgIcon :name="menu.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
          </el-icon>
          <span>{{ menu.text }}</span>
        </el-menu-item>
      </el-tooltip>
      <el-menu-item v-else-if="!menu.children" :index="menu.path" :route="{ path: menu.path }">
        <!-- 一级菜单展开状态 -->
        <el-icon>
          <SvgIcon :name="menu.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
        </el-icon>
        <span>{{ menu.text }}</span>
      </el-menu-item>
      <el-sub-menu v-else :index="menu.path">
        <template #title>
          <!-- 二级菜单 -->
          <el-icon>
            <SvgIcon :name="menu.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
          </el-icon>
          <span>{{ menu.text }}</span>
        </template>
        <template v-for="child in menu.children" :key="child.id">
          <!-- 导航栏收缩时提示框 -->
          <el-tooltip v-if="child.menu_type === 'C' && props.isCollapse" :content="child.text" placement="right">
            <el-menu-item :index="child.path" :route="{ path: child.path }">
              <el-icon>
                <SvgIcon :name="child.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
              </el-icon>
              <span>{{ child.text }}</span>
            </el-menu-item>
          </el-tooltip>
          <el-menu-item v-else-if="child.menu_type === 'C'" :index="child.path" :route="{ path: child.path }">
            <el-icon>
              <SvgIcon :name="child.icon" width="16px" height="16px" filter="grayscale(1) brightness(2)" />
            </el-icon>
            <span>{{ child.text }}</span>
          </el-menu-item>
        </template>
      </el-sub-menu>
    </template>
  </el-menu>

</template>

<style scoped>
/* 导航栏选中背景颜色 */
.el-menu-item.is-active {
  /* background-color: #4a5854; */
}

.el-menu {
  border-right: none;
}
</style>
