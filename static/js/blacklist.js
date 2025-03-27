// flatpickr initialise
const startDatePicker = flatpickr("#startDate", {
    dateFormat: "Y-m-d",
    onChange: function (selectedDates) {
        endDatePicker.set('minDate', selectedDates[0] || new Date());
        validateTimes();
    }
});

const startTimePicker = flatpickr("#startTime", {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: true,
    onChange: function () {
        validateTimes();
    }
});

const endDatePicker = flatpickr("#endDate", {
    dateFormat: "Y-m-d",
    onChange: function () {
        validateTimes();
    }
});

const endTimePicker = flatpickr("#endTime", {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: true,
    onChange: function () {
        validateTimes();
    }
});

// Time verification logic
function validateTimes() {
    const startDate = document.getElementById('startDate').value;
    const startTime = document.getElementById('startTime').value;
    const endDate = document.getElementById('endDate').value;
    const endTime = document.getElementById('endTime').value;
    const errorElement = document.getElementById('timeError');

    if (startDate && startTime && endDate && endTime) {
        const startDateTime = new Date(`${startDate}T${startTime}`);
        const endDateTime = new Date(`${endDate}T${endTime}`);

        if (endDateTime <= startDateTime) {
            errorElement.style.display = 'block';
            document.getElementById('endDate').classList.add('input-error');
            document.getElementById('endTime').classList.add('input-error');
            return false;
        }
    }

    errorElement.style.display = 'none';
    document.getElementById('endDate').classList.remove('input-error');
    document.getElementById('endTime').classList.remove('input-error');
    return true;
}

// Add blacklist
async function addToBlacklist() {
    if (!validateTimes()) {
        alert('The decapsulating time must be later than the masking time！');
        return;
    }

    const userId = document.getElementById('userId').value;
    const startDate = document.getElementById('startDate').value;
    const startTime = document.getElementById('startTime').value;
    const endDate = document.getElementById('endDate').value;
    const endTime = document.getElementById('endTime').value;
    const reason = document.getElementById('reason').value;

    if (userId && startDate && startTime && endDate && endTime && reason) {
        const requestBody = {
            user_id: parseInt(userId, 10),
            added_by: 1, // Assume that the current user ID is 1
            start_date: startDate,
            start_time: startTime,
            end_date: endDate,
            end_time: endTime,
            reason: reason
        };

        try {
            const response = await fetch('http://localhost:8000/insert-blacklist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });

            if (response.ok) {
                alert('successfully added！');
                loadBlacklist();
            }
            else {
                const errorData = await response.json();
                alert(`fail to add：${errorData.error}`);
            }
        } catch (error) {
            console.error('Request failed：', error);
            alert('Network error, please try again later');
        }

        // Clear input field
        document.getElementById('userId').value = '';
        document.getElementById('startDate').value = '';
        document.getElementById('startTime').value = '';
        document.getElementById('endDate').value = '';
        document.getElementById('endTime').value = '';
        document.getElementById('reason').value = '';
    } else {
        alert('Please fill in all required fields (User ID, start date, start time, end date, end time, reason)');
    }
}

// Remove blacklist
async function removeFromBlacklist(button, blacklistId) {
    if (confirm('Are you sure to unban the user？')) {
        try {
            const response = await fetch('http://localhost:8000/delete_blacklist', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ blacklist_id: blacklistId })
            });

            const responseData = await response.json();

            if (response.ok) {
                const row = button.closest('tr');
                if (row) row.remove();
                showNotification('Delete successfully！', 'success');
            } else {
                showNotification(`Failed to delete：${responseData.error}`, 'error');
            }
        } catch (error) {
            console.error('Failed to request：', error);
            showNotification('Network error', 'error');
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const colors = {
        success: '#2ecc71',
        error: '#e74c3c',
        info: '#3498db'
    };

    const notification = document.createElement('div');
    notification.style = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${colors[type]};
        color: white;
        border-radius: 8px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.16);
        z-index: 1000;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// load blacklist data
async function loadBlacklist() {
    try {
        const response = await fetch('http://localhost:8000/get-blacklist');
        if (response.ok) {
            const result = await response.json();
            renderBlacklist(result.blacklists);
        }
    } catch (error) {
        console.error('Request failed：', error);
    }
}

// 搜索功能
function searchBlacklist() {
    const searchTerm = document.getElementById('searchBlacklistInput').value.toLowerCase();
    const rows = document.querySelectorAll('#blacklistTable tbody tr');

    rows.forEach(row => {
        const userId = row.cells[1].textContent.toLowerCase();
        const userName = row.cells[0].textContent.toLowerCase();

        if (userId.includes(searchTerm) || userName.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Render form
function renderBlacklist(data) {
    const tableBody = document.querySelector('#blacklistTable tbody');
    tableBody.innerHTML = '';

    data.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td data-label="Username">${user.username}</td>
            <td data-label="User ID">${user.user_id}</td>
            <td class="time-cell" data-label="Start Time">${user.start_date} ${user.start_time}</td>
            <td class="time-cell" data-label="End Time">${user.end_date} ${user.end_time}</td>
            <td data-label="Reason" title="${user.reason}">${user.reason}</td>
            <td data-label="Actions">
                <div class="action-buttons">
                    <button class="btn btn-danger" onclick="removeFromBlacklist(this, '${user.blacklist_id}')">
                        <i class="fas fa-user-check"></i>
                        Unban
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadBlacklist();
});

// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    hamburger.addEventListener('click', function () {
        sidebar.classList.toggle('active');
    });

    document.addEventListener('click', function (e) {
        if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
});