// 模拟数据库返回的预订数据
const bookings = [
  {
    booking_id: 'B1001',
    user_id: 'U12345',
    room_id: 'R1001',
    start_time: '14:00',
    end_time: '16:00',
    booking_date: '2023-11-05',
    status: 'pending',
    reason: 'Department Meeting111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
  },
  {
    booking_id: 'B1002',
    user_id: 'U67890',
    room_id: 'R1002',
    start_time: '09:00',
    end_time: '11:00',
    booking_date: '2023-10-28',
    status: 'approved',
    reason: 'Product Launch Prep'
  },
  {
    booking_id: 'B1003',
    user_id: 'U11223',
    room_id: 'R1003',
    start_time: '15:00',
    end_time: '17:00',
    booking_date: '2023-11-06',
    status: 'rejected',
    reason: 'Client Workshop'
  }
];

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

// 初始化标签切换功能
function initTabs() {
  const tabs = document.querySelectorAll('.approval-tabs .tab');

  const filterCards = (showPending) => {
    document.querySelectorAll('.approval-card').forEach(card => {
      const isPending = card.dataset.reservationId ===
        bookings.find(b => b.booking_id === card.dataset.reservationId && b.status === 'pending')?.booking_id;
      card.style.display = (showPending === isPending) ? 'flex' : 'none';
    });
  };

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      filterCards(tab.dataset.tab === 'pending');
    });
  });

  // 初始显示pending
  filterCards(true);
}

// 初始化页面
document.addEventListener('DOMContentLoaded', () => {
  renderApprovalCards();
  initTabs();
});