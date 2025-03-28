document.addEventListener('DOMContentLoaded', function() {
  // Process menu group click
  document.querySelectorAll('.group-header').forEach(header => {
    header.addEventListener('click', function() {
      const group = this.closest('.menu-group');
      group.classList.toggle('active');

    // Close other expanded menu groups
      document.querySelectorAll('.menu-group').forEach(otherGroup => {
        if (otherGroup !== group) {
          otherGroup.classList.remove('active');
        }
      });
    });
  });

    // Mobile burger menu switch
  const hamburger = document.querySelector('.hamburger-menu');
  const sidebar = document.querySelector('.sidebar');

  hamburger.addEventListener('click', function(e) {
    e.stopPropagation(); 
    sidebar.classList.toggle('active');
  });

    // Click external to close the sidebar
  document.addEventListener('click', function(e) {
    if (sidebar.classList.contains('active') &&
        !e.target.closest('.sidebar') &&
        !e.target.closest('.hamburger-menu')) {
      sidebar.classList.remove('active');
    }
  });

    // Prevents clicking inside the sidebar from triggering closure
  sidebar.addEventListener('click', function(e) {
    e.stopPropagation();
  });    
    
    loadRooms();
});



let currentEditingRoomId = null;
let activeRooms = [];
let deletedRooms = [];

// load room data
async function loadRooms() {
    try {
        const response = await fetch('https://www.diicsu.top:8000/rooms');
        const data = await response.json();
         activeRooms = data.rooms.filter(room => room.room_status !== 2); //Filter out the deleted rooms 
        deletedRooms = data.rooms.filter(room => room.room_status === 2); //Filter out the deleted rooms 
        renderTables();
    } catch (error) {
        console.error('Failed to load:', error);
        alert('Unable to load room data, please check network connection');
    }
}
// Convert room_type numbers to text
function getRoomTypeText(roomType) {
    switch (roomType) {
        case 0: return "Available for all";
        case 1: return "Staff only";
        case 2: return "Trusted user only";
        default: return "Unknown";
    }
}

// Render tables and cards
function renderTables() {
    const activeTbody = document.querySelector('#activeTable tbody');
    const deletedTbody = document.querySelector('#deletedTable tbody');
    const cardsContainer = document.querySelector('.room-cards-container');

    // Desktop table rendering
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

// open edit model
function openEditModal(roomId) {
    const room = activeRooms.find(r => r.room_id == roomId);
    if (!room) return;

    currentEditingRoomId = roomId;
    document.getElementById('editRoomId').value = roomId;
    document.getElementById('editRoomName').value = room.room_name;
    document.getElementById('editCapacity').value = room.capacity;
    document.getElementById('editLocation').value = room.location;
    document.getElementById('editEquipment').value = room.equipment;
    document.getElementById('editRoomType').value = room.room_type; // set room type

    document.getElementById('editModal').style.display = 'flex';
}

// close edit model 
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// save edited information
async function saveRoom() {
    const updatedData = {
        room_name: document.getElementById('editRoomName').value,
        capacity: parseInt(document.getElementById('editCapacity').value),
        location: document.getElementById('editLocation').value,
        equipment: document.getElementById('editEquipment').value,
        type: parseInt(document.getElementById('editRoomType').value) // get room type
    };

    try {
        const response = await fetch(`https://www.diicsu.top:8000/update-room/${currentEditingRoomId}`, {
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

// soft delete
async function softDeleteRoom(roomId) {
    if (confirm(`Are you sure to delete ${roomId} 吗？`)) {
        try {
            const response = await fetch('https://www.diicsu.top:8000/update_room_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: roomId,
                    action: 'delete' 
                })
            });

            const result = await response.json();

            if (response.ok) {
                // Remove the room from activeRooms
                const index = activeRooms.findIndex(r => r.room_id == roomId);
                
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

// Switch TAB
function showTab(tabId) {
    // Desktop table switching
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.room-table').forEach(t => t.style.display = 'none');
    document.querySelector(`#${tabId}Table`).style.display = 'table';
    document.querySelector(`[onclick="showTab('${tabId}')"]`).classList.add('active');

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

// Open the Add Room mode box
function openAddRoomModal() {
    document.getElementById('addRoomModal').style.display = 'flex';
}
// Close the Add Room mode box
function closeAddRoomModal() {
    document.getElementById('addRoomModal').style.display = 'none';
}
// Add a new room
async function addRoom() {
    
    const newRoom = {
        room_name: document.getElementById('roomName').value,
        capacity: parseInt(document.getElementById('capacity').value),
        location: document.getElementById('location').value,
        equipment: document.getElementById('equipment').value,
        room_type: parseInt(document.getElementById('roomType').value)
    };

    try {
        const response = await fetch('https://www.diicsu.top:8000/insert_room', {
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
            loadRooms();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
// A message indicating that the addition succeeds is displayed
function showAddSuccessModal() {
    const successModal = document.getElementById('addSuccessModal');
    successModal.style.display = 'flex';
    setTimeout(() => successModal.style.display = 'none', 2000);
}

// display delete successfully
function showDeleteSuccessModal() {
    const successModal = document.getElementById('deleteSuccessModal');
    successModal.style.display = 'flex';
    setTimeout(() => successModal.style.display = 'none', 2000);
}

// open restore model 
function openRestoreRoomModal() {
    document.getElementById('restoreRoomModal').style.display = 'flex';
}

// cloes restore model
function closeRestoreRoomModal() {
    document.getElementById('restoreRoomModal').style.display = 'none';
}

// confirm restore room 
async function confirmRestoreRoom() {
    const roomId = document.getElementById('restoreRoomId').value;

    if (!roomId) {
        alert('Please enter a valid Room ID.');
        return;
    }

    try {
        const response = await fetch('https://www.diicsu.top:8000/update_room_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_id: roomId,
                action: 'restore' 
            })
        });

        const result = await response.json();

        if (response.ok) {
            const index = deletedRooms.findIndex(r => r.room_id == roomId);
            if (index > -1) {
                const restoredRoom = deletedRooms.splice(index, 1)[0];
                activeRooms.push(restoredRoom);
                renderTables();
                closeRestoreRoomModal();
                alert('Room restored successfully.');
            } else {
                alert('Room not found in deleted list.');
            }
        } else {
            alert(`Failed to restore room: ${result.error}`);
        }
    } catch (error) {
        console.error('Request error:', error);
        alert('Network request failed');
    }
}

// search room
function searchRooms() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    const filteredActive = activeRooms.filter(room => 
        room.room_id.toString().includes(searchTerm) ||
        room.room_name.toLowerCase().includes(searchTerm)
    );
    
    const filteredDeleted = deletedRooms.filter(room =>
        room.room_id.toString().includes(searchTerm) ||
        room.room_name.toLowerCase().includes(searchTerm)
    );

    // update display
    updateTableDisplay('#activeTable tbody', filteredActive, true);
    updateTableDisplay('#deletedTable tbody', filteredDeleted, false);
    updateCardDisplay(filteredActive);
}

// update table display
function updateTableDisplay(selector, data, showActions) {
    const tbody = document.querySelector(selector);
    tbody.innerHTML = data.map(room => `
        <tr class="${showActions ? 'room-item' : 'deleted-item'}" data-room-id="${room.room_id}">
            <td>${room.room_id}</td>
            <td>${room.room_name}</td>
            <td>${room.capacity}</td>
            <td>${room.location}</td>
            <td>${room.equipment}</td>
            <td>${getRoomTypeText(room.room_type)}</td>
            ${showActions ? `
            <td class="room-actions">
                <button class="edit-btn" onclick="openEditModal(${room.room_id})">Edit</button>
                <button class="delete-btn" onclick="softDeleteRoom(${room.room_id})">Delete</button>
            </td>
            ` : `<td>${new Date().toLocaleString()}</td>`}
        </tr>
    `).join('');
}

// update card display
function updateCardDisplay(data) {
    const cardsContainer = document.querySelector('.room-cards-container');
    if (window.innerWidth <= 768) {
        cardsContainer.innerHTML = data.map(room => `
            <div class="room-card" data-room-id="${room.room_id}">
                <!-- 保持原有卡片结构 -->
                ${document.querySelector('.tab-btn.active').id === 'active' ? `
                <div class="card-actions">
                    <button class="edit-btn" onclick="openEditModal(${room.room_id})">Edit</button>
                    <button class="delete-btn" onclick="softDeleteRoom(${room.room_id})">Delete</button>
                </div>
                ` : ''}
            </div>
        `).join('');
    }
}