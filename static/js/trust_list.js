    const API_BASE = 'http://localhost:8000';
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
            const response = await fetch(`http://localhost:8000//get_room_trusted_users`);
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

    async function addTrustedUser() {
        const roomId = document.getElementById('roomId').value.trim();
        const userId = document.getElementById('userId').value.trim();
        const notes = document.getElementById('notes').value.trim();
        const addedBy = 1;

        if (!validateInput(roomId, userId, notes, addedBy)) return;

        try {
            const response = await fetch(`http://localhost:8000/insert_trusted_user`, {
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
            if (!response.ok) throw new Error(result.message);

            showSuccessModal('User added successfully!');
            clearForm();
            await loadData();
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }

    async function deleteUser(roomId, userId) {
        if (!confirm(`Confirming the deletion of a user ${userId}?`)) return;

        try {
            const response = await fetch(`http://localhost:8000/delete_trusted_user`, {
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
            showError('userId', 'Please enter a user room ID');
            isValid = false;
        }

        if (!notes) {
            showError('notes', 'Remarks cannot be empty');
            isValid = false;
        }

        if (!addedBy || isNaN(addedBy)) {
            showError('global', 'User is not logged in or session has expired');
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

    function searchTrustedList() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        document.querySelectorAll('.room-box').forEach(box => {
            const roomId = box.querySelector('h3').textContent.match(/ID: (\d+)/)[1];
            box.style.display = roomId.includes(query) ? 'block' : 'none';
        });
    }

    function showSuccessModal(message) {
    // 创建弹窗元素
    const modal = document.createElement('div');
    modal.className = 'success-modal';
    modal.innerHTML = `
        <div class="success-modal-content">
            <h2>Success!</h2>
            <p>${message}</p>
        </div>
    `;

    // 将弹窗添加到页面
    document.body.appendChild(modal);

    // 3秒后自动关闭弹窗
    setTimeout(() => {
        modal.remove();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    hamburger.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });

    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
});

