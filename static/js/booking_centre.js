let pendingBookingData = null;
let classrooms = [];
let currentClassroom = null;
document.addEventListener('DOMContentLoaded', async () => {
    console.log('The document is loaded and initialization begins...');


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

    const elements = {
        classroomList: document.getElementById('classroomList'),
        searchInput: document.getElementById('searchKeyword'),
        capacityFilter: document.getElementById('capacityFilter'),
        startSelect: document.getElementById('startTime'),
        endSelect: document.getElementById('endTime'),
        datePicker: document.getElementById('datePicker'),
        equipmentFilter: document.getElementById('equipmentFilter'),
        modal: document.getElementById('bookingModal'),
        closeModal: document.querySelector('.close'),
        availableTimesContainer: document.getElementById('availableTimes'),
        confirmBookingButton: document.getElementById('confirmBooking')
    };

    // Initializes the time selector
    function initTimeSelectors() {
        elements.startSelect.innerHTML = '<option value="">Select start time</option>';
        elements.endSelect.innerHTML = '<option value="">Select end time</option>';

        timeSlots.forEach(slot => {
            const [start, end] = slot.split('-');
            elements.startSelect.innerHTML += `<option value="${start}">${start}</option>`;
        });

        // Add event listener to start time selector
        elements.startSelect.addEventListener('change', function() {
            const selectedStartTime = this.value;
            elements.endSelect.innerHTML = '<option value="">Select end time</option>';
            
            if (selectedStartTime) {
                // Find the index of the selected start time
                const startIndex = timeSlots.findIndex(slot => slot.startsWith(selectedStartTime));
                
                // Only show end times that are after the selected start time
                if (startIndex >= 0) {
                    for (let i = startIndex; i < timeSlots.length; i++) {
                        const [_, endTime] = timeSlots[i].split('-');
                        elements.endSelect.innerHTML += `<option value="${endTime}">${endTime}</option>`;
                    }
                }
            } else {
                // If no start time selected, show all end times
                timeSlots.forEach(slot => {
                    const [_, end] = slot.split('-');
                    elements.endSelect.innerHTML += `<option value="${end}">${end}</option>`;
                });
            }
        });

        // Initialize with all end times
        timeSlots.forEach(slot => {
            const [_, end] = slot.split('-');
            elements.endSelect.innerHTML += `<option value="${end}">${end}</option>`;
        });
    }

    // Get classroom data
    async function fetchClassrooms() {
        console.log(elements.datePicker.value);
    
            const capacityValue = parseInt(elements.capacityFilter.value);
            
            const requestData = {
                room_name: elements.searchInput.value.trim() || null,
                date: elements.datePicker?.value || null,
                start_time: elements.startSelect.value || null,
                end_time: elements.endSelect.value || null,
                equipment: elements.equipmentFilter?.value || null
            };

            //Use capacity or max_capacity based on the selected value
            if (capacityValue > 0) {
                if (capacityValue === 29) {
                    requestData.max_capacity = 29;
                    requestData.capacity = null; 
                } else {
                    requestData.capacity = capacityValue;
                    requestData.max_capacity = null;
                }
            }

            Object.keys(requestData).forEach(key => {
                if (requestData[key] === null) {
                    delete requestData[key];
                }
            });

        try {
            const response = await fetch('https://www.diicsu.top:8000/search-rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const responseData = await response.json();
            console.log('Response data:', responseData);

            const classroomMap = new Map();

            // 1.Filter out rooms with status 3
            const filteredRooms = responseData.results.filter(room => room.room_status !== 3);

            // 2. Gets all the room ids that need to be displayed
            const issueRoomIds = filteredRooms
                .filter(room => room.room_status === 1)
                .map(room => room.room_id);

            // 3. Obtain issue data in batches
            const issuesMap = await fetchIssuesForRooms(issueRoomIds);

            filteredRooms.forEach(room => {
                if (!classroomMap.has(room.room_id)) {
                    const isUnavailable = room.room_status === 2;

                    classroomMap.set(room.room_id, {
                        id: room.room_id,
                        name: room.room_name,
                        type: room.room_type,
                        capacity: room.capacity,
                        equipment: room.equipment ? room.equipment.split(', ') : [],
                        availableTimes: [],
                        status: room.room_status,
                        issues: issuesMap.get(room.room_id) || [],
                        disabled: isUnavailable // Mark not available for booking
                    });
                }

                const classroom = classroomMap.get(room.room_id);
                classroom.availableTimes.push({
                    time: `${room.available_begin}-${room.available_end}`,
                    booked: room.availability === 2 || classroom.disabled //Overlay unbookable state 
                });
            });

            classrooms = Array.from(classroomMap.values());
            renderClassrooms();
        } catch (error) {
            console.error('Failed to fetch classrooms:', error);
            alert('Failed to load classrooms. Please try again.');
        }
    }

    // Obtain issue data in batches
    async function fetchIssuesForRooms(roomIds) {
        if (roomIds.length === 0) return new Map();

        try {
            const promises = roomIds.map(roomId =>
                fetch(`https://www.diicsu.top:8000/get-issues/${roomId}`)
                    .then(res => res.json())
            );

            const results = await Promise.all(promises);
            return results.reduce((map, result, index) => {
                map.set(roomIds[index], result.issues);
                return map;
            }, new Map());
        } catch (error) {
            console.error('Failed to fetch issues:', error);
            return new Map();
        }
    }
    //  Rendering Classroom List
    function renderClassrooms() {
        const now = new Date();
        const currentHours = now.getHours();
        const currentMinutes = now.getMinutes();
        const isToday = elements.datePicker.value === `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

        elements.classroomList.innerHTML = classrooms.map(classroom => `
            <div class="classroom-card" data-classroom="${classroom.name}" ${classroom.disabled ? 'style="opacity:0.6"' : ''}>
                <h3>${classroom.name}</h3>
                
                ${classroom.status === 1 ? `
                    <div class="issue-alert">
                        ⚠️ Issues: 
                        ${classroom.issues.map(issue =>
                    `${issue.issue} (${issue.status})`
                ).join(', ')}
                    </div>
                ` : ''}

                <div class="details">
                    <p>Capacity: ${classroom.capacity} people</p>
                    <p>Equipment: ${classroom.equipment.join(', ')}</p>
                    <p>Available time slots:</p>
                    <ul>
                        ${classroom.availableTimes.map(t => {
                            let isPast = false;
                            if (isToday) {
                                const [start] = t.time.split('-');
                                const [startHour, startMinute] = start.split(':').map(Number);
                                if (startHour < currentHours || 
                                    (startHour === currentHours && startMinute < currentMinutes)) {
                                    isPast = true;
                                }
                            }
                            
                            const isDisabled = t.booked || isPast || classroom.disabled;
                            const pastText = isPast ? '<small>(Time passed)</small>' : '';
                            
                            return `
                            <li class="${isDisabled ? 'booked-slot' : ''}">
                                ${t.time}
                                ${t.booked ? '<span class="booked-marker">⛔️</span>' : ''}
                                ${pastText}
                            </li>
                            `;
                        }).join('')}
                    </ul>
                </div>
                <button ${classroom.disabled ? 'disabled style="background:#ccc"' : ''}>
                    ${classroom.disabled ? 'Unavailable' : 'Book Now'}
                </button>
            </div>
        `).join('');

        document.querySelectorAll('.classroom-card button').forEach(button => {
            button.addEventListener('click', function() {
                const classroomName = this.closest('.classroom-card').dataset.classroom;
                const classroom = classrooms.find(c => c.name === classroomName);
                showBookingModal(classroom);
            });
        });
    }

    // Shows the scheduled popup window
function showBookingModal(classroom) {
    currentClassroom = classroom;
    const now = new Date();
    const currentHours = now.getHours();
    const currentMinutes = now.getMinutes();
    const isToday = elements.datePicker.value === `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

    elements.availableTimesContainer.innerHTML = classroom.availableTimes.map(timeSlot => {
        const [start, end] = timeSlot.time.split('-');
        const [startHour, startMinute] = start.split(':').map(Number);
        const [endHour, endMinute] = end.split(':').map(Number);
        
        // Check if the time slot is in the past
        let isPast = false;
        if (isToday) {
            if (startHour < currentHours || 
                (startHour === currentHours && startMinute < currentMinutes)) {
                isPast = true;
            }
        }
        
        const isDisabled = timeSlot.booked || isPast;
        const pastText = isPast ? '<small>(Time passed)</small>' : '';

        return `
        <div class="time-slot ${isDisabled ? 'time-slot-disabled' : ''}">
            <input
                type="radio"
                name="timeSlot"
                id="slot_${timeSlot.time.replace(/:/g, '')}"
                value="${timeSlot.time}"
                ${isDisabled ? 'disabled' : ''}
            >
            <label for="slot_${timeSlot.time.replace(/:/g, '')}">
                ${isDisabled ? '⛔️ ' : '🕒 '}
                ${timeSlot.time}
                ${timeSlot.booked ? '<small>(Booked)</small>' : pastText}
            </label>
        </div>
        `;
    }).join('');

    elements.availableTimesContainer.querySelectorAll('.time-slot').forEach(slot => {
        const radio = slot.querySelector('input[type="radio"]');
        radio.addEventListener('change', () => {
            document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('checked'));
            if (radio.checked) slot.classList.add('checked');
        });
    });

    elements.modal.style.display = 'block';
}

    // Initialize event listening
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

        // Bind closed cause Mode frame event
        document.querySelector('.close-reason').addEventListener('click', () => {
            document.getElementById('reasonModal').style.display = 'none';
        });

        // Bind commit cause event
        document.getElementById('submitReason').addEventListener('click', handleReasonSubmit);

        // Disable Modal event listening
        elements.closeModal.onclick = () => elements.modal.style.display = 'none';

        // Prevents modal from closing when you click the date picker
        elements.datePicker.addEventListener('click', (event) => {
            event.stopPropagation();
            

        });

        // Turn off Modal event listening: It is only turned off by clicking on the modal background
        window.onclick = event => {
            if (event.target == elements.modal) {
                elements.modal.style.display = 'none';
            }
        };
    }

    // The modified handleBookingConfirmation function:
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

        const userId = 3;

        try {
            const response = await fetch('https://www.diicsu.top:8000/insert_booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: currentClassroom.id,
                    user_id: userId,
                    booking_date: bookingDate,
                    start_time: startTime,
                    end_time: endTime,
                    reason: ''
                })
            });

            const data = await response.json();
            if (!response.ok) {
                if (data.status === 'require_reason') {
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
            // todo: add new function for send email
            await fetch('https://www.diicsu.top:8000/send_email/success', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    booking_id: data.booking_id  // Make sure the back end returns booking_id
                })
            });
            await fetchClassrooms();
            await fetch('https://www.diicsu.top:8000/send_email/calendar_invite',{
                method:'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: data.room_id,
                    booking_date: data.booking_date,
                    start_time: data.start_time,
                    end_time: data.end_time
                })
            })
        } catch (error) {
            console.error('Booking Error:', error);
            alert(`Booking failed: ${error.message}`);
        }
    }

    // Function that handles the cause of submission
    async function handleReasonSubmit() {
        const reason = document.getElementById('reasonInput').value.trim();
        if (!reason) {
            alert('Please enter booking reason');
            return;
        }

        try {
            const response = await fetch('https://www.diicsu.top:8000/insert_booking_with_reason', {
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

            //todo ：0326 Call backend email notification after successful insertion
            const emailResponse = await fetch('https://www.diicsu.top:8000/send_email/broadcast_pending', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ booking_id: data.booking_id })
            });

            const emailData = await emailResponse.json();
            if (!emailResponse.ok) throw new Error(emailData.message || 'Email notification failed');

            console.log('Email notification:', emailData.message);


            document.getElementById('reasonModal').style.display = 'none';
            pendingBookingData = null;
            await fetchClassrooms();
        } catch (error) {
            console.error('Reason Submit Error:', error);
            alert(`Submission failed: ${error.message}`);
        }
    }


    // Initialization process
    try {
        initTimeSelectors();
        initEventListeners();
        const today = new Date();
        const todayFormatted = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        
        // Set minimum date to today
        elements.datePicker.min = todayFormatted;
        elements.datePicker.value = todayFormatted;
        
        await fetchClassrooms();
        console.log('System initialization complete');
    } catch (error) {
        console.error('Initialization error:', error);
        alert('System initialization failed');
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    hamburger.addEventListener('click', function () {
        sidebar.classList.toggle('active');
    });

    document.addEventListener('click', function (e) {
        if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });


    
});


