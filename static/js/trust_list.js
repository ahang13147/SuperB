const API_BASE = 'https://www.diicsu.top:8000';
const ENDPOINTS = {
    GET_ALL: '/get_room_trusted_users',
    ADD: '/insert_trusted_user',
    DELETE: '/delete_trusted_user'
};

window.onload = async () => {
    await loadData();
};

async function loadData() {
    try {
        const response = await fetch(`${API_BASE}${ENDPOINTS.GET_ALL}`);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

        const { data } = await response.json();
        renderData(data);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

function renderData(data) {
    const container = document.getElementById('roomContainer');
    container.innerHTML = '';

    const groupedData = data.reduce((acc, item) => {
        const key = item.room_id;
        if (!acc[key]) {
            acc[key] = {
                room_id: item.room_id,
                room_name: item.room_name || `Room ${item.room_id}`,
                users: []
            };
        }
        acc[key].users.push(item);
        return acc;
    }, {});

    Object.values(groupedData).forEach(room => {
        const box = document.createElement('div');
        box.className = 'room-box';
        box.innerHTML = `
            <h3>${room.room_name} (ID: ${room.room_id})</h3>
            <ul class="trusted-list">
                ${room.users.map(user => `
                    <li>
                        <span>${user.username} (ID: ${user.user_id})</span>
                        <button onclick="deleteUser(${room.room_id}, ${user.user_id})">
                            Delete
                        </button>
                    </li>
                `).join('')}
            </ul>
        `;
        container.appendChild(box);
    });
}

function searchTrustedList() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('.room-box').forEach(box => {
        const roomInfo = box.querySelector('h3').textContent.toLowerCase();
        const roomId = roomInfo.match(/id: (\d+)/)?.[1] || '';
        const roomName = roomInfo.replace(/\(id: \d+\)/g, '').trim();

        const match = roomId.includes(query) || roomName.includes(query);
        box.style.display = match ? 'block' : 'none';
    });
}

function openAddTrustedModal() {
    document.getElementById('addTrustedModal').style.display = 'flex';
}

function closeAddTrustedModal() {
    document.getElementById('addTrustedModal').style.display = 'none';
}

async function addTrustedUser() {
    const roomId = document.getElementById('roomId').value.trim();
    const userId = document.getElementById('userId').value.trim();
    const notes = document.getElementById('notes').value.trim();
    const addedBy = 1; // 假设当前用户ID为1

    if (!validateInput(roomId, userId, notes, addedBy)) return;

    try {
        const response = await fetch(`${API_BASE}${ENDPOINTS.ADD}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_id: parseInt(roomId),
                user_id: parseInt(userId),
                notes: notes,
                added_by: addedBy
            })
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.error);

        showSuccessModal('User added successfully!');
        closeAddTrustedModal();
        clearForm();
        await loadData();
    } catch (error) {
          // 打印到控制台
        console.error('Error:', error);

        // 弹出错误提示框
        alert(`Failed to add trusted user: ${error.message}`);
    }
}

async function deleteUser(roomId, userId) {
    if (!confirm(`Confirming the deletion of user ${userId}?`)) return;

    try {
        const response = await fetch(`${API_BASE}${ENDPOINTS.DELETE}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_id: roomId,
                user_id: userId
            })
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.message);

        showNotification(result.message, 'success');
        await loadData();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

function validateInput(roomId, userId, notes, addedBy) {
    let isValid = true;
    document.querySelectorAll('.error-msg').forEach(el => el.remove());

    if (!roomId || isNaN(roomId)) {
        showError('roomId', 'Please enter a valid room ID');
        isValid = false;
    }

    if (!userId || isNaN(userId)) {
        showError('userId', 'Please enter a valid user ID');
        isValid = false;
    }

    if (!notes) {
        showError('notes', 'Notes cannot be empty');
        isValid = false;
    }

    return isValid;
}

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const error = document.createElement('div');
    error.className = 'error-msg';
    error.textContent = message;
    field.parentNode.appendChild(error);
}

function clearForm() {
    ['roomId', 'userId', 'notes'].forEach(id => {
        document.getElementById(id).value = '';
    });
}

function showNotification(message, type) {
    const div = document.createElement('div');
    div.className = `notification ${type}`;
    div.textContent = message;

    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}

function showSuccessModal(message) {
    const modal = document.getElementById('successModal');
    const successMessage = document.getElementById('successMessage');
    successMessage.textContent = message;
    modal.style.display = 'flex';

    setTimeout(() => {
        modal.style.display = 'none';
    }, 3000);
}



document.addEventListener('DOMContentLoaded', function() {
    // 处理菜单分组点击
    document.querySelectorAll('.group-header').forEach(header => {
        header.addEventListener('click', function() {
            const group = this.closest('.menu-group');
            group.classList.toggle('active');

            // 关闭其他展开的菜单组
            document.querySelectorAll('.menu-group').forEach(otherGroup => {
                if (otherGroup !== group) {
                    otherGroup.classList.remove('active');
                }
            });
        });
    });

    // 移动端汉堡菜单切换
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    hamburger.addEventListener('click', function(e) {
        e.stopPropagation();
        sidebar.classList.toggle('active');
    });

    // 点击外部关闭侧边栏
    document.addEventListener('click', function(e) {
        if (sidebar.classList.contains('active') &&
            !e.target.closest('.sidebar') &&
            !e.target.closest('.hamburger-menu')) {
            sidebar.classList.remove('active');
        }
    });

    // 防止侧边栏内部点击触发关闭
    sidebar.addEventListener('click', function(e) {
        e.stopPropagation();
    });
});

