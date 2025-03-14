        // Initializes the time selector
        const startDatePicker = flatpickr("#startDate", {
            dateFormat: "Y-m-d",
            onChange: function(selectedDates) {

                endDatePicker.set('minDate', selectedDates[0] || new Date());
                validateTimes();
            }
        });

        const startTimePicker = flatpickr("#startTime", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,

            onChange: function() {
                validateTimes();
            }
        });

        const endDatePicker = flatpickr("#endDate", {
            dateFormat: "Y-m-d",

            onChange: function() {

                validateTimes();
            }
        });

        const endTimePicker = flatpickr("#endTime", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,

            onChange: function() {

                validateTimes();
            }
        });

        // proof time
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
                    const response = await fetch('http://127.0.0.1:8000/insert-blacklist', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestBody),
                    });

                    if (response.ok) {
                        alert('successfully added！');
                        loadBlacklist();
                    } else {
                        const errorData = await response.json();
                        alert(`fail to add：${errorData.message}`);
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
            if (confirm('Are you sure you want to unblock this user？')) {
                try {
                    const response = await fetch(`/api/remove-from-blacklist/${blacklistId}`, {
                        method: 'DELETE',
                    });

                    if (response.ok) {
                        alert('Successfully unsealed！');
                        loadBlacklist();
                    } else {
                        const errorData = await response.json();
                        alert(`Unseal failure：${errorData.message}`);
                    }
                } catch (error) {
                    console.error('Request failed：', error);
                    alert('Network error, please try again later.');
                }
            }
        }


        // Load blacklist data
        async function loadBlacklist() {
            try {
                const response = await fetch('http://127.0.0.1:8000/get-blacklist');
                if (response.ok) {
                    const result = await response.json();
                    renderBlacklist(result.blacklists);
                }
            } catch (error) {
                console.error('Request failed：', error);
            }
        }

        // Render blacklist table
        function renderBlacklist(data) {
            const tableBody = document.querySelector('#blacklistTable tbody');
            tableBody.innerHTML = '';

            data.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.user_id}</td>
                    <td class="time-cell">${user.start_date} ${user.start_time}</td>
                    <td class="time-cell">${user.end_date} ${user.end_time}</td>
                    <td title="${user.reason}">${user.reason}</td>
                    <td>
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


        // The data is initialized when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            loadBlacklist();
        });