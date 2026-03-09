const { app, BrowserWindow, globalShortcut, desktopCapturer, ipcMain, screen, Notification } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const net = require('net');
const http = require('http');

// 全局变量
let mainWindow = null;
let captureWindow = null;
let resultWindow = null;
let pythonProcess = null;
let isPythonReady = false;

// Python 服务配置
const PYTHON_PORT = 8000;
const PYTHON_HOST = '127.0.0.1';
const SERVICE_START_TIMEOUT = 30000; // 30秒超时

/**
 * 检查服务是否已运行（通过 HTTP 健康检查）
 */
async function checkServiceRunning() {
  return new Promise((resolve) => {
    const req = http.get(`http://${PYTHON_HOST}:${PYTHON_PORT}/health`, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * 启动 Python 后端服务
 */
async function startPythonService() {
  // 首先检查服务是否已经在运行
  const alreadyRunning = await checkServiceRunning();
  if (alreadyRunning) {
    console.log('✅ Python service already running');
    isPythonReady = true;
    return;
  }

  return new Promise((resolve, reject) => {
    const projectRoot = path.join(__dirname, '..');
    const pythonPath = path.join(projectRoot, '.venv', 'bin', 'python');
    const mainScript = path.join(projectRoot, 'backend', 'main.py');

    console.log('🐍 Starting Python backend service...');
    console.log(`   Python: ${pythonPath}`);
    console.log(`   Script: ${mainScript}`);

    // 启动 Python 进程
    pythonProcess = spawn(pythonPath, ['-m', 'backend.main'], {
      cwd: projectRoot,
      env: {
        ...process.env,
        PORT: PYTHON_PORT.toString(),
        HOST: PYTHON_HOST,
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let resolved = false;
    const resolveOnce = () => {
      if (!resolved) {
        resolved = true;
        resolve();
      }
    };

    // 捕获输出
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      console.log(`[Python] ${output}`);
      
      // 检查服务是否就绪
      if (output.includes('Application startup complete') || 
          output.includes('Uvicorn running') ||
          output.includes('AI Service initialized')) {
        isPythonReady = true;
        console.log('✅ Python backend is ready');
        resolveOnce();
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`[Python Error] ${data.toString().trim()}`);
    });

    pythonProcess.on('error', (err) => {
      console.error('❌ Failed to start Python process:', err);
      reject(err);
    });

    pythonProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`❌ Python process exited with code ${code}`);
      }
      isPythonReady = false;
      pythonProcess = null;
    });

    // 兜底：轮询检查服务是否就绪
    let attempts = 0;
    const maxAttempts = SERVICE_START_TIMEOUT / 500;
    const checkInterval = setInterval(async () => {
      attempts++;
      
      if (isPythonReady) {
        clearInterval(checkInterval);
        resolveOnce();
        return;
      }
      
      const running = await checkServiceRunning();
      if (running) {
        isPythonReady = true;
        console.log('✅ Python backend is ready (health check)');
        clearInterval(checkInterval);
        resolveOnce();
        return;
      }
      
      if (attempts >= maxAttempts) {
        clearInterval(checkInterval);
        reject(new Error('Timeout waiting for Python service to start'));
      }
    }, 500);
  });
}

/**
 * 停止 Python 后端服务
 */
function stopPythonService() {
  if (pythonProcess) {
    console.log('🛑 Stopping Python backend service...');
    
    // 尝试优雅地终止
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
    } else {
      pythonProcess.kill('SIGTERM');
      
      // 强制终止（如果还没退出）
      setTimeout(() => {
        if (pythonProcess && !pythonProcess.killed) {
          pythonProcess.kill('SIGKILL');
        }
      }, 3000);
    }
    
    pythonProcess = null;
    isPythonReady = false;
  }
}

/**
 * 显示系统通知
 */
function showNotification(title, body) {
  if (Notification.isSupported()) {
    new Notification({
      title,
      body,
      icon: path.join(__dirname, 'assets', 'icon.png')
    }).show();
  }
}

/**
 * 创建截图窗口
 */
function createCaptureWindow() {
  if (captureWindow) {
    captureWindow.focus();
    return;
  }

  // 获取主显示器尺寸
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.size;

  captureWindow = new BrowserWindow({
    width,
    height,
    x: 0,
    y: 0,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    fullscreen: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  captureWindow.loadFile(path.join(__dirname, 'capture.html'));

  // 窗口关闭时清理
  captureWindow.on('closed', () => {
    captureWindow = null;
  });

  // 捕获屏幕并发送给渲染进程
  captureScreen().then((sources) => {
    if (captureWindow && sources.length > 0) {
      captureWindow.webContents.send('screen-captured', sources[0].thumbnail.toDataURL());
    }
  });
}

/**
 * 创建结果窗口
 */
function createResultWindow(croppedImageData, selectionBounds) {
  if (resultWindow) {
    resultWindow.close();
  }

  // 计算窗口位置（在选区下方）
  const display = screen.getDisplayNearestPoint({ x: selectionBounds.x, y: selectionBounds.y });
  const workArea = display.workArea;
  
  const windowWidth = 450;
  const windowHeight = 350;
  
  let x = selectionBounds.x;
  let y = selectionBounds.y + selectionBounds.height + 10;
  
  // 确保窗口不超出屏幕
  if (x + windowWidth > workArea.x + workArea.width) {
    x = workArea.x + workArea.width - windowWidth - 20;
  }
  if (y + windowHeight > workArea.y + workArea.height) {
    y = selectionBounds.y - windowHeight - 10;
  }

  resultWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x,
    y,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  resultWindow.loadFile(path.join(__dirname, 'result.html'));

  // 窗口准备好后显示
  resultWindow.once('ready-to-show', () => {
    resultWindow.show();
    resultWindow.webContents.send('show-result', croppedImageData);
  });

  // 失去焦点时关闭
  resultWindow.on('blur', () => {
    if (resultWindow) {
      resultWindow.close();
    }
  });

  resultWindow.on('closed', () => {
    resultWindow = null;
  });
}

/**
 * 捕获屏幕
 */
async function captureScreen() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: primaryDisplay.size,
  });
  return sources;
}

/**
 * 应用初始化
 */
async function initializeApp() {
  try {
    await startPythonService();
    
    // 注册全局快捷键
    const shortcut = process.platform === 'darwin' ? 'Command+Shift+X' : 'Ctrl+Alt+D';
    const registered = globalShortcut.register(shortcut, async () => {
      console.log(`⚡ Global shortcut triggered: ${shortcut}`);
      
      // 检查后端是否就绪
      const ready = await checkServiceRunning();
      if (!ready) {
        showNotification(
          '服务启动中',
          '后端服务正在启动，请稍候...'
        );
        return;
      }
      
      createCaptureWindow();
    });

    if (registered) {
      console.log(`✅ Global shortcut registered: ${shortcut}`);
    } else {
      console.error(`❌ Failed to register global shortcut: ${shortcut}`);
    }
  } catch (err) {
    console.error('❌ Failed to initialize app:', err);
  }
}

// IPC 处理程序
ipcMain.handle('capture-area-selected', async (event, { imageData, bounds }) => {
  console.log('📸 Area selected:', bounds);
  
  // 关闭截图窗口
  if (captureWindow) {
    captureWindow.close();
    captureWindow = null;
  }

  // 检查选区大小（防误触）
  if (bounds.width < 15 || bounds.height < 15) {
    console.log('⚠️  Selection too small, ignoring');
    return;
  }

  // 创建结果窗口
  createResultWindow(imageData, bounds);
});

ipcMain.handle('close-result-window', () => {
  if (resultWindow) {
    resultWindow.close();
    resultWindow = null;
  }
});

// Electron 生命周期
app.whenReady().then(initializeApp);

app.on('window-all-closed', () => {
  // macOS 上保持应用运行
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    // macOS 上点击 dock 图标时
  }
});

app.on('will-quit', () => {
  // 注销全局快捷键
  globalShortcut.unregisterAll();
  // 停止 Python 服务
  stopPythonService();
});
