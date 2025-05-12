/**
 * 密码强度检测工具
 * 
 * 检测密码强度，并在指定容器中显示强度指示器。
 * 要求:
 * - 至少8位长度
 * - 包含大写字母
 * - 包含小写字母
 * - 包含数字
 * - 包含特殊字符
 */

class PasswordStrengthMeter {
  constructor(passwordInput, containerElement) {
    this.passwordInput = passwordInput;
    this.container = containerElement;
    this.requirements = [
      { regex: /.{8,}/, label: '至少8个字符' },
      { regex: /[A-Z]/, label: '包含大写字母' },
      { regex: /[a-z]/, label: '包含小写字母' },
      { regex: /[0-9]/, label: '包含数字' },
      { regex: /[^A-Za-z0-9]/, label: '包含特殊字符' }
    ];
    
    this.init();
  }
  
  init() {
    // 创建HTML结构
    this.container.innerHTML = `
      <div class="password-strength-meter">
        <div class="strength-meter-bar">
          <div class="strength-meter-fill"></div>
        </div>
        <div class="strength-meter-info">
          <div class="strength-text"></div>
          <ul class="requirement-list"></ul>
        </div>
      </div>
    `;
    
    // 引用DOM元素
    this.strengthBar = this.container.querySelector('.strength-meter-fill');
    this.strengthText = this.container.querySelector('.strength-text');
    this.requirementList = this.container.querySelector('.requirement-list');
    
    // 绑定事件
    this.passwordInput.addEventListener('input', () => this.checkPassword());
    
    // 应用样式
    this.applyStyles();
    
    // 初始化需求列表
    this.initRequirementList();
    
    // 初始检查
    this.checkPassword();
  }
  
  applyStyles() {
    // 添加基本样式
    const style = document.createElement('style');
    style.textContent = `
      .password-strength-meter {
        margin-top: 8px;
        width: 100%;
      }
      .strength-meter-bar {
        height: 5px;
        background-color: #e0e0e0;
        border-radius: 2px;
        margin-bottom: 5px;
        width: 100%;
      }
      .strength-meter-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.3s ease, background-color 0.3s ease;
        width: 0;
      }
      .strength-meter-info {
        width: 100%;
      }
      .strength-text {
        font-size: 12px;
        margin-bottom: 5px;
        font-weight: bold;
      }
      .requirement-list {
        padding-left: 18px;
        margin: 5px 0;
        font-size: 12px;
        display: flex;
        flex-wrap: wrap;
        list-style-type: none;
        padding: 0;
      }
      .requirement-item {
        margin: 3px 0;
        padding-left: 15px;
        position: relative;
        flex-basis: 50%;
        box-sizing: border-box;
      }
      .requirement-item:before {
        content: "•";
        position: absolute;
        left: 0;
      }
      .requirement-met {
        color: #10b981;
      }
      .requirement-not-met {
        color: #6b7280;
      }
      .strength-very-weak { color: #ef4444; }
      .strength-weak { color: #f97316; }
      .strength-medium { color: #f59e0b; }
      .strength-strong { color: #10b981; }
      .strength-very-strong { color: #059669; }
    `;
    document.head.appendChild(style);
  }
  
  initRequirementList() {
    // 初始化需求列表
    this.requirementList.innerHTML = '';
    
    this.requirements.forEach(req => {
      const li = document.createElement('li');
      li.classList.add('requirement-item', 'requirement-not-met');
      li.textContent = req.label;
      this.requirementList.appendChild(li);
    });
  }
  
  checkPassword() {
    const password = this.passwordInput.value;
    const requirementItems = this.requirementList.querySelectorAll('.requirement-item');
    
    // 检查每个需求
    let metCount = 0;
    this.requirements.forEach((req, index) => {
      const isMet = req.regex.test(password);
      requirementItems[index].classList.toggle('requirement-met', isMet);
      requirementItems[index].classList.toggle('requirement-not-met', !isMet);
      if (isMet) metCount++;
    });
    
    // 计算强度百分比
    const strengthPercent = (metCount / this.requirements.length) * 100;
    
    // 设置填充宽度
    this.strengthBar.style.width = `${strengthPercent}%`;
    
    // 设置强度文本和颜色
    if (password.length === 0) {
      this.strengthText.textContent = '';
      this.strengthBar.style.backgroundColor = '#e0e0e0';
      this.container.querySelectorAll('.requirement-item').forEach(item => {
        item.classList.replace('requirement-met', 'requirement-not-met');
      });
      return;
    }
    
    let strengthClass = '';
    let strengthLabel = '';
    
    if (metCount === 0) {
      strengthLabel = '非常弱';
      strengthClass = 'strength-very-weak';
      this.strengthBar.style.backgroundColor = '#ef4444';
    } else if (metCount === 1) {
      strengthLabel = '弱';
      strengthClass = 'strength-weak';
      this.strengthBar.style.backgroundColor = '#f97316';
    } else if (metCount === 2 || metCount === 3) {
      strengthLabel = '中等';
      strengthClass = 'strength-medium';
      this.strengthBar.style.backgroundColor = '#f59e0b';
    } else if (metCount === 4) {
      strengthLabel = '强';
      strengthClass = 'strength-strong';
      this.strengthBar.style.backgroundColor = '#10b981';
    } else {
      strengthLabel = '非常强';
      strengthClass = 'strength-very-strong';
      this.strengthBar.style.backgroundColor = '#059669';
    }
    
    // 更新强度文本
    this.strengthText.textContent = `密码强度: ${strengthLabel}`;
    
    // 移除所有强度类
    this.strengthText.classList.remove(
      'strength-very-weak', 
      'strength-weak', 
      'strength-medium', 
      'strength-strong', 
      'strength-very-strong'
    );
    
    // 添加相应的强度类
    this.strengthText.classList.add(strengthClass);
  }
}

// 检查提交的密码是否满足所有要求
function isPasswordValid(password) {
  // 密码要求
  const requirements = [
    { regex: /.{8,}/, label: '至少8个字符' },
    { regex: /[A-Z]/, label: '包含大写字母' },
    { regex: /[a-z]/, label: '包含小写字母' },
    { regex: /[0-9]/, label: '包含数字' },
    { regex: /[^A-Za-z0-9]/, label: '包含特殊字符' }
  ];
  
  // 检查每个需求
  for (const req of requirements) {
    if (!req.regex.test(password)) {
      return { valid: false, message: `密码必须${req.label}！` };
    }
  }
  
  return { valid: true, message: '' };
} 