
let bookings = [];

// Dynamically generate approval cards
function renderApprovalCards() {
    const container = document.querySelector('.approvals-container');
    container.innerHTML = ''; // Clear existing content


    if (!Array.isArray(bookings)) {
        console.error('bookings is not an array:', bookings);
        bookings = [];
    }

    if (bookings.length === 0) {
        container.innerHTML = '<div class="no-data">No bookings found.</div>';
        return;
    }

    bookings.forEach(booking => {
        const card = document.createElement('div');
        card.className = `approval-card ${booking.status === 'pending' ? '' : 'reviewed'}`;
        card.dataset.reservationId = booking.booking_id;

        // Card HTML structure
        card.innerHTML = `
      <div class="reservation-info"><label>Booking ID:</label> <span>${booking.booking_id}</span></div>
      <div class="reservation-info"><label>User Name:</label> <span>${booking.user_name}</span></div>
      <div class="reservation-info"><label>Room Name:</label> <span>${booking.room_name}</span></div>
      <div class="reservation-info"><label>Date:</label> <span>${booking.booking_date}</span></div>
      <div class="reservation-info"><label>Time:</label> <span>${booking.start_time} - ${booking.end_time}</span></div>
      <div class="reservation-info"><label>Reason:</label> <span class="reason-text">${booking.reason}</span></div>
      ${booking.status === 'pending' ? `
        <div class="approval-actions">
          <button class="accept-btn">Accept</button>
          <button class="reject-btn">Reject</button>
        </div>
      ` : `<div class="status-indicator ${booking.status}">${booking.status.toUpperCase()}</div>`}
    `;

        container.appendChild(card);
    });


    // Rebind button event
    bindButtonEvents();
    handleReasonOverflow();
}


// Detects if the Reason text is exceeded and adds an ellipsis
function handleReasonOverflow() {
    document.querySelectorAll('.reason-text').forEach(span => {
        let reason = span.innerText.trim();

        // Check whether the container is exceeded first
        if (span.scrollHeight > span.clientHeight || span.scrollWidth > span.clientWidth) {
            let ellipsis = document.createElement("span");
            ellipsis.classList.add("ellipsis");
            ellipsis.innerHTML = "...";
            ellipsis.style.cursor = "pointer";
            ellipsis.style.color = "#007bff";
            ellipsis.style.fontWeight = "bold";
            ellipsis.style.marginLeft = "5px";

            // Click on '... 'Show the full content
            ellipsis.addEventListener("click", function (event) {
                event.stopPropagation(); // Prevent bubbling, prevent miscontact
                showFullText(reason);
            });

            span.innerHTML = reason.substring(0, 50) + " ";
            span.appendChild(ellipsis);
        }
    });
}

// Display full text (can be replaced with Modal)
function showFullText(fullText) {
    alert(fullText); //
}

// Process approval operation
function handleApproval(action, card) {
    const bookingId = card.dataset.reservationId;
    const newStatus = action.toLowerCase();

    console.log(`Attempting to ${action} booking ID: ${bookingId}`);


    // 修正模板字符串用法
    fetch(`https://www.diicsu.top:8000/update-booking-status/${bookingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
        .then(response => {
            if (!response.ok) throw new Error('Update failed');
            return response.json();
        })
        .then(updatedBooking => {
            console.log('Updated booking:', updatedBooking);

            // Update local data
            const index = bookings.findIndex(b => b.booking_id === bookingId);
            if (index !== -1) {
                bookings[index] = updatedBooking; // Replace entire object
            }

            // Reload the data based on the current TAB
            const activeTab = document.querySelector('.approval-tabs .tab.active');
            if (activeTab.dataset.tab === 'pending') {
                fetchPendingBookings();
            } else if (activeTab.dataset.tab === 'finished') {
                fetchFinishedBookings();
            }

            alert(`${action} reservation ID: ${bookingId}`);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('The operation failed. Please try again later');
        });
}

// Bind button event
function bindButtonEvents() {
    document.querySelectorAll('.accept-btn, .reject-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.classList.contains('accept-btn') ? 'Approved' : 'Rejected';

            const card = btn.closest('.approval-card');
            handleApproval(action, card);
        });
    });
}

//Get a completed workflow reservation
function fetchFinishedBookings() {
    fetch('https://www.diicsu.top:8000/finished-workflow-bookings')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data && Array.isArray(data.bookings)) {
                bookings = data.bookings.filter(b => b.status !== 'pending'); // Ensure that only approved data is displayed
            } else {
                console.error('Invalid data format:', data);
                bookings = [];
            }
            renderApprovalCards();
        })
        .catch(error => {
            console.error('Error fetching finished bookings:', error);
            bookings = [];
            renderApprovalCards();
        });
}


// Get a pending reservation
function fetchPendingBookings() {
    fetch('https://www.diicsu.top:8000/pending-bookings')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Make sure that data.bookings is an array
            if (data && Array.isArray(data.bookings)) {
                bookings = data.bookings;
            } else {
                console.error('Invalid data format:', data);
                bookings = []; // Set to an empty array to avoid errors
            }
            renderApprovalCards();
        })
        .catch(error => {
            console.error('Error fetching pending bookings:', error);
            bookings = [];
            renderApprovalCards(); // Even if something goes wrong, try to render empty data
        });
}

// Initializes the label switching function
function initTabs() {
    const tabs = document.querySelectorAll('.approval-tabs .tab');


    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');


            if (tab.dataset.tab === 'pending') {
                fetchPendingBookings();
            } else if (tab.dataset.tab === 'finished') {
                fetchFinishedBookings();
            } else {
                console.error('Unknown tab:', tab.dataset.tab);
            }
        });
    });

    //load pending
    fetchPendingBookings();
}


//initialization GUI
document.addEventListener('DOMContentLoaded', () => {

    initTabs();
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
