let classrooms = [];
document.addEventListener('DOMContentLoaded', async () => {
    console.log('The document is loaded and initialization begins...');

    // 加载时间段配置
    let timeSlots = [
    "08:00-08:45",
    "08:55-09:40",
    "10:00-10:45",
    "10:55-11:40",
    "14:00-14:45",
    "14:55-15:40",
    "16:00-16:45",
    "16:55-17:40",
    "19:00-19:45",
    "19:55-20:40"
]


    // DOM元素引用
    const elements = {
        classroomList: document.getElementById('classroomList'),
        searchInput: document.getElementById('searchKeyword'),
        capacityFilter: document.getElementById('capacityFilter'),
        startSelect: document.getElementById('startTime'),
        endSelect: document.getElementById('endTime'),
        datePicker: document.getElementById('datePicker'), // 确保HTML中存在此ID
        equipmentFilter: document.getElementById('equipmentFilter'), // 确保HTML中存在此ID
        modal: document.getElementById('bookingModal'),
        closeModal: document.querySelector('.close'),
        availableTimesContainer: document.getElementById('availableTimes'),
        confirmBookingButton: document.getElementById('confirmBooking')
    };

    // 防抖函数
    const debounce = (func, timeout = 300) => {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => func.apply(this, args), timeout);
        };
    };

    // 初始化时间选择器
    function initTimeSelectors() {
        elements.startSelect.innerHTML = '<option value="">Select start time</option>';
        elements.endSelect.innerHTML = '<option value="">Select end time</option>';

        timeSlots.forEach(slot => {
            const [start, end] = slot.split('-');
            elements.startSelect.innerHTML += `<option value="${start}">${start}</option>`;
            elements.endSelect.innerHTML += `<option value="${end}">${end}</option>`;
        });
    }

    // 获取教室数据
    async function fetchClassrooms() {
        const requestData = {
            capacity: parseInt(elements.capacityFilter.value) || undefined,
            room_name: elements.searchInput.value.trim() || undefined,
            date: elements.datePicker?.value || undefined,
            start_time: elements.startSelect.value || undefined, // 直接使用HH:MM格式
            end_time: elements.endSelect.value || undefined,     // 直接使用HH:MM格式
            equipment: elements.equipmentFilter?.value || undefined
        };

        // 清除undefined值
        Object.keys(requestData).forEach(key => requestData[key] === undefined && delete requestData[key]);

        try {
            const response = await fetch('http://localhost:5000/search-rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const responseData = await response.json();
            console.log('Response data:', responseData);

            // 合并同一教室的多个时间段
            const classroomMap = new Map();
            responseData.results.forEach(room => {
                if (!classroomMap.has(room.room_id)) {
                    classroomMap.set(room.room_id, {
                        id: room.room_id,
                        name: room.room_name,
                        capacity: room.capacity,
                        equipment: room.equipment ? room.equipment.split(', ') : [],
                        availableTimes: []
                    });
                }
                const classroom = classroomMap.get(room.room_id);
                classroom.availableTimes.push({
                    time: `${room.available_begin}-${room.available_end}`,
                    booked: false // 根据实际业务逻辑判断是否被预订
                });
            });

            classrooms = Array.from(classroomMap.values());
            renderClassrooms();
        } catch (error) {
            console.error('Failed to fetch classrooms:', error);
            alert('Failed to load classrooms. Please try again.');
        }
    }

    // 渲染教室列表
    function renderClassrooms() {
        elements.classroomList.innerHTML = classrooms.map(classroom => `
            <div class="classroom-card" data-classroom="${classroom.name}">
                <h3>${classroom.name}</h3>
                <div class="details">
                    <p>Capacity: ${classroom.capacity} people</p>
                    <p>Equipment: ${classroom.equipment.join(', ')}</p>
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
                <button>
                    Book Now
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
    function showBookingModal(classroom) {
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

    // 初始化事件监听
    function initEventListeners() {
        const updateHandler = debounce(fetchClassrooms);
        ['input', 'change'].forEach(eventType => {
            elements.searchInput.addEventListener(eventType, updateHandler);
            elements.capacityFilter.addEventListener(eventType, updateHandler);
            elements.startSelect.addEventListener(eventType, updateHandler);
            elements.endSelect.addEventListener(eventType, updateHandler);
            elements.datePicker.addEventListener(eventType, updateHandler);
            elements.equipmentFilter.addEventListener(eventType, updateHandler);
        });

        elements.closeModal.onclick = () => elements.modal.style.display = 'none';
        window.onclick = event => event.target == elements.modal && (elements.modal.style.display = 'none');
    }

    // 初始化流程
    try {
        initTimeSelectors();
        initEventListeners();
        await fetchClassrooms();
        console.log('System initialization complete');
    } catch (error) {
        console.error('Initialization error:', error);
        alert('System initialization failed');
    }
});