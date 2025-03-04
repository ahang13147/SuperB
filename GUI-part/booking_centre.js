// booking_centre.js
// booking_centre.js
document.addEventListener('DOMContentLoaded', async () => {
    // DOM元素
    const classroomList = document.getElementById('classroomList');
    const searchInput = document.getElementById('searchKeyword');
    const capacityFilter = document.getElementById('capacityFilter');
    const startTime = document.getElementById('startTime');
    const endTime = document.getElementById('endTime');

    // 事件监听
    [searchInput, capacityFilter, startTime, endTime].forEach(element => {
        element.addEventListener('input', updateDisplay);
        element.addEventListener('change', updateDisplay);
    });

    // 初始显示
    updateDisplay();
    const classrooms = [
        {
            name: "101教室",
            capacity: 50,
            availableTimes: ["09:00-10:00", "14:00-15:00"],
            isBooked: false
        },
        {
            name: "201阶梯教室",
            capacity: 150,
            availableTimes: ["10:30-12:00", "15:00-17:00"],
            isBooked: true
        },
        {
            name: "301多媒体室",
            capacity: 80,
            availableTimes: ["08:00-09:30", "13:00-14:30"],
            isBooked: false
        }
    ];
    // 加载时间段配置
    const timeSlots = await fetch('time_slots.js').then(res => res.json());

    // 初始化时间选择器
    const startSelect = document.getElementById('startTime');
    const endSelect = document.getElementById('endTime');

    // 填充时间段选项
    timeSlots.forEach(slot => {
        startSelect.innerHTML += `<option value="${slot}">${slot.split('-')[0]}</option>`;
        endSelect.innerHTML += `<option value="${slot}">${slot.split('-')[1]}</option>`;
    });

    // 修改过滤逻辑
    function updateDisplay() {
        const filtered = classrooms.filter(classroom => {
            // ...保留之前的过滤条件...

            // 修改时间过滤逻辑
            let timeMatch = true;
            const selectedStart = startSelect.value;
            const selectedEnd = endSelect.value;

            if (selectedStart && selectedEnd) {
                // 检查是否存在包含选定时间段的可用时段
                timeMatch = classroom.availableTimes.some(classTime => {
                    return classTime === `${selectedStart.split('-')[0]}-${selectedEnd.split('-')[1]}`;
                });
            }

            return nameMatch && capacityMatch && timeMatch;
        });

        renderClassrooms(filtered);
    }

    // 确保所有筛选器都绑定事件
    [searchInput, capacityFilter, startSelect, endSelect].forEach(element => {
        element.addEventListener('change', updateDisplay);
    });
    function renderClassrooms(classrooms) {
        classroomList.innerHTML = classrooms.map(classroom => `
            <div class="classroom-card">
                <h3>${classroom.name}</h3>
                <div class="details">
                    <p>容纳人数：${classroom.capacity}人</p>
                    <p>可预约时间：${classroom.availableTimes.join(', ')}</p>
                </div>
                <span class="status ${classroom.isBooked ? 'booked' : 'available'}">
                    ${classroom.isBooked ? '已预约' : '可预约'}
                </span>
                <button ${classroom.isBooked ? 'disabled' : ''}>
                    ${classroom.isBooked ? '已满' : '立即预约'}
                </button>
            </div>
        `).join('');
    }
});
