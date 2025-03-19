document.addEventListener('DOMContentLoaded', () => {
    const systemPanel = document.querySelector('.system-panel');
    const personalPanel = document.querySelector('.personal-panel');
    let activePanel = document.querySelector('.notification-panel.active');

    // 显示加载状态
    function showLoading(panel) {
        panel.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i> Loading...
            </div>
        `;
    }

    // 隐藏加载状态
    function hideLoading(panel) {
        const loadingSpinner = panel.querySelector('.loading-spinner');
        if (loadingSpinner) loadingSpinner.remove();
    }

    // 统一错误处理
    function showError(panel, message) {
        panel.innerHTML = `<p class="error">${message}</p>`;
    }

    // 获取通知数据（Async/Await 版本）
    async function loadNotifications() {
        try {
            // 显示加载状态（保持当前活动面板）
            if (activePanel) showLoading(activePanel);

            const response = await fetch('http://localhost:8000/notifications', {
                credentials: 'include'
            });
            if (!response.ok) throw new Error('Network response was not ok');

            const { notifications } = await response.json();
            const systemData = notifications.filter(n => n.user_id === null);
            const personalData = notifications.filter(n => n.user_id !== null);

            renderNotifications(systemData, '.system-panel');
            renderNotifications(personalData, '.personal-panel');

        } catch (error) {
            console.error('Fetch Error:', error);
            if (activePanel) showError(activePanel, 'Failed to load notifications');
        } finally {
            if (activePanel) hideLoading(activePanel);
        }
    }

    // 渲染通知（合并事件绑定）
    function renderNotifications(data, panelSelector) {
        const panel = document.querySelector(panelSelector);
        panel.innerHTML = data.map(n => `
            <div class="notification-item ${n.status === 'unread' ? 'unread' : ''}"
                 data-id="${n.notification_id}">
                <div class="notification-header">
                    <span class="notification-type">${n.user_id === null ? '🔔 System' : '👤 Personal'}</span>
                    <span class="notification-time">${new Date(n.created_at).toLocaleString()}</span>
                </div>
                <div class="notification-content">
                    ${n.message}
                    ${n.user_id !== null ? `<button class="mark-read">Mark Read</button>` : ''}
                    ${n.user_id !== null ? `<button class="delete">Delete</button>` : ''}
                </div>
            </div>
        `).join('');

        // 动态绑定事件
        if (panelSelector === '.personal-panel') {
            panel.querySelectorAll('.mark-read').forEach(btn => {
                btn.addEventListener('click', handleMarkRead);
            });
        }
        panel.querySelectorAll('.delete').forEach(btn => {
            btn.addEventListener('click', handleDelete);
        });
    }

     // 标记已读处理
    async function handleMarkRead(e) {
        const notificationId = e.target.closest('.notification-item').dataset.id;
        const markReadButton = e.target; // 获取点击的按钮

        try {
            const response = await fetch('/update_notification_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    notification_id: notificationId,
                    status: 'read'
                }),
                credentials: 'include'
            });

            if (response.ok) {
                // 标记为已读后，移除未读样式
                e.target.closest('.notification-item').classList.remove('unread');

                // 禁用按钮并更改文本为 "Read"
                markReadButton.disabled = true;
                markReadButton.textContent = 'Read';
            } else {
                console.error('Failed to mark notification as read');
            }
        } catch (error) {
            console.error('Update Error:', error);
        }
    }
    // 删除处理
    async function handleDelete(e) {
        const notificationId = e.target.closest('.notification-item').dataset.id;
        try {
            const response = await fetch('/delete_notification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    notification_id: notificationId
                }),
                credentials: 'include'
            });

            if (response.ok) {
                e.target.closest('.notification-item').remove();
            } else {
                console.error('Failed to delete notification');
            }
        } catch (error) {
            console.error('Delete Error:', error);
        }
    }

    // 选项卡切换
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab, .notification-panel').forEach(el => {
                el.classList.remove('active');
            });
            this.classList.add('active');
            activePanel = document.querySelector(`.${this.dataset.tab}-panel`);
            activePanel.classList.add('active');
            loadNotifications(); // 切换时重新加载
        });
    });

    // 初始化加载
    loadNotifications();

    // 侧边栏切换（与原代码相同）
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');
    hamburger.addEventListener('click', () => sidebar.classList.toggle('active'));
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) sidebar.classList.remove('active');
    });
});