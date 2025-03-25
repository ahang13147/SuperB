// adminSidebar.js
// ============ Load the sidebar dynamically ============
function loadSidebar() {
  fetch('/adminSidebar')  // Call Flask routing
    .then(response => response.text())
    .then(data => {
      // Insert sidebar into container
      const sidebarContainer = document.querySelector('.main-container');
      if (sidebarContainer) {
        sidebarContainer.insertAdjacentHTML('afterbegin', data);
        // Automatically highlight the current page after loading
        highlightCurrentPage();
      }
    })
    .catch(error => {
      console.error('Error loading sidebar:', error);
    });
}
// ========== Automatically highlight the current page ==========
function highlightCurrentPage() {
  // Get the current page path (standardized processing)
  const currentPath = window.location.pathname
    .split("/")
    .pop()
    .toLowerCase()
    .replace(/(\.html|\/)/g, "");

  // Traverse all navigation items in the sidebar
  document.querySelectorAll(".adminSidebar .nav-item").forEach(item => {
    // Extract navigation item path (again standardized)
    const itemPath = item.getAttribute("href")
      .toLowerCase()
      .replace(/(\.html|\/)/g, "");

    // Exact matching path
    if (currentPath === itemPath) {
      item.classList.add("active");
    }
  });
}

// ========== Initialize the sidebar ==========
document.addEventListener("DOMContentLoaded", function() {
  loadSidebar(); 
});