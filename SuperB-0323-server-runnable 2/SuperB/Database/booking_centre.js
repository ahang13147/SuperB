let classrooms = [];
document.addEventListener('DOMContentLoaded', async () => {
    console.log('The document is loaded and initialization begins...');

    // 加载时间段配置
    let timeSlots;
    try {
        const response = await fetch('time_slots.json');
        if (!response.ok) throw new Error(`HTTP error! Status code: ${response.status}`);
        timeSlots = await response.json();
    } catch (error) {
        console.error('Failed to load time slots:', error);
        alert('Unable to load time slots configuration');
        return;
    }

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
            const [start] = slot.split('-');
            elements.startSelect.innerHTML += `<option value="${slot}">${start}</option>`;
            elements.endSelect.innerHTML += `<option value="${slot}">${slot.split('-')[1]}</option>`;
        });
    }

    // 获取教室数据
    async function fetchClassrooms() {
        const requestData = {
            capacity: parseInt(elements.capacityFilter.value) || undefined,
            room_name: elements.searchInput.value.trim() || undefined,
            start_time: elements.startSelect.value ? elements.startSelect.value.split('-')[0] : undefined,
            end_time: elements.endSelect.value ? elements.endSelect.value.split('-')[1] : undefined
        };

        // 清除undefined值
        Object.keys(requestData).forEach(key => requestData[key] === undefined && delete requestData[key]);

        try {
            const response = await fetch('https://101.200.197.132:5000/search-rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            classrooms = await response.json();
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
            button.addEventListener('click', function () {
                const classroomName = this.closest('.classroom-card').dataset.classroom;
                const classroom = classrooms.find(c => c.name === classroomName);
                showBookingModal(classroom);
            });
        });
    }

    // 显示预定弹窗
    function showBookingModal(classroom) {
        document.querySelectorAll('.classroom-card').forEach(card => {
            card.dataset.active = "false";
        });
        document.querySelector(`.classroom-card[data-classroom="${classroom.name}"]`).dataset.active = "true";

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
        });

        elements.closeModal.onclick = () => elements.modal.style.display = 'none';
        window.onclick = event => event.target == elements.modal && (elements.modal.style.display = 'none');
    }

    // 初始化流程
    try {
        initTimeSelectors();
        initEventListeners();
        await fetchClassrooms(); // 初始加载所有教室
        console.log('System initialization complete');
    } catch (error) {
        console.error('Initialization error:', error);
        alert('System initialization failed');
    }
});