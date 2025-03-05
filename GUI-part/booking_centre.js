document.addEventListener('DOMContentLoaded', async () => {
    console.log('The document is loaded and initialization begins...');

    // 加载时间段配置
    let timeSlots;
    try {
        console.log('loading time_slots.json...');
        const response = await fetch('time_slots.json');
        if (!response.ok) throw new Error(`HTTP error! Status code: ${response.status}`);
        timeSlots = await response.json();
        console.log('The time range configuration was successfully loaded. Procedure:', timeSlots);
    } catch (error) {
        console.error('Failed to configure the loading time range:', error);
        alert('Unable to load the time period configuration, check the console log');
        return;
    }

    // 模拟教室数据
    const classrooms = [
        {
            name: "101 classroom",
            capacity: 50,
            availableTimes: [
                { time: "08:00-08:45", booked: false },
                { time: "10:00-10:45", booked: true }
            ],
            isBooked: false
        },
        {
            name: "201 Lecture theatre",
            capacity: 150,
            availableTimes: [
                { time: "14:00-14:45", booked: true },
                { time: "16:00-16:45", booked: false }
            ],
            isBooked: false
        },
        {
            name: "301 Multimedia Room",
            capacity: 80,
            availableTimes: [
                { time: "19:00-19:45", booked: false },
                { time: "19:55-20:40", booked: false }
            ],
            isBooked: false
        },
        {
            name: "Building A laboratory",
            capacity: 40,
            availableTimes: [
                { time: "08:55-09:40", booked: false },
                { time: "10:55-11:40", booked: false }
            ],
            isBooked: false
        }
    ];
    console.log('Initialize the classroom data:', classrooms);

    // DOM元素引用
    const elements = {
        classroomList: document.getElementById('classroomList'),
        searchInput: document.getElementById('searchKeyword'),
        capacityFilter: document.getElementById('capacityFilter'),
        startSelect: document.getElementById('startTime'),
        endSelect: document.getElementById('endTime'),
        modal: document.getElementById('bookingModal'),
        closeModal: document.querySelector('.close'),
        availableTimesContainer: document.getElementById('availableTimes'),
        confirmBookingButton: document.getElementById('confirmBooking')
    };
    console.log('DOM element reference:', elements);

    // 防抖函数
    function debounce(func, timeout = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => { func.apply(this, args); }, timeout);
        };
    }

    // 初始化时间选择器
    function initTimeSelectors() {
        console.log('Initializes the time selector...');
        elements.startSelect.innerHTML = '<option value="">Select start time</option>';
        elements.endSelect.innerHTML = '<option value="">Select end time</option>';

        timeSlots.forEach(slot => {
            const [start, end] = slot.split('-');
            elements.startSelect.innerHTML += `<option value="${slot}">${start}</option>`;
            elements.endSelect.innerHTML += `<option value="${slot}">${end}</option>`;
        });
        console.log('Time selector initialization is complete');
    }

    // 筛选逻辑
    function filterClassrooms() {
        const searchTerm = elements.searchInput.value.toLowerCase();
        const minCapacity = parseInt(elements.capacityFilter.value) || 0;
        const selectedStart = elements.startSelect.value;
        const selectedEnd = elements.endSelect.value;

        console.log('Current filter:', {
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
                timeMatch = classroom.availableTimes.some(t => t.time === expectedSlot);
            }

            console.log(`classroom ${classroom.name} Matching result:`, {
                nameMatch,
                capacityMatch,
                timeMatch
            });

            return nameMatch && capacityMatch && timeMatch;
        });
    }

    // 渲染教室列表
function renderClassrooms() {
    const filtered = filterClassrooms();
    elements.classroomList.innerHTML = filtered.map(classroom => `
        <div class="classroom-card" data-classroom="${classroom.name}">
            <h3>${classroom.name}</h3>
            <div class="details">
                <p>Capacity: ${classroom.capacity} people</p>
                <p>Available time slots:</p>
                <ul>
                    ${classroom.availableTimes.map(t => `
                        <li class="${t.booked ? 'booked-slot' : ''}">
                            ${t.time} 
                            ${t.booked ? '<span class="booked-marker">⛔️</span>' : ''}
                        </li>
                    `).join('')}
                </ul>
            </div>
            <span class="status ${classroom.isBooked ? 'booked' : 'available'}">
                ${classroom.isBooked ? 'Booked' : 'Available'}
            </span>
            <button ${classroom.isBooked ? 'disabled' : ''}>
                ${classroom.isBooked ? 'Booked' : 'Book Now'}
            </button>
        </div>
    `).join('');

    // 绑定事件监听器
    document.querySelectorAll('.classroom-card button').forEach(button => {
        button.addEventListener('click', function() {
            const classroomName = this.closest('.classroom-card').dataset.classroom;
            const classroom = classrooms.find(c => c.name === classroomName);
            showBookingModal(classroom);
        });
    });
}

// 显示预定弹窗
// 修改显示弹窗逻辑
function showBookingModal(classroom) {
    // 标记当前激活的教室卡片
    document.querySelectorAll('.classroom-card').forEach(card => {
        card.dataset.active = "false";
    });
    document.querySelector(`.classroom-card[data-classroom="${classroom.name}"]`).dataset.active = "true";

    // 渲染时间段时添加调试信息
    console.log('Rendering time slots for:', {
        classroom: classroom.name,
        availableTimes: classroom.availableTimes.map(t => t.time)
    });

    elements.availableTimesContainer.innerHTML = classroom.availableTimes.map(timeSlot => `
        <div class="${timeSlot.booked ? 'time-slot-booked' : ''}">
            <input 
                type="radio" 
                name="timeSlot" 
                id="slot_${timeSlot.time}" 
                value="${timeSlot.time}"
                ${timeSlot.booked ? 'disabled' : ''}
            >
            <label for="slot_${timeSlot.time}">
                ${timeSlot.booked ? '⛔️ ' : '🕒 '}
                ${timeSlot.time}
                ${timeSlot.booked ? '<small>(Booked)</small>' : ''}
            </label>
        </div>
    `).join('');

    elements.modal.style.display = 'block';
}

    // 处理预定按钮点击
    function handleBookingButtonClick(button) {
        const classroomCard = button.closest('.classroom-card');
        const classroom = classrooms.find(c => c.name === classroomCard.querySelector('h3').textContent);

        elements.availableTimesContainer.innerHTML = '';

        classroom.availableTimes.forEach(timeSlot => {
            const div = document.createElement('div');
            div.className = timeSlot.booked ? 'time-slot-booked' : '';
            div.innerHTML = `
                <input 
                    type="radio" 
                    name="timeSlot" 
                    id="slot_${timeSlot.time}" 
                    value="${timeSlot.time}"
                    ${timeSlot.booked ? 'disabled' : ''}
                >
                <label for="slot_${timeSlot.time}">
                    ${timeSlot.booked ? '⛔️ ' : '🕒 '}
                    ${timeSlot.time}
                    ${timeSlot.booked ? '<small>(Booked)</small>' : ''}
                </label>
            `;

            if (!timeSlot.booked) {
                div.addEventListener('click', function() {
                    document.querySelectorAll('#availableTimes div').forEach(d =>
                        d.classList.remove('checked'));
                    this.classList.add('checked');
                });
            }

            elements.availableTimesContainer.appendChild(div);
        });

        elements.modal.style.display = 'block';
    }

    // 修改后的 updateClassroomStatus 函数
function normalizeTime(timeString) {
    return timeString
        .replace(/\s+/g, '') // 移除所有空格
        .replace(/[：]/g, ':') // 替换中文冒号为英文冒号
        .trim(); // 移除前后空格
}

// 加强版的updateClassroomStatus
function updateClassroomStatus(classroomName, bookedTime) {
    const normalizedBookedTime = normalizeTime(bookedTime);

    // 精确匹配教室
    const classroom = classrooms.find(c =>
        normalizeTime(c.name) === normalizeTime(classroomName)
    );

    if (!classroom) {
        console.error('Classroom not found:', {
            input: classroomName,
            classrooms: classrooms.map(c => c.name)
        });
        return;
    }

    // 精确匹配时间段
    const timeSlot = classroom.availableTimes.find(t =>
        normalizeTime(t.time) === normalizedBookedTime
    );

    if (timeSlot) {
        console.log('Updating status:', {
            classroom: classroom.name,
            timeSlot: timeSlot.time,
            before: timeSlot.booked,
            after: true
        });
        timeSlot.booked = true;
        classroom.isBooked = classroom.availableTimes.every(t => t.booked);
        renderClassrooms();
    } else {
        console.error('Time slot mismatch:', {
            classroom: classroom.name,
            inputTime: bookedTime,
            normalizedInput: normalizedBookedTime,
            availableTimes: classroom.availableTimes.map(t => ({
                original: t.time,
                normalized: normalizeTime(t.time)
            }))
        });
    }
}
elements.confirmBookingButton.addEventListener('click', function() {
    const selectedTimeSlot = document.querySelector('input[name="timeSlot"]:checked');

    if (selectedTimeSlot) {
        // 直接从当前打开的弹窗获取教室信息
        const activeClassroom = document.querySelector('.classroom-card[data-active="true"]');
        if (!activeClassroom) {
            alert('No available classroom selected');
            return;
        }

        const classroomName = activeClassroom.dataset.classroom;
        const selectedTime = selectedTimeSlot.value;

        console.log('Confirming booking:', {
            classroomName,
            selectedTime,
            classroomData: classrooms.find(c => c.name === classroomName)
        });

        updateClassroomStatus(classroomName, selectedTime);
        elements.modal.style.display = 'none';
    } else {
        alert('Please select a time period');
    }
});

    // 初始化事件监听
    function initEventListeners() {
        console.log('Initialize event listening...');

        // 使用防抖优化输入事件
        const updateHandler = debounce(renderClassrooms);
        ['input', 'change'].forEach(eventType => {
            elements.searchInput.addEventListener(eventType, updateHandler);
            elements.capacityFilter.addEventListener(eventType, updateHandler);
            elements.startSelect.addEventListener(eventType, updateHandler);
            elements.endSelect.addEventListener(eventType, updateHandler);
        });

        // 使用事件委托处理预定按钮点击
        elements.classroomList.addEventListener('click', function(e) {
            if (e.target.tagName === 'BUTTON' && !e.target.disabled) {
                handleBookingButtonClick(e.target);
            }
        });

        // 关闭弹窗
        elements.closeModal.onclick = function() {
            elements.modal.style.display = 'none';
        }

        // 点击窗口外部关闭弹窗
        window.onclick = function(event) {
            if (event.target == elements.modal) {
                elements.modal.style.display = 'none';
            }
        }

        // 确认预定按钮
        elements.confirmBookingButton.addEventListener('click', function() {
            const selectedTimeSlot = document.querySelector('input[name="timeSlot"]:checked');
            if (selectedTimeSlot) {
                const classroomName = document.querySelector('.classroom-card button:not(:disabled)')
                    .closest('.classroom-card')
                    .querySelector('h3').textContent;

                updateClassroomStatus(classroomName, selectedTimeSlot.value);
                alert(`Reservation confirmed! Time period: ${selectedTimeSlot.value}`);
                elements.modal.style.display = 'none';
            } else {
                alert('Please select a time period');
            }
        });

        console.log('The event listening initialization is complete');
    }

    // 执行初始化流程
    try {
        initTimeSelectors();
        initEventListeners();
        renderClassrooms();
        console.log('System initialization is complete');
    } catch (error) {
        console.error('An error occurred during initialization:', error);
        alert('System initialization failed. Please check console logs');
    }
});