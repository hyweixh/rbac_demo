import axios, { CancelToken, isCancel } from 'axios';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';
import router from '@/router';
import { useAuthStore } from '@/stores/auth';
import { ElMessage } from 'element-plus';

// 配置 NProgress，禁用右上角的加载小圆圈
NProgress.configure({ showSpinner: false });

class Http {
  constructor() {
    // 全局取消源，用于一次性取消所有正在进行的请求
    this.cancelSource = CancelToken.source();
    // 标记是否已提示过会话过期，防止重复弹窗
    this.sessionExpiredNotified = false;

    // 创建 Axios 实例
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_BASE_URL, // 接口根地址
      timeout: 30000 // 超时时间设置
    });

    // 初始化拦截器
    this._setupInterceptors();
  }

  _setupInterceptors() {
    // ========== 请求拦截器 ==========
    this.instance.interceptors.request.use(
      (config) => {
        // 为每个请求设置当前的 cancelToken
        config.cancelToken = this.cancelSource.token;
        config.__id = Date.now() + Math.random();
        // 启动进度条
        NProgress.start();

        // 从 Pinia 的 AuthStore 获取 JWT token，并添加到请求头
        const token = useAuthStore().token;
        if (token) {
          config.headers.Authorization = 'JWT ' + token;
        }
        return config;
      },
      (error) => {
        // 请求出错时直接结束进度条
        NProgress.done();
        return Promise.reject(error);
      }
    );

    // ========== 响应拦截器 ==========
    this.instance.interceptors.response.use(
      (response) => {
        // 请求成功，结束进度条
        NProgress.done();
        return response;
      },
      (error) => {
        // 不管成功或失败，都先结束进度条
        NProgress.done();

        // 如果是我们手动取消的请求，静默处理，不抛出错误
        if (isCancel(error)) {
          // 返回一个永不 resolve 的 Promise，阻断后续 .catch
          return new Promise(() => {});
        }

        const status = error.response?.status;
        // 统一强制下线处理
        if (status === 401) {
          return this._forceLogout('登录已过期，请重新登录');
        }
        if (status === 409) {
          return this._forceLogout('用户在其他设备已登录');
        }

        // 对非 401 的其他错误，继续抛给调用者处理
        const message = this.handleRequestError(error);
        return Promise.reject(message);
      }
    );
  }

  /**
   * 登录成功后调用：重置过期提示标志与取消源
   * 确保新的请求继续正常运行，并在下次 401 时重新提示一次
   */
  resetSession() {
    this.sessionExpiredNotified = false;
    this.cancelSource = CancelToken.source();
  }

  /**
   * 错误信息提取方法
   */
  handleRequestError(error) {
    console.log(error.response);
    
    const response = error.response;
    if (response?.data?.message) {
      return response.data.message;
    }
    if (response?.request?.response) {
      try {
        const parsed = JSON.parse(response.request.response);
        return this.extractErrorMessage(parsed);
      } catch {
        return '服务器异常';
      }
    }
    return '服务器异常';
  }

  /**
   * 统一的强制下线处理（会话过期 / 异地登录等）
   * 调用后返回一个 pending Promise，阻断后续 .catch
   */
  _forceLogout(message) {
    if (this.sessionExpiredNotified) {
      // 已提示过则直接吞掉
      return new Promise(() => {});
    }

    this.sessionExpiredNotified = true;
    // 取消所有在途请求
    this.cancelSource.cancel('Session expired');
    // 统一提示
    ElMessage.error(message);
    // 清除 Token
    useAuthStore().clearUserToken();
    // 跳转登录并在跳转完成后重置状态
    router.replace({ name: 'login' }).then(() => {
      this.resetSession();
    });
    // 吞掉错误链
    return new Promise(() => {});
  }

  /**
   * 提取后端字段详细信息
   */
  extractErrorMessage(errorData) {
    const messages = [];
    for (const key in errorData) {
      if (Array.isArray(errorData[key])) {
        messages.push(...errorData[key]);
      } else if (typeof errorData[key] === 'string') {
        messages.push(errorData[key]);
      }
    }
    return messages.join(', ');
  }

  post(path, data) {
    return this.instance.post(path, data).then((res) => res.data);
  }

  get(path, params) {
    return this.instance.get(path, { params }).then((res) => res.data);
  }

  put(path, data) {
    return this.instance.put(path, data).then((res) => res.data);
  }

  delete(path) {
    return this.instance.delete(path).then((res) => res);
  }

  // 文件下载，设置响应类型为 blob
  downloadFile(path, params) {
    return this.instance.get(path, {
      params,
      responseType: 'blob'
    });
  }
}

// 导出单例
const http = new Http();
export default http;
// 供外部重置会话状态使用
export const resetSessionExpiredFlag = () => http.resetSession();
