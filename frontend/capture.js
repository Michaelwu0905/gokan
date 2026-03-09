// 截图选区逻辑
let isSelecting = false;
let startX = 0;
let startY = 0;
let currentX = 0;
let currentY = 0;
let screenImageData = null;

const backgroundImage = document.getElementById('background-image');
const overlay = document.getElementById('overlay');
const selection = document.getElementById('selection');
const info = document.getElementById('info');

// 接收屏幕截图
electronAPI.onScreenCaptured((imageData) => {
  screenImageData = imageData;
  backgroundImage.src = imageData;
  console.log('📸 Screen captured, ready for selection');
});

// 鼠标按下 - 开始选择
document.addEventListener('mousedown', (e) => {
  if (e.button !== 0) return; // 只响应左键
  
  isSelecting = true;
  startX = e.clientX;
  startY = e.clientY;
  
  selection.style.display = 'block';
  selection.style.left = startX + 'px';
  selection.style.top = startY + 'px';
  selection.style.width = '0px';
  selection.style.height = '0px';
  
  info.textContent = '释放鼠标完成选择';
});

// 鼠标移动 - 更新选择区域
document.addEventListener('mousemove', (e) => {
  if (!isSelecting) return;
  
  currentX = e.clientX;
  currentY = e.clientY;
  
  const left = Math.min(startX, currentX);
  const top = Math.min(startY, currentY);
  const width = Math.abs(currentX - startX);
  const height = Math.abs(currentY - startY);
  
  selection.style.left = left + 'px';
  selection.style.top = top + 'px';
  selection.style.width = width + 'px';
  selection.style.height = height + 'px';
  
  info.textContent = `${width} x ${height} px`;
});

// 鼠标释放 - 完成选择
document.addEventListener('mouseup', async () => {
  if (!isSelecting) return;
  
  isSelecting = false;
  
  const left = Math.min(startX, currentX);
  const top = Math.min(startY, currentY);
  const width = Math.abs(currentX - startX);
  const height = Math.abs(currentY - startY);
  
  // 检查选区大小（防误触）
  if (width < 15 || height < 15) {
    console.log('⚠️ Selection too small, cancelling');
    electronAPI.captureAreaSelected({
      imageData: null,
      bounds: { x: left, y: top, width, height }
    });
    return;
  }
  
  // 裁剪选区图像
  try {
    const croppedImage = await cropImage(screenImageData, left, top, width, height);
    
    // 发送选区数据到主进程
    electronAPI.captureAreaSelected({
      imageData: croppedImage,
      bounds: { x: left, y: top, width, height }
    });
  } catch (err) {
    console.error('Failed to crop image:', err);
    electronAPI.captureAreaSelected({
      imageData: null,
      bounds: { x: left, y: top, width, height }
    });
  }
});

// 按 ESC 取消
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    isSelecting = false;
    electronAPI.captureAreaSelected({
      imageData: null,
      bounds: { x: 0, y: 0, width: 0, height: 0 }
    });
  }
});

/**
 * 裁剪图片
 */
function cropImage(imageDataUrl, x, y, width, height) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      
      const ctx = canvas.getContext('2d');
      
      // 计算缩放比例（截图可能缩放了）
      const scaleX = img.naturalWidth / window.innerWidth;
      const scaleY = img.naturalHeight / window.innerHeight;
      
      // 绘制裁剪区域
      ctx.drawImage(
        img,
        x * scaleX,
        y * scaleY,
        width * scaleX,
        height * scaleY,
        0,
        0,
        width,
        height
      );
      
      resolve(canvas.toDataURL('image/png'));
    };
    img.onerror = reject;
    img.src = imageDataUrl;
  });
}
