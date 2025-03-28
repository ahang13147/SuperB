document.addEventListener('DOMContentLoaded', () => {
    const reservationsContainer = document.querySelector('.reservations-container');
    const modal = document.getElementById('cancelModal');
    const closeModalBtn = document.getElementById('closeModal');
    const confirmCancelBtn = document.getElementById('confirmCancel');
    const infoModal = document.getElementById('infoModal');
    const closeInfoModal = document.getElementById('closeInfoModal');
    const infoModalMessage = document.getElementById('infoModalMessage');


    
    // Show loading status
    function showLoading() {
        reservationsContainer.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i> Loading...
            </div>
        `;
    }

    // Hide the loading state and display the contents
    function hideLoading() {
        const loadingSpinner = document.querySelector('.loading-spinner');
        if (loadingSpinner) {
            loadingSpinner.remove();
        }
    }

    // Render the reservation card function
function renderReservation(reservation) {
    return `
    <div class="reservation-card" data-reservation-id="${reservation.booking_id}">
        <div class="reservation-info">
            <label>User ID:</label>
            <span data-user-id="${reservation.user_id}">${reservation.user_id}</span>
        </div>
        <div class="reservation-info">
            <label>User Name:</label>
            <span data-username="${reservation.username}">${reservation.username}</span>
        </div>
        <div class="reservation-info">
            <label>Date:</label>
            <span data-date="${reservation.booking_date}">${reservation.booking_date}</span>
        </div>
        <div class="reservation-info">
            <label>Time:</label>
            <span data-time="${reservation.start_time} - ${reservation.end_time}">${reservation.start_time} - ${reservation.end_time}</span>
        </div>
        <div class="reservation-info">
            <label>Room:</label>
            <span data-room="${reservation.room_name}">${reservation.room_name}</span>
        </div>
        <span class="status-indicator" data-status="${reservation.status.toLowerCase()}">${reservation.status}</span>
        <div class="reservation-info">
            <label>Reason:</label>
            <span data-reason="${reservation.reason || 'No reason provided'}">${reservation.reason || 'No reason provided'}</span>
        </div>
        <button class="cancel-btn">Cancel Reservation</button>
    </div>
    `;
}

     // Search function with status filter
function searchReservations() {
    const searchTerm = document.getElementById('searchReservationInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
    const cards = document.querySelectorAll('.reservation-card');

    cards.forEach(card => {
        const userId = card.querySelector('[data-user-id]')?.textContent?.toLowerCase() || '';
        const userName = card.querySelector('[data-username]')?.textContent?.toLowerCase() || '';
        const roomName = card.querySelector('[data-room]')?.textContent?.toLowerCase() || '';
        const cardStatus = card.querySelector('.status-indicator')?.dataset?.status?.toLowerCase() || '';

        const matchesSearch = userId.includes(searchTerm) ||
                            userName.includes(searchTerm) ||
                            roomName.includes(searchTerm);
        const matchesStatus = !statusFilter || cardStatus === statusFilter;

        card.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
    });
}

    // Check if a booking is in the future
    function isBookingInFuture(booking) {
        const now = new Date();
        const bookingDate = new Date(`${booking.booking_date}T${booking.start_time}`);
        return bookingDate > now;
    }

    // Get and display all approved and future reservations
    async function loadReservations() {
        showLoading();

        try {
            const response = await fetch(`https://www.diicsu.top:8000/bookings`);
            const { bookings } = await response.json();
            reservationsContainer.innerHTML = bookings
                .map(reservation => renderReservation(reservation))
                .join('');

            document.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.addEventListener('click', showCancelModal);
            });

            searchReservations();

        } catch (error) {
            console.error('Error:', error);
            reservationsContainer.innerHTML = `<p class="error">Failed to load reservations</p>`;
        } finally {
            hideLoading();
        }
    }

    function showCancelModal(e) {
        const card = e.target.closest('.reservation-card');
        const status = card.querySelector('.status-indicator').dataset.status.toLowerCase();
        
        // Only allow cancellation for approved and changed statuses
        if (status !== 'approved' && status !== 'changed') {
            infoModalMessage.textContent = `This booking is ${status} and cannot be canceled. Only approved or changed bookings can be canceled.`;
            infoModal.style.display = 'flex';
            return;
        }

        const reservationData = {
            booking_id: card.dataset.reservationId,
            booking_date: card.querySelector('[data-date]').dataset.date,
            start_time: card.querySelector('[data-time]').dataset.time.split(' - ')[0],
            end_time: card.querySelector('[data-time]').dataset.time.split(' - ')[1],
            room_name: card.querySelector('[data-room]').dataset.room,
            status: 'canceled',
            reason: card.querySelector('[data-reason]').dataset.reason
        };

        modal.dataset.reservation = JSON.stringify(reservationData);
        modal.style.display = 'flex';
    }
    // Added the ability to click external to close the mode box
    window.addEventListener('click', (e) => {
        if (e.target === infoModal) {
            infoModal.style.display = 'none';
        }
    });

    confirmCancelBtn.addEventListener('click', async () => {
      const reservation = JSON.parse(modal.dataset.reservation);

      try {
        // Construct the URL correctly: Insert booking_id using a template string
        const response = await fetch(
          `https://www.diicsu.top:8000/cancel-booking/${reservation.booking_id}`, // Remove redundant symbols and insert variables
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        // The subsequent logic remains unchanged
        if (response.ok) {
          const card = document.querySelector(`[data-reservation-id="${reservation.booking_id}"]`);
          card.querySelector('.status-indicator').textContent = 'canceled';
          card.querySelector('.status-indicator').style.backgroundColor = 'var(--danger-color)';
          card.querySelector('.cancel-btn').disabled = true;
          modal.style.display = 'none';
          loadReservations();
        } else {
          alert('Failed to cancel reservation');
        }
      } catch (error) {
        console.error('Error:', error);
        alert('An error occurred');
      }
    });

     // Expose search function to global scope
    window.searchReservations = searchReservations;

    loadReservations();

    closeModalBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => e.target === modal && (modal.style.display = 'none'));
    closeInfoModal.addEventListener('click', () => {
        infoModal.style.display = 'none';
    });

    const searchInput = document.getElementById('searchReservationInput');
    const statusFilter = document.getElementById('statusFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', searchReservations);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', searchReservations);
    }
});



document.addEventListener('DOMContentLoaded', function() {
  // Process menu group click
  document.querySelectorAll('.group-header').forEach(header => {
    header.addEventListener('click', function() {
      const group = this.closest('.menu-group');
      group.classList.toggle('active');

      // Close other expanded menu groups
      document.querySelectorAll('.menu-group').forEach(otherGroup => {
        if (otherGroup !== group) {
          otherGroup.classList.remove('active');
        }
      });
    });
  });

  // Mobile burger menu switch
  const hamburger = document.querySelector('.hamburger-menu');
  const sidebar = document.querySelector('.sidebar');

  hamburger.addEventListener('click', function(e) {
    e.stopPropagation(); 
    sidebar.classList.toggle('active');
  });

  // Click outside to close the sidebar
  document.addEventListener('click', function(e) {
    if (sidebar.classList.contains('active') &&
        !e.target.closest('.sidebar') &&
        !e.target.closest('.hamburger-menu')) {
      sidebar.classList.remove('active');
    }
  });

  // Prevents clicking inside the sidebar from triggering closure
  sidebar.addEventListener('click', function(e) {
    e.stopPropagation();
  });
});