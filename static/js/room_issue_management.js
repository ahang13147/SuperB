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

// Get all questions and display them
function fetchAndDisplayIssues() {
    // Get the search box and drop-down box values
    const roomId = document.getElementById('searchRoomId').value;
    const status = document.getElementById('filterStatus').value;

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
            issuesTableBody.innerHTML = ''; 
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

                row.querySelector('.issue-content').addEventListener('click', function () {
                    this.classList.toggle('expanded');
                });
            });
        })
        .catch(error => console.error('Error fetching issues:', error));
}
// Add event listeners to the search box and drop-down box
document.getElementById('searchRoomId').addEventListener('input', fetchAndDisplayIssues);
document.getElementById('filterStatus').addEventListener('change', fetchAndDisplayIssues);
// Gets and displays the problem when the page loads
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
            fetch('https://www.diicsu.top:8000/send_email/broadcast_issue', {
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

                fetchAndDisplayIssues(); // refresh
                document.getElementById('issueForm').reset(); // delete list
            } else {
                showAlert(data.error || 'Failed to add issue', 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error.message, 'error'));
});
// Open the Edit mode box
function openEditModal(issueId, roomId, issue, startTime) {
    document.getElementById('editIssue').value = issue; 
    document.getElementById('editIssueId').value = issueId;
    const editModal = new bootstrap.Modal(document.getElementById('editModal'));
    editModal.show();
}
// save edit
function saveEdit() {
    const issueId = document.getElementById('editIssueId').value;
    const issue = document.getElementById('editIssue').value; // Get only the problem description

    fetch(`https://www.diicsu.top:8000/update-issues/${issueId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue: issue }), // Send only the issue field
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Issue updated successfully') {
                showAlert('Issue edited successfully!', 'success');
                fetchAndDisplayIssues(); 
                bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            } else {
                showAlert('Failed to edit: ' + data.error, 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error.message, 'error'));
}

// Update the problem status
function updateStatus(selectElement, issueId) {
    const status = selectElement.value.replace(/ /g, '_');

    fetch(`https://www.diicsu.top:8000/update-issues/${issueId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: status }), 
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Issue updated successfully') {
                fetchAndDisplayIssues(); 
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

  // Click outside to close the sidebar
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
});