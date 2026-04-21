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

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_base64: imageData,
        context: '',
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.status === 'success') {
      displayResult(result.data);
    } else {
      throw new Error(result.error || 'Unknown error');
    }
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('请求超时，请重试');
    }
    throw err;
  }
}

/**
 * 构建 ruby HTML
 */
function buildRubyHtml(tokens) {
  if (!tokens || tokens.length === 0) return '';
  return tokens
    .map((t) =>
      t.reading
        ? `<ruby>${escapeHtml(t.text)}<rt>${escapeHtml(t.reading)}</rt></ruby>`
        : escapeHtml(t.text)
    )
    .join('');
}

/**
 * 显示结果
 */
function displayResult(data) {
  // 原文（带 ruby 振假名）
  const originalTextEl = document.getElementById('original-text');
  if (data.furigana_tokens && data.furigana_tokens.length > 0) {
    originalTextEl.innerHTML = buildRubyHtml(data.furigana_tokens);
  } else {
    originalTextEl.textContent = data.original_text || 'N/A';
  }

  // 翻译
  document.getElementById('translation').textContent = data.translation || 'N/A';

  // 词汇列表
  const vocabList = document.getElementById('vocab-list');
  vocabList.innerHTML = '';

  if (data.vocabulary && data.vocabulary.length > 0) {
    data.vocabulary.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'vocab-item';

      const wordSpan = document.createElement('span');
      wordSpan.className = 'vocab-word';
      if (item.reading) {
        wordSpan.innerHTML = `<ruby>${escapeHtml(item.word)}<rt>${escapeHtml(
          item.reading
        )}</rt></ruby>`;
      } else {
        wordSpan.textContent = item.word;
      }

      const posBadge = document.createElement('span');
      posBadge.className = 'pos-badge';
      posBadge.textContent = item.part_of_speech || '';

      const meaningSpan = document.createElement('span');
      meaningSpan.className = 'vocab-meaning';
      meaningSpan.textContent = item.meaning || '';

      div.appendChild(wordSpan);
      div.appendChild(posBadge);
      div.appendChild(meaningSpan);
      vocabList.appendChild(div);
    });
  } else {
    vocabList.innerHTML = '<div class="section-content">无词汇数据</div>';
  }

  // 语法解析
  const grammarList = document.getElementById('grammar-list');
  grammarList.innerHTML = '';

  if (data.grammar_analysis && data.grammar_analysis.length > 0) {
    data.grammar_analysis.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'grammar-item';

      const header = document.createElement('div');
      header.className = 'grammar-header';

      const wordSpan = document.createElement('span');
      wordSpan.className = 'grammar-word';
      wordSpan.textContent = item.word || '';

      const posBadge = document.createElement('span');
      posBadge.className = 'pos-badge';
      posBadge.textContent = item.part_of_speech || '';

      header.appendChild(wordSpan);
      header.appendChild(posBadge);

      const explanation = document.createElement('div');
      explanation.className = 'grammar-explanation';
      explanation.textContent = item.explanation || '';

      div.appendChild(header);
      div.appendChild(explanation);
      grammarList.appendChild(div);
    });
  } else {
    grammarList.innerHTML = '<div class="section-content">无语法解析数据</div>';
  }

  // 例句
  const exampleList = document.getElementById('example-list');
  exampleList.innerHTML = '';

  if (data.example_sentences && data.example_sentences.length > 0) {
    data.example_sentences.forEach((ex) => {
      const div = document.createElement('div');
      div.className = 'example-item';

      const jpDiv = document.createElement('div');
      jpDiv.className = 'example-jp';
      jpDiv.textContent = ex.japanese || '';

      const cnDiv = document.createElement('div');
      cnDiv.className = 'example-cn';
      cnDiv.textContent = ex.chinese || '';

      div.appendChild(jpDiv);
      div.appendChild(cnDiv);
      exampleList.appendChild(div);
    });
  } else {
    exampleList.innerHTML = '<div class="section-content">无例句数据</div>';
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
