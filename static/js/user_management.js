document.addEventListener('DOMContentLoaded', function () {
    loadUsers(); // 页面加载时获取用户数据

    // 添加用户表单提交事件
    document.getElementById('addUserForm').addEventListener('submit', function (e) {
        e.preventDefault();
        addUser();
    });

    // 搜索功能实时过滤
    document.querySelector('.search-box input').addEventListener('input', function () {
        filterUsers(this.value.trim().toLowerCase());
    });
});

// 加载用户列表
function loadUsers() {
    fetch('https://www.diicsu.top:8000/get_all_users_admin')
        .then(response => response.json())
        .then(data => {
            populateUsersTable(data.users);
        })
        .catch(error => {
            console.error('Error loading users:', error);
            alert('Failed to load users');
        });
}

// 填充表格数据
function populateUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = ''; // 清空现有数据

    users.forEach(user => {
        const row = `
            <tr data-user-id="${user.user_id}">
                <td>${user.user_id}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${user.phone_number}</td>
                <td>${user.role}</td>
                <td>
                    <button class="btn btn-edit" onclick="openEditModal(${user.user_id})">Edit</button>
                    <button class="btn btn-delete" onclick="deleteUser(${user.user_id})">Delete</button>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// 添加新用户
function addUser() {
    const userData = {
        username: document.getElementById('username').value.trim(),
        email: document.getElementById('email').value.trim().toLowerCase(),
        phone_number: document.getElementById('phone').value.trim(),
        role: document.getElementById('role').value
    };

    fetch('https://www.diicsu.top:8000/insert_users_admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    })
        .then(response => {
            // 统一解析 JSON
            return response.json().then(data => {
                if (!response.ok) {
                    throw data; // 将错误数据抛出
                }
                return data; // 成功时返回数据
            });
        })
        .then(data => {
            // 使用Bootstrap API关闭模态框
            const addModalEl = document.getElementById('addUserModal');
            const addModal = bootstrap.Modal.getInstance(addModalEl);
            if (addModal) {
                addModal.hide();
            } else {
                new bootstrap.Modal(addModalEl).hide(); // 确保模态框关闭
            }
            document.getElementById('addUserForm').reset();
            loadUsers();
            alert('User added successfully!');
        })
        .catch(error => { /* 错误处理不变 */ });
}


// 打开编辑模态框
function openEditModal(userId) {
    fetch(`https://www.diicsu.top:8000/get_all_users_admin`)
        .then(response => response.json())
        .then(data => {
            const user = data.users.find(u => u.user_id === userId);
            if (!user) throw new Error('User not found');

            document.getElementById('editUserId').value = user.user_id;
            document.getElementById('editUsername').value = user.username;
            document.getElementById('editEmail').value = user.email; // 确保填充邮箱
            document.getElementById('editPhone').value = user.phone_number;
            document.getElementById('editRole').value = user.role;

            // 使用原生Bootstrap API显示模态框
            const editModalEl = document.getElementById('editModal');
            const editModal = new bootstrap.Modal(editModalEl);
            editModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load user data');
        });
}

// 保存编辑
function saveEdit() {
    const userData = {
        user_id: parseInt(document.getElementById('editUserId').value),
        username: document.getElementById('editUsername').value.trim(),
        phone_number: document.getElementById('editPhone').value.trim(),
        role: document.getElementById('editRole').value
    };

    fetch('https://www.diicsu.top:8000/update_user_admin', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    })
        .then(response => {
            // ...原有处理逻辑...
        })
        .then(data => {
            const editModalEl = document.getElementById('editModal');
            const editModal = bootstrap.Modal.getInstance(editModalEl);
            editModal.hide(); // 使用原生API关闭模态框
            loadUsers();
            alert('User updated successfully!');
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.error || 'Failed to update user');
        });
}

// 删除用户（预留接口）
function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        // 预留删除接口调用
        console.log('Delete user ID:', userId);
        alert('Delete functionality not implemented yet');
    }
}

// 实时过滤用户
function filterUsers(searchTerm) {
    const rows = document.querySelectorAll('#usersTableBody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}