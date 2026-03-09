// 结果展示逻辑
const API_BASE_URL = 'http://127.0.0.1:8000';

// DOM 元素
const loadingEl = document.getElementById('loading');
const resultEl = document.getElementById('result');
const errorEl = document.getElementById('error');
const closeBtn = document.getElementById('close-btn');

// 关闭按钮
document.getElementById('close-btn').addEventListener('click', () => {
  electronAPI.closeResultWindow();
});

// ESC 键关闭
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    electronAPI.closeResultWindow();
  }
});

// 接收显示结果事件
electronAPI.onShowResult(async (imageData) => {
  console.log('🎯 Showing result window with image');
  
  if (!imageData) {
    showError('无法获取截图数据');
    return;
  }
  
  try {
    await analyzeImage(imageData);
  } catch (err) {
    console.error('Analysis failed:', err);
    showError('分析失败: ' + err.message);
  }
});

/**
 * 分析图片
 */
async function analyzeImage(imageData) {
  showLoading();
  
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_base64: imageData,
      context: '',
    }),
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const result = await response.json();
  
  if (result.status === 'success') {
    displayResult(result.data);
  } else {
    throw new Error(result.error || 'Unknown error');
  }
}

/**
 * 显示结果
 */
function displayResult(data) {
  // 原文
  document.getElementById('original-text').textContent = data.original_text || 'N/A';
  document.getElementById('furigana').textContent = data.furigana || '';
  document.getElementById('translation').textContent = data.translation || 'N/A';
  
  // 语法解析
  const grammarList = document.getElementById('grammar-list');
  grammarList.innerHTML = '';
  
  if (data.grammar_analysis && data.grammar_analysis.length > 0) {
    data.grammar_analysis.forEach(item => {
      const div = document.createElement('div');
      div.className = 'grammar-item';
      div.innerHTML = `
        <div class="grammar-word">${escapeHtml(item.word)}</div>
        <div class="grammar-explanation">${escapeHtml(item.explanation)}</div>
      `;
      grammarList.appendChild(div);
    });
  } else {
    grammarList.innerHTML = '<div class="section-content">无语法解析数据</div>';
  }
  
  // 例句
  if (data.example_sentence) {
    document.getElementById('example-jp').textContent = data.example_sentence.japanese || 'N/A';
    document.getElementById('example-cn').textContent = data.example_sentence.chinese || 'N/A';
  }
  
  showResult();
}

/**
 * 显示加载状态
 */
function showLoading() {
  loadingEl.classList.remove('hidden');
  resultEl.classList.add('hidden');
  errorEl.style.display = 'none';
}

/**
 * 显示结果
 */
function showResult() {
  loadingEl.classList.add('hidden');
  resultEl.classList.remove('hidden');
  errorEl.style.display = 'none';
}

/**
 * 显示错误
 */
function showError(message) {
  loadingEl.classList.add('hidden');
  resultEl.classList.add('hidden');
  errorEl.style.display = 'flex';
  document.getElementById('error-message').textContent = message;
}

/**
 * HTML 转义
 */
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
