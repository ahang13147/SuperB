document.addEventListener('DOMContentLoaded', function() {
    // 获取弹窗元素
    const modal = document.getElementById('bookingModal');
    const closeModal = document.querySelector('.close');
    const availableTimesContainer = document.getElementById('availableTimes');
    const confirmBookingButton = document.getElementById('confirmBooking');

    // 关闭弹窗
    closeModal.onclick = function() {
        modal.style.display = 'none';
    }

    // 点击窗口外部关闭弹窗
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // 处理立即预约按钮点击事件
    document.querySelectorAll('.classroom-card button').forEach(button => {
        button.addEventListener('click', function() {
            const classroomCard = this.closest('.classroom-card');
            const availableTimes = classroomCard.querySelectorAll('.details ul li');

            // 清空之前的时间段
            availableTimesContainer.innerHTML = '';

            // 填充可用时间段
            availableTimes.forEach(time => {
                const timeSlot = document.createElement('div');
                timeSlot.textContent = time.textContent;
                availableTimesContainer.appendChild(timeSlot);
            });

            // 显示弹窗
            modal.style.display = 'block';
        });
    });

    // 确认预约按钮点击事件
    confirmBookingButton.addEventListener('click', function() {
        alert('预约已确认！');
        modal.style.display = 'none';
    });
});document.addEventListener('DOMContentLoaded', async () => {
    console.log('文档加载完成，开始初始化...');

    // 加载时间段配置
    let timeSlots;
    try {
        console.log('正在加载 time_slots.json...');
        const response = await fetch('time_slots.json');
        if (!response.ok) throw new Error(`HTTP错误! 状态码: ${response.status}`);
        timeSlots = await response.json();
        console.log('成功加载时间段配置:', timeSlots);
    } catch (error) {
        console.error('加载时间段配置失败:', error);
        alert('无法加载时间段配置，请检查控制台日志');
        return;
    }

    // 模拟教室数据（增加更多测试数据）
    const classrooms = [
        {
            name: "101教室",
            capacity: 50,
            availableTimes: ["08:00-08:45", "10:00-10:45"],
            isBooked: false
        },
        {
            name: "201阶梯教室",
            capacity: 150,
            availableTimes: ["14:00-14:45", "16:00-16:45"],
            isBooked: true
        },
        {
            name: "301多媒体室",
            capacity: 80,
            availableTimes: ["19:00-19:45", "19:55-20:40"],
            isBooked: false
        },
        {
            name: "A栋实验室",
            capacity: 40,
            availableTimes: ["08:55-09:40", "10:55-11:40"],
            isBooked: false
        }
    ];
    console.log('初始化教室数据:', classrooms);

    // DOM元素引用
    const elements = {
        classroomList: document.getElementById('classroomList'),
        searchInput: document.getElementById('searchKeyword'),
        capacityFilter: document.getElementById('capacityFilter'),
        startSelect: document.getElementById('startTime'),
        endSelect: document.getElementById('endTime')
    };
    console.log('DOM元素引用:', elements);

    // 初始化时间选择器
    function initTimeSelectors() {
        console.log('初始化时间选择器...');
        elements.startSelect.innerHTML = '<option value="">选择开始时间</option>';
        elements.endSelect.innerHTML = '<option value="">选择结束时间</option>';

        timeSlots.forEach(slot => {
            const [start, end] = slot.split('-');
            elements.startSelect.innerHTML += `<option value="${slot}">${start}</option>`;
            elements.endSelect.innerHTML += `<option value="${slot}">${end}</option>`;
        });
        console.log('时间选择器初始化完成');
    }

    // 筛选逻辑
    function filterClassrooms() {
        const searchTerm = elements.searchInput.value.toLowerCase();
        const minCapacity = parseInt(elements.capacityFilter.value) || 0;
        const selectedStart = elements.startSelect.value;
        const selectedEnd = elements.endSelect.value;

        console.log('当前筛选条件:', {
            searchTerm,
            minCapacity,
            selectedStart,
            selectedEnd
        });

        return classrooms.filter(classroom => {
            // 名称匹配
            const nameMatch = classroom.name.toLowerCase().includes(searchTerm);

            // 容量匹配
            const capacityMatch = classroom.capacity >= minCapacity;

            // 时间匹配
            let timeMatch = true;
            if (selectedStart && selectedEnd) {
                const expectedSlot = `${selectedStart.split('-')[0]}-${selectedEnd.split('-')[1]}`;
                timeMatch = classroom.availableTimes.includes(expectedSlot);
            }

            console.log(`教室 ${classroom.name} 匹配结果:`, {
                nameMatch,
                capacityMatch,
                timeMatch
            });

            return nameMatch && capacityMatch && timeMatch;
        });
    }

    // 渲染教室列表
    function renderClassrooms() {
        console.log('开始渲染教室列表...');
        const filtered = filterClassrooms();
        console.log('筛选结果:', filtered);

        elements.classroomList.innerHTML = filtered.map(classroom => `
            <div class="classroom-card">
                <h3>${classroom.name}</h3>
                <div class="details">
                    <p>容纳人数：${classroom.capacity}人</p>
                    <p>可预约时段：</p>
                    <ul>
                        ${classroom.availableTimes.map(t => `<li>${t}</li>`).join('')}
                    </ul>
                </div>
                <span class="status ${classroom.isBooked ? 'booked' : 'available'}">
                    ${classroom.isBooked ? '已预约' : '可预约'}
                </span>
                <button ${classroom.isBooked ? 'disabled' : ''}>
                    ${classroom.isBooked ? '已满' : '立即预约'}
                </button>
            </div>
        `).join('');

        console.log('渲染完成，显示 ${filtered.length} 个教室');
    }

    // 初始化事件监听
    function initEventListeners() {
        console.log('初始化事件监听...');
        const updateEvents = ['input', 'change'];
        updateEvents.forEach(eventType => {
            elements.searchInput.addEventListener(eventType, renderClassrooms);
            elements.capacityFilter.addEventListener(eventType, renderClassrooms);
            elements.startSelect.addEventListener(eventType, renderClassrooms);
            elements.endSelect.addEventListener(eventType, renderClassrooms);
        });
        console.log('事件监听初始化完成');
    }

    // 执行初始化流程
    try {
        initTimeSelectors();
        initEventListeners();
        renderClassrooms();
        console.log('系统初始化完成');
    } catch (error) {
        console.error('初始化过程中发生错误:', error);
        alert('系统初始化失败，请检查控制台日志');
    }
});