// 模拟数据库返回的预订数据
let bookings = [];

// 动态生成审批卡片
function renderApprovalCards() {
  const container = document.querySelector('.approvals-container');
  container.innerHTML = ''; // 清空现有内容

  bookings.forEach(booking => {
    const card = document.createElement('div');
    card.className = `approval-card ${booking.status === 'pending' ? '' : 'reviewed'}`;
    card.dataset.reservationId = booking.booking_id;

    // 构建卡片内容
    card.innerHTML = `
      <div class="reservation-info">
        <label>Booking ID:</label>
        <span>${booking.booking_id}</span>
      </div>
      <div class="reservation-info">
        <label>User ID:</label>
        <span>${booking.user_id}</span>
      </div>
      <div class="reservation-info">
        <label>Room ID:</label>
        <span>${booking.room_id}</span>
      </div>
      <div class="reservation-info">
        <label>Date:</label>
        <span>${booking.booking_date}</span>
      </div>
      <div class="reservation-info">
        <label>Time:</label>
        <span>${booking.start_time} - ${booking.end_time}</span>
      </div>
      <div class="reservation-info">
        <label>Reason:</label>
        <span class="reason-text">${booking.reason}</span>
      </div>
      ${booking.status === 'pending' ? `
        <div class="approval-actions">
          <button class="approve-btn">Approve</button>
          <button class="reject-btn">Reject</button>
        </div>
      ` : `<div class="status-indicator ${booking.status}">${booking.status.toUpperCase()}</div>`}
    `;

    container.appendChild(card);
  });

  // 重新绑定事件监听器
  bindButtonEvents();
  handleReasonOverflow();
}

// 检测 Reason 文本是否超出，并添加省略号
function handleReasonOverflow() {
  document.querySelectorAll('.reason-text').forEach(span => {
    let reason = span.innerText.trim();

    // 先检查是否超出容器
    if (span.scrollHeight > span.clientHeight || span.scrollWidth > span.clientWidth) {
      let ellipsis = document.createElement("span");
      ellipsis.classList.add("ellipsis");
      ellipsis.innerHTML = "...";
      ellipsis.style.cursor = "pointer";
      ellipsis.style.color = "#007bff";
      ellipsis.style.fontWeight = "bold";
      ellipsis.style.marginLeft = "5px";

      // 点击 `...` 显示完整内容
      ellipsis.addEventListener("click", function (event) {
        event.stopPropagation(); // 阻止冒泡，防止误触
        showFullText(reason);
      });

      span.innerHTML = reason.substring(0, 50) + " "; // 只显示前50字符
      span.appendChild(ellipsis);
    }
  });
}

// 显示完整文本（可替换为 Modal）
function showFullText(fullText) {
  alert(fullText); // 你可以换成自定义 Modal
}

// 处理审批操作
function handleApproval(action, card) {
  const bookingId = card.dataset.reservationId;

  fetch(`/api/bookings/${bookingId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: action.toLowerCase() })
  })
    .then(response => {
      if (!response.ok) throw new Error('Update failed');
      const booking = bookings.find(b => b.booking_id === bookingId);
      booking.status = action.toLowerCase();
      renderApprovalCards();
      alert(`${action} reservation ID: ${bookingId}`);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('操作失败，请稍后重试');
    });
}

// 绑定按钮事件
function bindButtonEvents() {
  document.querySelectorAll('.approve-btn, .reject-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.classList.contains('approve-btn') ? 'Approved' : 'Rejected';
      const card = btn.closest('.approval-card');
      handleApproval(action, card);
    });
  });
}

// 获取已完成的工作流预订
function fetchFinishedBookings() {
  fetch('http://localhost:5000/finished-workflow-bookings')
    .then(response => response.json())
    .then(data => {
      bookings = data;
      renderApprovalCards();
    })
    .catch(error => {
      console.error('Error fetching finished bookings:', error);
    });
}

// 获取待处理的预订
function fetchPendingBookings() {
  fetch('http://localhost:5000/pending-bookings')
    .then(response => response.json())
    .then(data => {
      bookings = data;
      renderApprovalCards();
    })
    .catch(error => {
      console.error('Error fetching pending bookings:', error);
    });
}

// 初始化标签切换功能
function initTabs() {
  const tabs = document.querySelectorAll('.approval-tabs .tab');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      if (tab.dataset.tab === 'pending') {
        fetchPendingBookings();
      } else if (tab.dataset.tab === 'finished') {
        fetchFinishedBookings();
      }
    });
  });

  // 初始显示pending
  fetchPendingBookings();
}

// 初始化页面
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
});