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

    // Rebind button events
    bindButtonEvents();
    handleReasonOverflow();
}

// Handle text overflow for reason field
function handleReasonOverflow() {
    document.querySelectorAll('.reason-text').forEach(span => {
        const reason = span.innerText.trim();

        // Check if text overflows container
        if (span.scrollHeight > span.clientHeight || span.scrollWidth > span.clientWidth) {
            const ellipsis = document.createElement("span");
            ellipsis.classList.add("ellipsis");
            ellipsis.innerHTML = "...";
            ellipsis.style.cursor = "pointer";
            ellipsis.style.color = "#007bff";
            ellipsis.style.fontWeight = "bold";
            ellipsis.style.marginLeft = "5px";

            // Show full text on ellipsis click
            ellipsis.addEventListener("click", function(event) {
                event.stopPropagation();
                showFullText(reason);
            });

            span.innerHTML = reason.substring(0, 50) + " ";
            span.appendChild(ellipsis);
        }
    });
}

// Display full text in alert (replace with modal if needed)
function showFullText(fullText) {
    alert(fullText);
}

// Handle approval/rejection actions
function handleApproval(action, card) {
    const bookingId = card.dataset.reservationId;
    const newStatus = action.toLowerCase();

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

        // Send appropriate emails based on status
        if (updatedBooking.status === 'approved') {
            sendEmail('success', updatedBooking.booking_id);
        } else if (updatedBooking.status === 'rejected') {
            sendEmail('rejected', updatedBooking.booking_id);
        }

        // Handle failed bookings notifications
        if (updatedBooking.failed_bookings?.length > 0) {
            updatedBooking.failed_bookings.forEach(failedId => {
                sendEmail('failed', failedId);
            });
        }

        // Refresh data based on current tab
        const activeTab = document.querySelector('.approval-tabs .tab.active');
        activeTab.dataset.tab === 'pending' ? fetchPendingBookings() : fetchFinishedBookings();

        alert(`${action} reservation ID: ${bookingId}`);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Operation failed. Please try again later');
    });
}

// Generic email sending function
function sendEmail(type, bookingId) {
    fetch(`https://www.diicsu.top:8000/send_email/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(resp => resp.json())
    .then(data => console.log(`${type} email sent:`, data))
    .catch(err => console.error(`Error sending ${type} email:`, err));
}

// Bind button click handlers
function bindButtonEvents() {
    document.querySelectorAll('.accept-btn, .reject-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.classList.contains('accept-btn') ? 'Approved' : 'Rejected';
            handleApproval(action, btn.closest('.approval-card'));
        });
    });
}

// Fetch completed bookings
function fetchFinishedBookings() {
    fetch('https://www.diicsu.top:8000/finished-workflow-bookings')
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        bookings = (Array.isArray(data?.bookings) ? data.bookings : []).filter(b => b.status !== 'pending');
        renderApprovalCards();
    })
    .catch(error => {
        console.error('Error fetching finished bookings:', error);
        bookings = [];
        renderApprovalCards();
    });
}

// Fetch pending bookings
function fetchPendingBookings() {
    fetch('https://www.diicsu.top:8000/pending-bookings')
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        bookings = Array.isArray(data?.bookings) ? data.bookings : [];
        renderApprovalCards();
    })
    .catch(error => {
        console.error('Error fetching pending bookings:', error);
        bookings = [];
        renderApprovalCards();
    });
}

// Initialize tab functionality
function initTabs() {
    const tabs = document.querySelectorAll('.approval-tabs .tab');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            tab.dataset.tab === 'pending' ? fetchPendingBookings() : fetchFinishedBookings();
        });
    });

    // Initial load
    fetchPendingBookings();
}

// Initialize UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initTabs();

    // Mobile menu handling
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    hamburger.addEventListener('click', (e) => {
        e.stopPropagation();
        sidebar.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('active') &&
            !e.target.closest('.sidebar') &&
            !e.target.closest('.hamburger-menu')) {
            sidebar.classList.remove('active');
        }
    });


    sidebar.addEventListener('click', (e) => e.stopPropagation());

    // Menu group handling
    document.querySelectorAll('.group-header').forEach(header => {
        header.addEventListener('click', function() {
            const group = this.closest('.menu-group');
            group.classList.toggle('active');
            document.querySelectorAll('.menu-group').forEach(other => {
                if (other !== group) other.classList.remove('active');
            });
        });
    });
});
