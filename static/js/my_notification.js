document.addEventListener('DOMContentLoaded', () => {
    const systemPanel = document.querySelector('.system-panel');
    const personalPanel = document.querySelector('.personal-panel');
    let activePanel = document.querySelector('.notification-panel.active');

    // Show loading status
    function showLoading(panel) {
        panel.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i> Loading...
            </div>
        `;
    }

    // Hidden loaded state
    function hideLoading(panel) {
        const loadingSpinner = panel.querySelector('.loading-spinner');
        if (loadingSpinner) loadingSpinner.remove();
    }

    // Unified error handling
    function showError(panel, message) {
        panel.innerHTML = `<p class="error">${message}</p>`;
    }

    // Get notification data
    async function loadNotifications() {
        try {
            // Display load status (keep current active panel)
            if (activePanel) showLoading(activePanel);

            const response = await fetch('https://www.diicsu.top:8000/notifications', {
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
                ${n.user_id !== null ? `
                    <button class="mark-read" ${n.status === 'read' ? 'disabled' : ''}>
                        ${n.status === 'unread' ? 'Mark Read' : 'Read'}
                    </button>
                ` : ''}
                ${n.user_id !== null ? `<button class="delete">Delete</button>` : ''}
            </div>
        </div>
    `).join('');

        // Dynamic binding event
        if (panelSelector === '.personal-panel') {
            panel.querySelectorAll('.mark-read').forEach(btn => {
                btn.addEventListener('click', handleMarkRead);
            });
        }
        panel.querySelectorAll('.delete').forEach(btn => {
            btn.addEventListener('click', handleDelete);
        });
    }

     // Mark read processed
    async function handleMarkRead(e) {
        const notificationId = e.target.closest('.notification-item').dataset.id;
        const markReadButton = e.target; // Get the click button

        try {
            const response = await fetch('https://www.diicsu.top:8000/update_notification_status', {
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
                // After marking as read, unread styles are removed
                e.target.closest('.notification-item').classList.remove('unread');

                // Disable button and change text to "Read"
                markReadButton.disabled = true;
                markReadButton.textContent = 'Read';
            } else {
                console.error('Failed to mark notification as read');
            }
        } catch (error) {
            console.error('Update Error:', error);
        }
    }
    // Delete processing
    async function handleDelete(e) {
        const notificationId = e.target.closest('.notification-item').dataset.id;
        try {
            const response = await fetch('https://www.diicsu.top:8000/delete_notification', {
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

    // TAB switching
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab, .notification-panel').forEach(el => {
                el.classList.remove('active');
            });
            this.classList.add('active');
            activePanel = document.querySelector(`.${this.dataset.tab}-panel`);
            activePanel.classList.add('active');
            loadNotifications(); // Reload when switching
        });
    });

    // Initial load
    loadNotifications();
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