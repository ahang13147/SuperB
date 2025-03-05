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

    // 模拟教室数据（增加更多测试数据）
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
        { time: "14:00-14:45", booked: true },  // 已预定
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
                timeMatch = classroom.availableTimes.includes(expectedSlot);
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
        elements.classroomList.innerHTML = classrooms.map(classroom => `
            <div class="classroom-card">
                <h3>${classroom.name}</h3>
                <div class="details">
                    <p>容纳人数：${classroom.capacity}人</p>
                    <p>可预约时段：</p>
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
                    ${classroom.isBooked ? 'Be already full' : 'Can be booked'}
                </span>
                <button ${classroom.isBooked ? 'disabled' : ''}>
                    ${classroom.isBooked ? 'Be already full' : 'Book now'}
                </button>
            </div>
        `).join('');

        // 添加事件监听器
         document.querySelectorAll('.classroom-card button').forEach(button => {
        button.addEventListener('click', function() {
            const classroomCard = this.closest('.classroom-card');
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
                        ${timeSlot.booked ? '<small>(Be booked)</small>' : ''}
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
        });
    });



        console.log('Render complete，display ${filtered.length} classroom');
    }


    function updateClassroomStatus(classroomName, bookedTime) {
        const classroom = classrooms.find(c => c.name === classroomName);
        const timeSlot = classroom.availableTimes.find(t => t.time === bookedTime);

        if (timeSlot) {
            timeSlot.booked = true;
            // 检查是否所有时间段都已预定
            classroom.isBooked = classroom.availableTimes.every(t => t.booked);
        }
        renderClassrooms();
    }

    // 修改后的确认预约逻辑
    elements.confirmBookingButton.addEventListener('click', function() {
        const selectedTimeSlot = document.querySelector('input[name="timeSlot"]:checked');
        if (selectedTimeSlot) {
            const classroomName = document.querySelector('.classroom-card button:not(:disabled)')
                .closest('.classroom-card')
                .querySelector('h3').textContent;

            updateClassroomStatus(classroomName, selectedTimeSlot.value);
            alert(`Reservation confirmed! Time period：${selectedTimeSlot.value}`);
            elements.modal.style.display = 'none';
        } else {
            alert('Please select a time period');
        }
    });




    // 初始化事件监听
    function initEventListeners() {
        console.log('Initialize event listening...');
        const updateEvents = ['input', 'change'];
        updateEvents.forEach(eventType => {
            elements.searchInput.addEventListener(eventType, renderClassrooms);
            elements.capacityFilter.addEventListener(eventType, renderClassrooms);
            elements.startSelect.addEventListener(eventType, renderClassrooms);
            elements.endSelect.addEventListener(eventType, renderClassrooms);
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

        // 确认预约按钮点击事件
        elements.confirmBookingButton.addEventListener('click', function() {
            const selectedTimeSlot = document.querySelector('input[name="timeSlot"]:checked');
            if (selectedTimeSlot) {
                alert(`Reservation confirmed! Time period：${selectedTimeSlot.value}`);
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