document.addEventListener('DOMContentLoaded', function () {
    // Mock Data
    const rooms = [
        { id: 1, name: 'Conference Room A', type: 'Large' },
        { id: 2, name: 'Conference Room B', type: 'Medium' }
    ];

    const bookings = [
        {
            id: 1,
            roomId: 1,
            userId: 'user123',
            start: '2023-10-01T09:00:00',
            end: '2023-10-01T10:00:00',
            status: 'approved'
        },
        // Add more booking data
    ];

    const issues = [
        {
            id: 1,
            roomId: 1,
            description: 'Projector not working',
            startTime: '2023-10-01T09:00:00',
            endTime: '2023-10-01T10:00:00',
            status: 'fault'
        },
        // Add more issue data
    ];

    const blacklists = [
        {
            id: 1,
            userId: 'user123',
            userName: 'John Doe',
            startTime: '2023-10-01T09:00:00',
            endTime: '2023-10-08T09:00:00',
            reason: 'Repeated cancellations'
        },
        // Add more blacklist data
    ];

    const statusOptions = ['pending', 'approved', 'canceled', 'rejected', 'failed', 'changed'];
    const issueStatuses = ['fault', 'in_maintenance', 'resolved', 'severe'];

    // Global variables for date filtering
    let globalStartDate = null;
    let globalEndDate = null;

    // Initialize Filters
    const roomFilter = document.getElementById('roomFilter');
    const statusFilter = document.getElementById('statusFilter');
    const issueStatusFilter = document.getElementById('issueStatusFilter');
    const blacklistFilter = document.getElementById('blacklistFilter');

    // Initialize Flatpickr for date inputs
    flatpickr("#startDate", {});
    flatpickr("#endDate", {});

    // Populate Room Filter
    rooms.forEach(room => {
        const option = document.createElement('option');
        option.value = room.id;
        option.textContent = room.name;
        roomFilter.appendChild(option);
    });

    // Populate Status Filter
    statusOptions.forEach(status => {
        const option = document.createElement('option');
        option.value = status;
        option.textContent = status;
        statusFilter.appendChild(option);
    });

    // Populate Issue Status Filter
    issueStatuses.forEach(status => {
        const option = document.createElement('option');
        option.value = status;
        option.textContent = status;
        issueStatusFilter.appendChild(option);
    });

    // Event Listeners for Filters
    roomFilter.addEventListener('change', updateBookings);
    statusFilter.addEventListener('change', updateBookings);
    issueStatusFilter.addEventListener('change', updateIssues);
    blacklistFilter.addEventListener('change', updateBlacklist);

    // Initial Data Load
    updateTopRooms();
    updateBookings();
    updateIssues();
    updateBlacklist();
    updateMetrics();

    // Date range filtering function
    function filterByDateRange(item, startField = 'start', endField = 'end') {
        if (!globalStartDate && !globalEndDate) return true;

        const itemStart = new Date(item[startField]);
        const itemEnd = new Date(item[endField]);

        const startFilter = globalStartDate ? itemEnd >= new Date(globalStartDate) : true;
        const endFilter = globalEndDate ? itemStart <= new Date(globalEndDate) : true;

        return startFilter && endFilter;
    }

    // Generate Report function
    function generateReport() {
        globalStartDate = document.getElementById('startDate').value;
        globalEndDate = document.getElementById('endDate').value;

        updateTopRooms();
        updateBookings();
        updateIssues();
        updateBlacklist();
        updateMetrics();
    }

    // Update Top Rooms function
    function updateTopRooms() {
        const filteredBookings = bookings.filter(filterByDateRange);
        const roomMap = new Map();

        filteredBookings.forEach(booking => {
            const duration = calculateDuration(booking);
            if (roomMap.has(booking.roomId)) {
                roomMap.get(booking.roomId).totalHours += duration;
            } else {
                roomMap.set(booking.roomId, {
                    ...getRoomInfo(booking.roomId),
                    totalHours: duration
                });
            }
        });

        const topRooms = [...roomMap.values()]
            .sort((a, b) => b.totalHours - a.totalHours)
            .slice(0, 5);

        const tbody = document.querySelector('#topRoomsTable tbody');
        tbody.innerHTML = '';
        topRooms.forEach(room => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${room.id}</td>
                <td>${room.name}</td>
                <td>${room.type}</td>
                <td>${room.totalHours.toFixed(2)}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // Update Bookings function
    function updateBookings() {
        const selectedRoom = roomFilter.value;
        const selectedStatus = statusFilter.value;

        const filteredBookings = bookings.filter(booking => {
            const roomMatch = !selectedRoom || booking.roomId == selectedRoom;
            const statusMatch = !selectedStatus || booking.status === selectedStatus;
            const dateMatch = filterByDateRange(booking);
            return roomMatch && statusMatch && dateMatch;
        });

        const tbody = document.querySelector('#bookingTable tbody');
        tbody.innerHTML = '';
        filteredBookings.forEach(booking => {
            const room = getRoomInfo(booking.roomId);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${room.name}</td>
                <td>${booking.userId}</td>
                <td>${formatDateTime(booking.start)}</td>
                <td>${formatDateTime(booking.end)}</td>
                <td>${booking.status}</td>
            `;
            tbody.appendChild(row);
        });

        updateMetrics();
    }

    // Update Issues function
    function updateIssues() {
        const selectedStatus = issueStatusFilter.value;

        const filteredIssues = issues.filter(issue => {
            const statusMatch = !selectedStatus || issue.status === selectedStatus;
            const dateMatch = filterByDateRange(issue, 'startTime', 'endTime');
            return statusMatch && dateMatch;
        });

        const tbody = document.querySelector('#issueTable tbody');
        tbody.innerHTML = '';
        filteredIssues.forEach(issue => {
            const room = getRoomInfo(issue.roomId);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${room.name}</td>
                <td>${issue.description}</td>
                <td>${formatDateTime(issue.startTime)}</td>
                <td>${formatDateTime(issue.endTime)}</td>
                <td>${issue.status}</td>
            `;
            tbody.appendChild(row);
        });

        updateMetrics();
    }

    // Update Blacklist function
    function updateBlacklist() {
        const filterValue = blacklistFilter.value;
        const currentDate = new Date();

        const filteredBlacklist = blacklists.filter(record => {
            const dateMatch = filterByDateRange(record, 'startTime', 'endTime');
            if (filterValue === 'current') {
                return currentDate >= new Date(record.startTime) &&
                    currentDate <= new Date(record.endTime) &&
                    dateMatch;
            }
            return dateMatch;
        });

        const tbody = document.querySelector('#blacklistTable tbody');
        tbody.innerHTML = '';
        filteredBlacklist.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.userId}</td>
                <td>${record.userName}</td>
                <td>${formatDateTime(record.startTime)}</td>
                <td>${formatDateTime(record.endTime)}</td>
                <td>${record.reason}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // Update Metrics function
    function updateMetrics() {
        const filteredBookings = bookings.filter(filterByDateRange);
        const filteredIssues = issues.filter(filterByDateRange);

        document.getElementById('totalBookings').textContent = filteredBookings.length;
        document.getElementById('canceledCount').textContent = filteredBookings.filter(b => b.status === 'canceled').length;
        document.getElementById('totalIssues').textContent = filteredIssues.length;
    }

    // Utility Functions
    function getRoomInfo(roomId) {
        return rooms.find(room => room.id === roomId) || { id: roomId, name: 'Unknown', type: 'Unknown' };
    }

    function calculateDuration(booking) {
        return (new Date(booking.end) - new Date(booking.start)) / 3600000;
    }

    function formatDateTime(dateTime) {
        if (!dateTime) return '';
        const date = new Date(dateTime);
        return date.toLocaleString();
    }

    // Expose generateReport to global scope
    window.generateReport = generateReport;
});