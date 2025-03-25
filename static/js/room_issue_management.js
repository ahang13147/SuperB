// 初始化 Flatpickr（英文日历）
flatpickr("#startTime", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
    time_24hr: true,
    locale: "en",
});
flatpickr("#editStartTime", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
    time_24hr: true,
    locale: "en",
});

// 获取所有问题并显示
function fetchAndDisplayIssues() {
    // 获取搜索框和下拉框的值
    const roomId = document.getElementById('searchRoomId').value;
    const status = document.getElementById('filterStatus').value;

    // 构建请求 URL
    let url = 'https://www.diicsu.top:8000/display-issues';
    const params = [];
    if (roomId) {
        params.push(`room_id=${roomId}`);
    }
    if (status) {
        params.push(`status=${status}`);
    }
    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const issuesTableBody = document.getElementById('issuesTableBody');
            issuesTableBody.innerHTML = ''; // 清空现有内容
            data.issues.forEach(issue => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${issue.issue_id}</td>
                    <td>${issue.room_id}</td>
                    <td>${issue.room_name}</td>
                    <td>${issue.reporter_name}</td>
                    <td><div class="issue-content">${issue.issue}</div></td>
                    <td>${issue.start_date} ${issue.start_time}</td>
                    <td>
                        <select class="form-select status-select" onchange="updateStatus(this, ${issue.issue_id})">
                            <option value="fault" ${issue.status === 'fault' ? 'selected' : ''}>Fault</option>
                            <option value="in maintenance" ${issue.status === 'in_maintenance' ? 'selected' : ''}>In Maintenance</option>
                            <option value="resolved" ${issue.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                            <option value="severe" ${issue.status === 'severe' ? 'selected' : ''}>Severe</option>
                        </select>
                    </td>
                    <td id="endTime-${issue.issue_id}">${issue.end_date ? issue.end_date + ' ' + issue.end_time : ''}</td>
                    <td>
                        <button class="btn-edit" onclick="openEditModal(${issue.issue_id}, '${issue.room_id}', '${issue.issue}', '${issue.start_date} ${issue.start_time}')">Edit</button>
                    </td>
                `;
                issuesTableBody.appendChild(row);

                // 点击展开/收起问题内容
                row.querySelector('.issue-content').addEventListener('click', function () {
                    this.classList.toggle('expanded');
                });
            });
        })
        .catch(error => console.error('Error fetching issues:', error));
}

// 为搜索框和下拉框添加事件监听器
document.getElementById('searchRoomId').addEventListener('input', fetchAndDisplayIssues);
document.getElementById('filterStatus').addEventListener('change', fetchAndDisplayIssues);

// 页面加载时获取并显示问题
document.addEventListener('DOMContentLoaded', fetchAndDisplayIssues);


document.getElementById('issueForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const roomId = document.getElementById('roomId').value;
    const issue = document.getElementById('issue').value;
    const startTime = document.getElementById('startTime').value;
    const [startDate, startTimeValue] = startTime.split(' ');

    fetch('https://www.diicsu.top:8000/insert-issues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_id: roomId, issue: issue, start_date: startDate, start_time: startTimeValue }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Issue created successfully') {
                showAlert('Issue added successfully!', 'success');


                //todo: add send email to all users
            fetch('http://localhost:8000/send_email/broadcast_issue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ issue_id: data.issue_id })
            })
            .then(resp => resp.json())
            .then(broadcastData => {
                console.log('Broadcast email sent:', broadcastData);
            })
            .catch(error => {
                console.error('Error broadcasting email:', error);
            });

                fetchAndDisplayIssues(); // 刷新列表
                document.getElementById('issueForm').reset(); // 清空表单
            } else {
                showAlert(data.error || 'Failed to add issue', 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error.message, 'error'));
});

// 打开编辑模态框
// 修改后的 openEditModal 函数
// 修改后的 openEditModal 函数
function openEditModal(issueId, roomId, issue, startTime) {
    document.getElementById('editIssue').value = issue; // 正确赋值问题描述
    document.getElementById('editIssueId').value = issueId;
    const editModal = new bootstrap.Modal(document.getElementById('editModal'));
    editModal.show();
}
// 保存编辑
// 修改后的 saveEdit 函数
function saveEdit() {
    const issueId = document.getElementById('editIssueId').value;
    const issue = document.getElementById('editIssue').value; // 仅获取问题描述

    fetch(`https://www.diicsu.top:8000/update-issues/${issueId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue: issue }), // 仅发送 issue 字段
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Issue updated successfully') {
                showAlert('Issue edited successfully!', 'success');
                fetchAndDisplayIssues(); // 强制刷新
                bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            } else {
                showAlert('Failed to edit: ' + data.error, 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error.message, 'error'));
}

// 更新问题状态
function updateStatus(selectElement, issueId) {
    // 将状态值中的空格转为下划线（兼容数据库格式）
    const status = selectElement.value.replace(/ /g, '_');

    fetch(`https://www.diicsu.top:8000/update-issues/${issueId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: status }), // 发送转换后的值
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Issue updated successfully') {
                fetchAndDisplayIssues(); // 强制刷新
            } else {
                showAlert('Failed to update status: ' + data.error, 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error.message, 'error'));
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 3000);
}

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
