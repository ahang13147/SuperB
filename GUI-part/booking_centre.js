let pendingBookingData = null; // 用于暂存需要补充reason的预定数据
let classrooms = [];
let currentClassroom = null; // 添加在文件顶部，与classrooms变量并列
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
    ];

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
        console.log(elements.datePicker.value);  // 应该直接输出"2025-03-05"
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
            const response = await fetch('http://localhost:8000/search-rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const responseData = await response.json();
            console.log('Response data:', responseData);

            // 合并同一教室的多个时间段
            const classroomMap = new Map();
            // 修改这部分代码
            responseData.results.forEach(room => {
                if (!classroomMap.has(room.room_id)) {
                    classroomMap.set(room.room_id, {
                        id: room.room_id,       // 新增room_id存储
                        name: room.room_name,
                        type: room.room_type,   // 新增room_type存储
                        capacity: room.capacity,
                        equipment: room.equipment ? room.equipment.split(', ') : [],
                        availableTimes: []
                    });
                }
                const classroom = classroomMap.get(room.room_id);
                classroom.availableTimes.push({
                    time: `${room.available_begin}-${room.available_end}`,
                    // 修改这里：根据availability判断是否被预定
                    booked: room.availability === 2 // 当availability等于2时设为true
                });
            });

            classrooms = Array.from(classroomMap.values());
            renderClassrooms();
        } catch (error) {
            console.error('Failed to fetch classrooms:', error);
            alert('Failed to load classrooms. Please try again.');
        }
    }

    // 渲染教室列表（修正版）
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
        </div> <!-- 修复闭合标签 -->
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
        currentClassroom = classroom;
        elements.availableTimesContainer.innerHTML = classroom.availableTimes.map(timeSlot => `
        <div class="time-slot ${timeSlot.booked ? 'time-slot-booked' : ''}">
            <input 
                type="radio" 
                name="timeSlot" 
                id="slot_${timeSlot.time.replace(/:/g, '')}" 
                value="${timeSlot.time}"
                ${timeSlot.booked ? 'disabled' : ''}
            >
            <label for="slot_${timeSlot.time.replace(/:/g, '')}">
                ${timeSlot.booked ? '⛔️ ' : '🕒 '}
                ${timeSlot.time}
                ${timeSlot.booked ? '<small>(Booked)</small>' : ''}
            </label>
        </div>
    `).join('');

        // 新增：添加时间段选中样式交互
        elements.availableTimesContainer.querySelectorAll('.time-slot').forEach(slot => {
            const radio = slot.querySelector('input[type="radio"]');
            radio.addEventListener('change', () => {
                // 移除所有槽的选中状态
                document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('checked'));
                // 添加当前选中槽的样式
                if (radio.checked) slot.classList.add('checked');
            });
        });

        elements.modal.style.display = 'block';
    }

    // 初始化事件监听
     function initEventListeners() {
        ['input', 'change'].forEach(eventType => {
            elements.searchInput.addEventListener(eventType, fetchClassrooms);
            elements.capacityFilter.addEventListener(eventType, fetchClassrooms);
            elements.startSelect.addEventListener(eventType, fetchClassrooms);
            elements.endSelect.addEventListener(eventType, fetchClassrooms);
            elements.datePicker.addEventListener(eventType, fetchClassrooms);
            elements.equipmentFilter.addEventListener(eventType, fetchClassrooms);
            elements.confirmBookingButton.addEventListener('click', handleBookingConfirmation);
        });

        // 关闭 Modal 的事件监听
        elements.closeModal.onclick = () => elements.modal.style.display = 'none';

        // 防止点击日期选择器时关闭 modal
        elements.datePicker.addEventListener('click', (event) => {
            event.stopPropagation();  // 阻止点击事件传播到 window

        // 新增原因弹窗关闭事件
        document.querySelector('.close-reason').onclick = () => {
            document.getElementById('reasonModal').style.display = 'none';
        };

            // 新增原因提交事件
        document.getElementById('submitReason').addEventListener('click', handleReasonSubmit);


        
        });

        // 关闭 Modal 的事件监听：只有点击 modal 背景才关闭
        window.onclick = event => {
            if (event.target == elements.modal) {
                elements.modal.style.display = 'none';
            }
        };
    }
    
    // 修改后的handleBookingConfirmation函数：
    async function handleBookingConfirmation() {
        const selectedTime = document.querySelector('input[name="timeSlot"]:checked');
        if (!selectedTime) {
            alert('Please select a time slot.');
            return;
        }

        const timeRange = selectedTime.value.split('-');
        const startTime = timeRange[0].trim();
        const endTime = timeRange[1].trim();

        const bookingDate = elements.datePicker.value;
        if (!bookingDate) {
            alert('Please select a date.');
            return;
        }

        // 获取用户ID（根据实际登录状态获取）
        const userId = 2;

        try {
            const response = await fetch('http://localhost:8000/insert_booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: currentClassroom.id, // 改为使用room_id
                    user_id: userId,
                    booking_date: bookingDate,
                    start_time: startTime,
                    end_time: endTime,
                    reason: ' ' // 默认传空格
                })
            });

            const data = await response.json();
            if (!response.ok) {
                if (data.status === 'require_reason') {
                    // 存储预定数据并显示原因输入框
                    pendingBookingData = {
                        room_id: currentClassroom.id,
                        user_id: userId,
                        booking_date: bookingDate,
                        start_time: startTime,
                        end_time: endTime
                    };
                    elements.modal.style.display = 'none';
                    document.getElementById('reasonModal').style.display = 'block';
                    return;
                }
                throw new Error(data.error || 'Booking failed');
            }

            alert('Booking successful!');
            elements.modal.style.display = 'none';
            await fetchClassrooms();
        } catch (error) {
            console.error('Booking Error:', error);
            alert(`Booking failed: ${error.message}`);
        }
    }

    // 新增处理原因提交的函数
    async function handleReasonSubmit() {
        const reason = document.getElementById('reasonInput').value.trim();
        if (!reason) {
            alert('Please enter booking reason');
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/insert_booking_with_reason', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...pendingBookingData,
                    reason: reason
                })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Booking failed');

            alert('Booking request submitted, awaiting approval.');
            document.getElementById('reasonModal').style.display = 'none';
            pendingBookingData = null;
            await fetchClassrooms();
        } catch (error) {
            console.error('Reason Submit Error:', error);
            alert(`Submission failed: ${error.message}`);
        }
    }


    // 初始化流程
    try {
        initTimeSelectors();
        initEventListeners();
        // 设置中国本地日期（新增代码）
        const today = new Date();
        elements.datePicker.value =
            `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        await fetchClassrooms();
        console.log('System initialization complete');
        
    } catch (error) {
        console.error('Initialization error:', error);
        alert('System initialization failed');
    }
});
