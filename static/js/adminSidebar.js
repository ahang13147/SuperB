// adminSidebar.js
// ============ 动态加载侧边栏 ============
function loadSidebar() {
  fetch('/adminSidebar')  // 调用 Flask 路由
    .then(response => response.text())
    .then(data => {
      // 插入侧边栏到容器
      const sidebarContainer = document.querySelector('.main-container');
      if (sidebarContainer) {
        sidebarContainer.insertAdjacentHTML('afterbegin', data);
        // 加载完成后自动高亮当前页
        highlightCurrentPage();
      }
    })
    .catch(error => {
      console.error('Error loading sidebar:', error);
    });
}
// ========== 自动高亮当前页面 ==========
function highlightCurrentPage() {
  // 获取当前页面路径（标准化处理）
  const currentPath = window.location.pathname
    .split("/")
    .pop()
    .toLowerCase()
    .replace(/(\.html|\/)/g, "");

  // 遍历侧边栏所有导航项
  document.querySelectorAll(".adminSidebar .nav-item").forEach(item => {
    // 提取导航项路径（同样标准化）
    const itemPath = item.getAttribute("href")
      .toLowerCase()
      .replace(/(\.html|\/)/g, "");

    // 精确匹配路径
    if (currentPath === itemPath) {
      item.classList.add("active");
    }
  });
}

// ========== 初始化侧边栏 ==========
document.addEventListener("DOMContentLoaded", function() {
  loadSidebar(); // 页面加载时执行
});