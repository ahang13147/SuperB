document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    // 侧边栏菜单切换
    hamburger.addEventListener('click', function () {
        sidebar.classList.toggle('active');
    });

    // 点击外部关闭侧边栏
    document.addEventListener('click', function (e) {
        if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    // 响应式布局切换
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            document.querySelector('.room-table-container').style.display = 'block';
            document.querySelector('.room-cards-container').style.display = 'none';
        } else {
            document.querySelector('.room-table-container').style.display = 'none';
            document.querySelector('.room-cards-container').style.display = 'grid';
        }
    });

    // 初始化加载房间数据
    loadRooms();
});

let currentEditingRoomId = null;
let activeRooms = [];
let deletedRooms = [];

// 加载房间数据
async function loadRooms() {
    try {
        const response = await fetch('https://101.200.197.132:8000/rooms');
        const data = await response.json();
        activeRooms = data.rooms;
        renderTables();
    } catch (error) {
        console.error('Failed to load:', error);
        alert('Unable to load room data, please check network connection');
    }
}

// 将room_type数字转换为文本
function getRoomTypeText(roomType) {
    switch (roomType) {
        case 0: return "Available for all";
        case 1: return "Staff only";
        case 2: return "Trusted user only";
        default: return "Unknown";
    }
}

// 渲染表格和卡片
function renderTables() {
    const activeTbody = document.querySelector('#activeTable tbody');
    const deletedTbody = document.querySelector('#deletedTable tbody');
    const cardsContainer = document.querySelector('.room-cards-container');

    // 桌面端表格渲染
    activeTbody.innerHTML = activeRooms.map(room => `
        <tr class="room-item" data-room-id="${room.room_id}">
            <td>${room.room_id}</td>
            <td>${room.room_name}</td>
            <td>${room.capacity}</td>
            <td>${room.location}</td>
            <td>${room.equipment}</td>
            <td>${getRoomTypeText(room.room_type)}</td>
            <td class="room-actions">
                <button class="edit-btn" onclick="openEditModal(${room.room_id})">Edit</button>
                <button class="delete-btn" onclick="softDeleteRoom(${room.room_id})">Delete</button>
            </td>
        </tr>
    `).join('');

    // 移动端卡片渲染
    cardsContainer.innerHTML = activeRooms.map(room => `
        <div class="room-card" data-room-id="${room.room_id}">
            <div class="card-header">
                <span class="card-id">ID: ${room.room_id}</span>
                <h3 class="card-title">${room.room_name}</h3>
            </div>
            <div class="card-details">
                <div>
                    <span class="card-label">Capacity:</span>
                    <span class="card-value">${room.capacity}</span>
                </div>
                <div>
                    <span class="card-label">Location:</span>
                    <span class="card-value">${room.location}</span>
                </div>
                <div>
                    <span class="card-label">Equipment:</span>
                    <span class="card-value">${room.equipment}</span>
                </div>
                <div>
                    <span class="card-label">Room Type:</span>
                    <span class="card-value">${getRoomTypeText(room.room_type)}</span>
                </div>
            </div>
            <div class="card-actions">
                <button class="edit-btn" onclick="openEditModal(${room.room_id})">Edit</button>
                <button class="delete-btn" onclick="softDeleteRoom(${room.room_id})">Delete</button>
            </div>
        </div>
    `).join('');

    // 已删除表格渲染
    deletedTbody.innerHTML = deletedRooms.map(room => `
        <tr class="deleted-item">
            <td>${room.room_id}</td>
            <td>${room.room_name}</td>
            <td>${room.capacity}</td>
            <td>${room.location}</td>
            <td>${room.equipment}</td>
            <td>${getRoomTypeText(room.room_type)}</td>
            <td>${new Date().toLocaleString()}</td>
        </tr>
    `).join('');
}

// 打开编辑模态框
function openEditModal(roomId) {
    const room = activeRooms.find(r => r.room_id == roomId);
    if (!room) return;

    currentEditingRoomId = roomId;
    document.getElementById('editRoomId').value = roomId;
    document.getElementById('editRoomName').value = room.room_name;
    document.getElementById('editCapacity').value = room.capacity;
    document.getElementById('editLocation').value = room.location;
    document.getElementById('editEquipment').value = room.equipment;
    document.getElementById('editRoomType').value = room.room_type; // 设置 room type

    document.getElementById('editModal').style.display = 'flex';
}

// 关闭编辑模态框
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// 保存编辑后的房间信息
async function saveRoom() {
    const updatedData = {
        room_name: document.getElementById('editRoomName').value,
        capacity: parseInt(document.getElementById('editCapacity').value),
        location: document.getElementById('editLocation').value,
        equipment: document.getElementById('editEquipment').value,
        type: parseInt(document.getElementById('editRoomType').value) // 获取 room type
    };

    try {
        const response = await fetch(`https://101.200.197.132:8000/update-room/${currentEditingRoomId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });

        if (response.ok) {
            const index = activeRooms.findIndex(r => r.room_id == currentEditingRoomId);
            activeRooms[index] = { ...activeRooms[index], ...updatedData };
            renderTables();
            closeEditModal();
            alert('Update successfully');
        } else {
            alert('Failed to load');
        }
    } catch (error) {
        console.error('Request error:', error);
        alert('Network request failed');
    }
}

// 软删除房间
async function softDeleteRoom(roomId) {
    if (confirm(`Are you sure to delete ${roomId} 吗？`)) {
        try {
            const response = await fetch('https://101.200.197.132:8000/update_room_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: roomId,
                    action: 'delete' // 操作类型为删除
                })
            });

            const result = await response.json();

            if (response.ok) {
                // 从 activeRooms 中移除该房间
                const index = activeRooms.findIndex(r => r.room_id == roomId);
                // 重新加载房间数据
                await loadRooms();
                showDeleteSuccessModal();
                if (index > -1) {
                    const deletedRoom = activeRooms.splice(index, 1)[0];
                    deletedRooms.push({ ...deletedRoom, deletedAt: new Date() });
                    renderTables();
                    showDeleteSuccessModal();
                }
            } else {
                alert(`Failed to delete: ${result.error}`);
            }
        } catch (error) {
            console.error('Request error:', error);
            alert('Network request failed');
        }
    }
}

// 切换标签页
function showTab(tabId) {
    // 桌面端表格切换
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.room-table').forEach(t => t.style.display = 'none');
    document.querySelector(`#${tabId}Table`).style.display = 'table';
    document.querySelector(`[onclick="showTab('${tabId}')"]`).classList.add('active');

    // 新增移动端卡片切换逻辑
    const cardsContainer = document.querySelector('.room-cards-container');
    if (window.innerWidth <= 768) {
        cardsContainer.innerHTML = (tabId === 'active' ? activeRooms : deletedRooms).map(room => `
            <div class="room-card" data-room-id="${room.room_id}">
                <div class="card-header">
                    <span class="card-id">ID: ${room.room_id}</span>
                    <h3 class="card-title">${room.room_name}</h3>
                </div>
                <div class="card-details">
                <div>
                    <span class="card-label">Capacity:</span>
                    <span class="card-value">${room.capacity}</span>
                </div>
                <div>
                    <span class="card-label">Location:</span>
                    <span class="card-value">${room.location}</span>
                </div>
                <div>
                    <span class="card-label">Equipment:</span>
                    <span class="card-value">${room.equipment}</span>
                </div>
                <div>
                    <span class="card-label">Room Type:</span>
                    <span class="card-value">${getRoomTypeText(room.room_type)}</span>
                </div>
                </div>
                ${tabId === 'active' ? `
                <div class="card-actions">
                    <button class="edit-btn" onclick="openEditModal(${room.room_id})">Edit</button>
                    <button class="delete-btn" onclick="softDeleteRoom('${room.room_id}')">Delete</button>
                </div>
                ` : ''}
            </div>
        `).join('');
    }
}

// 打开添加房间模态框
function openAddRoomModal() {
    document.getElementById('addRoomModal').style.display = 'flex';
}

// 关闭添加房间模态框
function closeAddRoomModal() {
    document.getElementById('addRoomModal').style.display = 'none';
}

// 添加新房间
async function addRoom() {
    
    const newRoom = {
        room_name: document.getElementById('roomName').value,
        capacity: parseInt(document.getElementById('capacity').value),
        location: document.getElementById('location').value,
        equipment: document.getElementById('equipment').value,
        room_type: parseInt(document.getElementById('roomType').value)
    };

    try {
        const response = await fetch('https://101.200.197.132:8000/insert_room', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newRoom)
        });

        if (response.ok) {
            const result = await response.json();
            activeRooms.push({ ...newRoom, room_id: result.room_id });
            renderTables();
            closeAddRoomModal();
            showAddSuccessModal();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// 显示添加成功提示
function showAddSuccessModal() {
    const successModal = document.getElementById('addSuccessModal');
    successModal.style.display = 'flex';
    setTimeout(() => successModal.style.display = 'none', 2000);
}

// 显示删除成功提示
function showDeleteSuccessModal() {
    const successModal = document.getElementById('deleteSuccessModal');
    successModal.style.display = 'flex';
    setTimeout(() => successModal.style.display = 'none', 2000);
}