// usage_report_center.js

// ==================== 全局函数声明 ====================
let updateBookings, updateIssues, updateBlacklist;
let globalStartDate, globalEndDate;
let currentBookings = [];
let currentIssues = [];
let currentBlacklist = [];

// ==================== 工具函数 ====================
const getDefaultDates = () => {
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);
    return {
        start: thirtyDaysAgo.toISOString().split('T')[0],
        end: today.toISOString().split('T')[0]
    };
};

const formatDateTime = (dateTime) => {
    try {
        return new Date(dateTime).toLocaleString();
    } catch {
        return 'Invalid Date';
    }
};

const filterByDateRange = (item) => {
    if (!globalStartDate && !globalEndDate) return true;

    try {
        const itemStart = new Date(item.start);
        const itemEnd = new Date(item.end);
        const filterStart = new Date(globalStartDate);
        const filterEnd = new Date(globalEndDate);

        // 判断时间段是否有交集
        return (
            (itemStart <= filterEnd && itemEnd >= filterStart) ||
            (itemStart >= filterStart && itemStart <= filterEnd)
        );
    } catch (error) {
        console.error('日期过滤错误:', error);
        return false;
    }
};

// ==================== 数据获取函数 ====================
const fetchTopBookedRooms = async () => {
    try {
        const response = await fetch('https://www.diicsu.top:8000/top-booked-rooms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_date: globalStartDate,
                end_date: globalEndDate
            })
        });
        const data = await response.json();
        return data.results || [];
    } catch (error) {
        console.error('获取热门房间数据失败:', error);
        return [];
    }
};
const fetchBookings = async () => {
    try {
        const response = await fetch('https://www.diicsu.top:8000/bookings');
        const data = await response.json();
        return data.bookings || [];
    } catch (error) {
        console.error('获取预订数据失败:', error);
        return [];
    }
};

const fetchIssues = async () => {
    try {
        const params = new URLSearchParams({
            status: document.getElementById('issueStatusFilter').value,
            room_id: ''
        });
        const response = await fetch(`https://www.diicsu.top:8000/display-issues?${params}`);
        const data = await response.json();
        return data.issues || [];
    } catch (error) {
        console.error('获取问题数据失败:', error);
        return [];
    }
};

const fetchBlacklist = async () => {
    try {
        const response = await fetch('https://www.diicsu.top:8000/get-blacklist');
        const data = await response.json();
        return data.blacklists || [];
    } catch (error) {
        console.error('获取黑名单失败:', error);
        return [];
    }
};

// ==================== 数据更新函数 ====================
updateBookings = async () => {
    try {
        const bookings = await fetchBookings();
        const selectedStatus = document.getElementById('statusFilter').value;

        const filteredBookings = bookings.filter(booking => {
            const statusMatch = !selectedStatus || booking.status === selectedStatus;
            const dateMatch = filterByDateRange({
                start: `${booking.booking_date}T${booking.start_time}`,
                end: `${booking.booking_date}T${booking.end_time}`
            });
            return statusMatch && dateMatch;
        });

        renderBookings(filteredBookings);
        currentBookings = filteredBookings;
        updateMetrics();
    } catch (error) {
        console.error('更新预订数据失败:', error);
    }
};

updateIssues = async () => {
    try {
        const issues = await fetchIssues();
        const selectedStatus = document.getElementById('issueStatusFilter').value;

        const filteredIssues = issues.filter(issue => {
            const statusMatch = !selectedStatus || issue.status === selectedStatus;
            const dateMatch = filterByDateRange({
                start: `${issue.start_date}T${issue.start_time}`,
                end: `${issue.end_date}T${issue.end_time}`
            });
            return statusMatch && dateMatch;
        });

        renderIssues(filteredIssues);
        currentIssues = filteredIssues;
        updateMetrics();
    } catch (error) {
        console.error('更新问题数据失败:', error);
    }
};

updateBlacklist = async () => {
    try {
        const blacklists = await fetchBlacklist();
        const filterValue = document.getElementById('blacklistFilter').value;
        const currentDate = new Date();

        const filteredBlacklist = blacklists.filter(record => {
            const dateMatch = filterByDateRange({
                start: `${record.start_date}T${record.start_time}`,
                end: `${record.end_date}T${record.end_time}`
            });

            let statusMatch = true;
            if (filterValue === 'current') {
                statusMatch = currentDate >= new Date(`${record.start_date}T${record.start_time}`) &&
                    currentDate <= new Date(`${record.end_date}T${record.end_time}`);
            }

            return dateMatch && statusMatch;
        });

        renderBlacklist(filteredBlacklist);
        currentBlacklist = filteredBlacklist;
    } catch (error) {
        console.error('更新黑名单失败:', error);
    }
};

const handleExport = async () => {
  const format = document.getElementById('exportFormat').value;
  
  // 获取所有选中的复选框
  const tables = [
    document.getElementById('exportBooking'),
    document.getElementById('exportIssue'),
    document.getElementById('exportBlacklist')
  ].filter(checkbox => checkbox.checked)
   .map(checkbox => checkbox.value);

  if (tables.length === 0) {
    alert('Please select at least one table to export!');
    return;
  }
  
    if (format === 'PDF') {
        await exportToPDF(tables);
    } else {
        await exportToExcel(tables);
    }
    $('#exportModal').modal('hide');
};

// ==================== 渲染函数 ====================
const renderTopBookedRooms = (rooms) => {
    const container = document.querySelector('.room-list');
    container.innerHTML = ''; // 清空静态示例数据

    // 添加room_type映射关系
    const roomTypeMap = {
        0: 'Normal Room',
        1: 'Staff Only Room',
        2: 'Trusted User Only Room'
    };

    // 根据使用时长设置透明度梯度
    const maxHours = rooms.length > 0 ? rooms[0].total_hours : 1;

    rooms.forEach((room, index) => {
        const opacity = 0.5 - (index * 0.1); // 前5名透明度递减
        const item = document.createElement('div');
        item.className = 'room-item';
        item.style.backgroundColor = `rgba(106, 161, 255, ${opacity})`;
        item.innerHTML = `
            <div class="room-info">
                <div class="room-header">
                    <span class="room-name">${room.room_name}</span>
                    <span class="room-hours">${room.total_hours}h</span>
                </div>
                <span class="room-type">
                    ${roomTypeMap[room.room_type] || 'N/A'}
                </span>
            </div>
        `;
        container.appendChild(item);
    });
};
const renderBookings = (bookings) => {
    const tbody = document.querySelector('#bookingTable tbody');
    tbody.innerHTML = '';
    bookings.forEach(booking => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${booking.booking_id}</td>
            <td>${booking.room_name}</td>
            <td>${booking.room_id}</td>
            <td>${booking.username}</td>
            <td>${booking.user_id}</td>
            <td>${formatDateTime(booking.booking_date + 'T' + booking.start_time)}</td>
            <td>${formatDateTime(booking.booking_date + 'T' + booking.end_time)}</td>
            <td>${booking.status}</td>
            <td>${booking.reason || ''}</td>
        `;
        tbody.appendChild(row);
    });
};

const renderIssues = (issues) => {
    const tbody = document.querySelector('#issueTable tbody');
    tbody.innerHTML = '';
    issues.forEach(issue => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${issue.issue_id}</td>
            <td>${issue.room_id}</td>
            <td>${issue.room_name}</td>
            <td>${issue.issue}</td>
            <td>${formatDateTime(issue.start_date + 'T' + issue.start_time)}</td>
            <td>${formatDateTime(issue.end_date + 'T' + issue.end_time)}</td>
            <td>${issue.status}</td>
        `;
        tbody.appendChild(row);
    });
};

const renderBlacklist = (records) => {
    const tbody = document.querySelector('#blacklistTable tbody');
    tbody.innerHTML = '';
    records.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.blacklist_id}</td>
            <td>${record.user_id}</td>
            <td>${record.username}</td>
            <td>${formatDateTime(record.start_date + 'T' + record.start_time)}</td>
            <td>${formatDateTime(record.end_date + 'T' + record.end_time)}</td>
            <td>${record.reason}</td>
        `;
        tbody.appendChild(row);
    });
};

// ==================== 指标更新 ====================
const updateMetrics = () => {
    try {
        const bookingCount = document.querySelectorAll('#bookingTable tbody tr').length;
        const canceledCount = Array.from(document.querySelectorAll('#bookingTable tbody tr'))
            .filter(tr => tr.cells[7].textContent === 'canceled').length;
        const issueCount = document.querySelectorAll('#issueTable tbody tr').length;

        document.getElementById('totalBookings').textContent = bookingCount;
        document.getElementById('canceledCount').textContent = canceledCount;
        document.getElementById('totalIssues').textContent = issueCount;
    } catch (error) {
        console.error('更新统计指标失败:', error);
    }
};

// ==================== 主逻辑 ====================
document.addEventListener('DOMContentLoaded', () => {
    // 初始化日期范围
    const defaultDates = getDefaultDates();
    globalStartDate = defaultDates.start;
    globalEndDate = defaultDates.end;

    // 设置输入框默认值
    document.getElementById('startDate').value = globalStartDate;
    document.getElementById('endDate').value = globalEndDate;

    // 初始化Flatpickr
    flatpickr("#startDate", {});
    flatpickr("#endDate", {});

    // 事件监听
    document.getElementById('startDate').addEventListener('change', async () => {
        globalStartDate = document.getElementById('startDate').value;
        await Promise.all([updateBookings(), updateIssues(), updateBlacklist()]);
    });

    document.getElementById('endDate').addEventListener('change', async () => {
        globalEndDate = document.getElementById('endDate').value;
        await Promise.all([updateBookings(), updateIssues(), updateBlacklist()]);
    });
    document.getElementById('statusFilter').addEventListener('change', () => updateBookings());
    document.getElementById('issueStatusFilter').addEventListener('change', () => updateIssues());
    document.getElementById('blacklistFilter').addEventListener('change', () => updateBlacklist());

    // 初始加载数据
    updateBookings();
    updateIssues();
    updateBlacklist();
    // 初始加载Top 5数据
    (async () => {
        const topRooms = await fetchTopBookedRooms();
        renderTopBookedRooms(topRooms);
    })();
});

// ==================== 报告生成 ====================
const generateReport = async () => {
    try {
        // 强制更新所有数据
        globalStartDate = document.getElementById('startDate').value || getDefaultDates().start;
        globalEndDate = document.getElementById('endDate').value || getDefaultDates().end;

        await Promise.all([
            updateBookings(),
            updateIssues(),
            updateBlacklist(),
            (async () => {
                const topRooms = await fetchTopBookedRooms();
                renderTopBookedRooms(topRooms);
            })()
        ]);

        // 确保数据更新后显示弹窗
        new bootstrap.Modal(document.getElementById('exportModal')).show();

    } catch (error) {
        console.error('An error occurred while generating the report:', error);
        alert('Report generation failed. Check console log');
    }
};

const exportToPDF = async (tables) => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    tables.forEach((tableType, index) => {
        if (index > 0) doc.addPage();

        let data = [];
        let columns = [];

        switch (tableType) {
            case 'booking':
                data = currentBookings.map(b => [
                    b.booking_id,
                    b.room_name,
                    b.room_id,
                    b.username,
                    b.user_id,
                    formatDateTime(b.booking_date + 'T' + b.start_time),
                    formatDateTime(b.booking_date + 'T' + b.end_time),
                    b.status,
                    b.reason || ''
                ]);
                columns = ['ID', 'Room', 'Room ID', 'User', 'User ID', 'Start', 'End', 'Status', 'Reason'];
                break;
            case 'issue':
                data = currentIssues.map(i => [
                    i.issue_id,
                    i.room_id,
                    i.room_name,
                    i.issue,
                    formatDateTime(i.start_date + 'T' + i.start_time),
                    formatDateTime(i.end_date + 'T' + i.end_time),
                    i.status
                ]);
                columns = ['ID', 'Room ID', 'Room', 'Issue', 'Start', 'End', 'Status'];
                break;
            case 'blacklist':
                data = currentBlacklist.map(b => [
                    b.blacklist_id,
                    b.user_id,
                    b.username,
                    formatDateTime(b.start_date + 'T' + b.start_time),
                    formatDateTime(b.end_date + 'T' + b.end_time),
                    b.reason
                ]);
                columns = ['ID', 'User ID', 'User', 'Start', 'End', 'Reason'];
                break;
        }

        doc.autoTable({
            head: [columns],
            body: data,
            startY: index === 0 ? 20 : 15,
            theme: 'grid',
            styles: { fontSize: 8 }
        });
    });

    doc.save(`report_${new Date().toISOString().slice(0, 10)}.pdf`);
};

const exportToExcel = (tables) => {
    const wb = XLSX.utils.book_new();

    tables.forEach(tableType => {
        let data = [];
        let headers = [];

        switch (tableType) {
            case 'booking':
                headers = ['Booking ID', 'Room Name', 'Room ID', 'Username', 'User ID', 'Start Time', 'End Time', 'Status', 'Reason'];
                data = currentBookings.map(b => ({
                    'Booking ID': b.booking_id,
                    'Room Name': b.room_name,
                    'Room ID': b.room_id,
                    'Username': b.username,
                    'User ID': b.user_id,
                    'Start Time': formatDateTime(b.booking_date + 'T' + b.start_time),
                    'End Time': formatDateTime(b.booking_date + 'T' + b.end_time),
                    'Status': b.status,
                    'Reason': b.reason || ''
                }));
                break;
            case 'issue':
                headers = ['Issue ID', 'Room ID', 'Room Name', 'Issue', 'Start Time', 'End Time', 'Status'];
                data = currentIssues.map(i => ({
                    'Issue ID': i.issue_id,
                    'Room ID': i.room_id,
                    'Room Name': i.room_name,
                    'Issue': i.issue,
                    'Start Time': formatDateTime(i.start_date + 'T' + i.start_time),
                    'End Time': formatDateTime(i.end_date + 'T' + i.end_time),
                    'Status': i.status
                }));
                break;
            case 'blacklist':
                headers = ['Blacklist ID', 'User ID', 'Username', 'Start Time', 'End Time', 'Reason'];
                data = currentBlacklist.map(b => ({
                    'Blacklist ID': b.blacklist_id,
                    'User ID': b.user_id,
                    'Username': b.username,
                    'Start Time': formatDateTime(b.start_date + 'T' + b.start_time),
                    'End Time': formatDateTime(b.end_date + 'T' + b.end_time),
                    'Reason': b.reason
                }));
                break;
        }

        const ws = XLSX.utils.json_to_sheet(data);
        XLSX.utils.book_append_sheet(wb, ws, tableType);
    });

    XLSX.writeFile(wb, `report_${new Date().toISOString().slice(0, 10)}.xlsx`);
};


document.addEventListener('DOMContentLoaded', function() {
  // 处理菜单分组点击
  document.querySelectorAll('.group-header').forEach(header => {
    header.addEventListener('click', function() {
      const group = this.closest('.menu-group');
      group.classList.toggle('active');

      // 关闭其他展开的菜单组
      document.querySelectorAll('.menu-group').forEach(otherGroup => {
        if (otherGroup !== group) {
          otherGroup.classList.remove('active');
        }
      });
    });
  });

  // 移动端汉堡菜单切换
  const hamburger = document.querySelector('.hamburger-menu');
  const sidebar = document.querySelector('.sidebar');

  hamburger.addEventListener('click', function(e) {
    e.stopPropagation(); // 防止点击汉堡菜单触发下面的 document 点击事件
    sidebar.classList.toggle('active');
  });

  // 点击外部关闭侧边栏
  document.addEventListener('click', function(e) {
    if (sidebar.classList.contains('active') &&
        !e.target.closest('.sidebar') &&
        !e.target.closest('.hamburger-menu')) {
      sidebar.classList.remove('active');
    }
  });

  // 防止侧边栏内部点击触发关闭
  sidebar.addEventListener('click', function(e) {
    e.stopPropagation();
  });
});