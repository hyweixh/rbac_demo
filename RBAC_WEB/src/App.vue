<script setup>
import '@/assets/css/light.css'
import '@/assets/css/elementPlus.css'
import '@/assets/css/global-scrollbar.css'
</script>

<template>
  <router-view />
</template>

<style>

.el-input__inner,
.el-textarea__inner,
.el-select .el-input__inner,
.el-button,
.el-form-item {
  font-family: var(--my-font-family) !important;
}

/* 主题色 */
:root {
  --el-color-primary: #626aef;
  --el-color-primary-light-3: #f56c6c;    /* 确认删除按钮-悬停 */
  --dark-background-color:#151617;
  --dark-background-card:#1D1E1F;
  --light-background-card:#FFFFFF;
  --dark-text-blod:#CFD3DC;       /* 暗黑模式下普通文本颜色 */
  --el-color-primary-light-9:#eff0fd;   /* 浅紫 */
  --el-text-color-secondary:#525a6e;    /* table表头 */
  --dark-underline:#323232;       /* 下划线 */
  --light-underline:#e6e6e6;       /* 下划线 */
  --light-background-gm:#f4f6f9;  /* 未填充背景色 */

  /* 颜色 */
  --el-color-warning: #fac858;    /* 警告颜色 */
  --el-color-green: #4fc08d;
  --el-color-red: #f56c6c;
  --el-color-unknown: #767a72;
}

/* nprogress进度条颜色-接口进度条 */
#nprogress .bar {
  background: var(--el-color-primary) !important;
}
#nprogress .peg {
  box-shadow:
    0 0 10px rgb(98, 106, 239),
    0 0 5px rgb(98, 106, 239) !important;
}


/* 抽屉头部样式 */
.drawer-header-container {
  padding-bottom: 10px;
  display: flex;
  justify-content: space-between;
}

.drawer-header-container-role {
  padding-bottom: 10px;
  display: flex;
  justify-content: space-between;
}

/* 去除所有按钮取消时，两侧阴影 */
button:focus,
.el-button:focus {
  outline: none;
  /* 去除默认的焦点样式 */
  box-shadow: none;
  /* 去除焦点时的阴影 */
}



/* 服务点状态样式 */
.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 100%;
  margin-right: 5px;
}

.icon-green {
  color: var(--el-color-green);
}

.icon-red {
  color: #f56c6c;
}

/* 正常 */
.status-normal {
  background-color: var(--el-color-green);
}

/* 异常 */
.status-error {
  background-color: #f56c6c;
}

/* 异常 */
.status-warning {
  background-color: #fac858;
}

/* 异常 */
.status-unknown {
  background-color: #767a72;
}


/* 筛选卡片 */
.location-container {
  display: flex;
  align-items: center;
}

/* 表格按钮容器 */
.table-container {
  /* 内边距 */
  padding: 10px;  
  /* 圆角 */
  border-radius: 8px; 
}

.table-link{
  font-size: 12px;
}

.cmdb_table {
  width: 100%;
  height: 72vh;
  font-size: 12px;
}


/* 加载图标旋转动画 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 二维码和按钮水平对其 */
.update-button-dq {
  display: inline-flex;
  align-items: flex-end;
}

.upload-demo {
  margin-left: 10px;
}

/* 设置 GridItem card */
.layout-card,.layout-card-fixed {
  border-radius: 4px; /* 圆角 */
  overflow: hidden;
  /* 防止内容溢出 */
  box-sizing: border-box;
}

.button-container {
  display: flex;
  align-items: center;
  margin-bottom: 2px;
}

.operation-mini-icon {
  height: 100%;
  border: none;
  transition: transform 0.3s ease;
}

/* 水平对齐，间距4px */
.center-flex {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.left-flex {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 全局表格单元格不换行 */
.el-table .cell {
  white-space: nowrap;        /* 不换行 */
  overflow: hidden;           /* 隐藏溢出 */
  text-overflow: ellipsis;    /* 超出显示省略号 */
}

.space_4px{
  margin-left: 0px;
  margin-right: 4px;
}

</style>
