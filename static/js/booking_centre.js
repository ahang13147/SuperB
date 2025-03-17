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
            elements.endSelect.innerHTML += `<option value="${end}">${end}</option>`;
        });
    }

    // Get classroom data
    async function fetchClassrooms() {
        console.log(elements.datePicker.value); 
        const requestData = {
            capacity: parseInt(elements.capacityFilter.value) || undefined,
            room_name: elements.searchInput.value.trim() || undefined,
            date: elements.datePicker?.value || undefined,
            start_time: elements.startSelect.value || undefined, 
            end_time: elements.endSelect.value || undefined,    
            equipment: elements.equipmentFilter?.value || undefined
        };

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

            const classroomMap = new Map();

            responseData.results.forEach(room => {
                if (!classroomMap.has(room.room_id)) {
                    classroomMap.set(room.room_id, {
                        id: room.room_id,      
                        name: room.room_name,
                        type: room.room_type,  
                        capacity: room.capacity,
                        equipment: room.equipment ? room.equipment.split(', ') : [],
                        availableTimes: []
                    });
                }
                const classroom = classroomMap.get(room.room_id);
                classroom.availableTimes.push({
                    time: `${room.available_begin}-${room.available_end}`,
                    booked: room.availability === 2 
                });
            });

            classrooms = Array.from(classroomMap.values());
            renderClassrooms();
        } catch (error) {
            console.error('Failed to fetch classrooms:', error);
            alert('Failed to load classrooms. Please try again.');
        }
    }

    //  Rendering Classroom List
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

        document.querySelectorAll('.classroom-card button').forEach(button => {
            button.addEventListener('click', function () {
                const classroomName = this.closest('.classroom-card').dataset.classroom;
                const classroom = classrooms.find(c => c.name === classroomName);
                showBookingModal(classroom);
            });
        });
    }

    // Shows the scheduled popup window
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

         // Disable Modal event listening
        elements.closeModal.onclick = () => elements.modal.style.display = 'none';

         // Prevents modal from closing when you click the date picker
        elements.datePicker.addEventListener('click', (event) => {
            event.stopPropagation();  

        // Cause The pop-up closed event
        document.querySelector('.close-reason').onclick = () => {
            document.getElementById('reasonModal').style.display = 'none';
        };

        // Added Cause The event was submitted
        document.getElementById('submitReason').addEventListener('click', handleReasonSubmit);


        
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
            const response = await fetch('http://localhost:8000/insert_booking', {
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
            await fetchClassrooms();
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


    // Initialization process
    try {
        initTimeSelectors();
        initEventListeners();
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
