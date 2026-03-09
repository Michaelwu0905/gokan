const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 截图相关
  onScreenCaptured: (callback) => {
    ipcRenderer.on('screen-captured', (event, imageData) => callback(imageData));
  },
  
  // 区域选择完成
  captureAreaSelected: (data) => {
    ipcRenderer.invoke('capture-area-selected', data);
  },
  
  // 结果展示相关
  onShowResult: (callback) => {
    ipcRenderer.on('show-result', (event, imageData) => callback(imageData));
  },
  
  // 关闭结果窗口
  closeResultWindow: () => {
    ipcRenderer.invoke('close-result-window');
  },
  
  // 移除事件监听器
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  },
});
