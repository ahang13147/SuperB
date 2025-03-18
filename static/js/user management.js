let userIdCounter = 1; // 自动分配 User ID

// 添加用户
document.getElementById("addUserForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    const role = document.getElementById("role").value;

    const userId = userIdCounter++; // 自动分配 User ID

    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${userId}</td>
        <td>${username}</td>
        <td>${email}</td>
        <td>${phone}</td>
        <td>${role}</td>
        <td>
            <button class="btn btn-edit btn-action" onclick="openEditModal(${userId}, '${username}', '${email}', '${phone}', '${role}')">Edit</button>
            <button class="btn btn-delete btn-action" onclick="deleteUser(${userId})">Delete</button>
        </td>
    `;

    document.getElementById("usersTableBody").appendChild(row);

    // 清空表单
    document.getElementById("addUserForm").reset();

    // 关闭弹窗
    const addUserModal = bootstrap.Modal.getInstance(document.getElementById("addUserModal"));
    addUserModal.hide();
});

// 打开编辑模态框
function openEditModal(userId, username, email, phone, role) {
    document.getElementById("editUsername").value = username;
    document.getElementById("editEmail").value = email;
    document.getElementById("editPhone").value = phone;
    document.getElementById("editRole").value = role;
    document.getElementById("editUserId").value = userId;

    const editModal = new bootstrap.Modal(document.getElementById("editModal"));
    editModal.show();
}

// 保存编辑
function saveEdit() {
    const userId = document.getElementById("editUserId").value;
    const username = document.getElementById("editUsername").value;
    const email = document.getElementById("editEmail").value;
    const phone = document.getElementById("editPhone").value;
    const role = document.getElementById("editRole").value;

    const row = document.querySelector(`#usersTableBody tr td:first-child`).parentElement;
    row.children[1].textContent = username;
    row.children[2].textContent = email;
    row.children[3].textContent = phone;
    row.children[4].textContent = role;

    const editModal = bootstrap.Modal.getInstance(document.getElementById("editModal"));
    editModal.hide();
}

// 删除用户
function deleteUser(userId) {
    const row = document.querySelector(`#usersTableBody tr td:first-child`).parentElement;
    row.remove();
}

// 搜索功能
document.getElementById("searchInput").addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase(); // 获取搜索关键词
    const rows = document.querySelectorAll("#usersTableBody tr");

    rows.forEach((row) => {
        const userId = row.children[0].textContent.toLowerCase();
        const username = row.children[1].textContent.toLowerCase();
        const role = row.children[4].textContent.toLowerCase();

        // 如果匹配 User ID、Username 或 Role，显示该行；否则隐藏
        if (userId.includes(searchTerm) || username.includes(searchTerm) || role.includes(searchTerm)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
});