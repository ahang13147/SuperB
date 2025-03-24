// 初始化加载房间数据
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

    loadRooms();
});

let currentEditingRoomId = null;

// 加载房间数据
async function loadRooms() {
    try {
        const response = await fetch('https://101.200.197.132:8000/rooms');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        const roomListContainer = document.querySelector('.room-list-container');
        roomListContainer.innerHTML = data.rooms.map(room => `
            <div class="room-item" data-room-id="${room.room_id}">
                <div class="room-info">
                    <div><label>Room ID:</label> ${room.room_id}</div>
                    <div><label>Name:</label> ${room.room_name}</div>
                    <div><label>Capacity:</label> ${room.capacity}</div>
                    <div><label>Location:</label> ${room.location}</div>
                    <div><label>Equipment:</label> ${room.equipment}</div>
                </div>
                <div class="room-actions">
                    <button class="edit-btn" onclick="openEditModal(${room.room_id})">Edit</button>
                    <button class="delete-btn" onclick="deleteRoom(${room.room_id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载房间数据失败:', error);
        alert('无法加载房间数据，请检查网络连接');
    }
}



// 打开编辑模态框
function openEditModal(roomId) {
    const roomItem = document.querySelector(`[data-room-id="${roomId}"]`);
    const info = roomItem.querySelector('.room-info');

    currentEditingRoomId = roomId;
    document.getElementById('editRoomId').value = roomId;
    document.getElementById('editRoomName').value = info.children[1].textContent.split(':')[1].trim();
    document.getElementById('editCapacity').value = info.children[2].textContent.split(':')[1].trim();
    document.getElementById('editLocation').value = info.children[3].textContent.split(':')[1].trim();
    document.getElementById('editEquipment').value = info.children[4].textContent.split(':')[1].trim();

    document.getElementById('editModal').style.display = 'flex';
}

// 关闭编辑模态框
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// 保存房间修改
async function saveRoom() {
    const updatedData = {
        room_name: document.getElementById('editRoomName').value,
        capacity: parseInt(document.getElementById('editCapacity').value),
        equipment: document.getElementById('editEquipment').value,
        location: document.getElementById('editLocation').value
    };

    try {
        const response = await fetch(`https://101.200.197.132:8000/update-room/${currentEditingRoomId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(updatedData)
        });

        const result = await response.json();
        if (response.ok) {
            alert('更新成功！');
            loadRooms();
            closeEditModal();
        } else {
            alert(`更新失败：${result.message}`);
        }
    } catch (error) {
        console.error('请求错误:', error);
        alert('网络请求失败，请检查控制台');
    }
}

// 删除房间
async function deleteRoom(roomId) {
    if (confirm(`确认要删除房间 ${roomId} 吗？`)) {
        try {
            const response = await fetch('https://101.200.197.132:8000/delete/rooms', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ room_id: roomId })
            });

            const result = await response.json();
            if (response.ok) {
                document.querySelector(`[data-room-id="${roomId}"]`).remove();
                showDeleteSuccessModal();
            } else {
                alert(`删除失败：${result.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('删除操作失败，请检查网络连接');
        }
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
        capacity: document.getElementById('capacity').value,
        location: document.getElementById('location').value,
        equipment: document.getElementById('equipment').value
    };

    try {
        const response = await fetch('https://101.200.197.132:8000/insert_room', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(newRoom)
        });

        if (response.ok) {
            document.getElementById('roomName').value = '';
            document.getElementById('capacity').value = '';
            document.getElementById('location').value = '';
            document.getElementById('equipment').value = '';
            loadRooms();
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