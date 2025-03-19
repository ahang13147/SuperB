document.addEventListener('DOMContentLoaded', () => {
    const reservationsContainer = document.querySelector('.reservations-container');
    const modal = document.getElementById('cancelModal');
    const closeModalBtn = document.getElementById('closeModal');
    const confirmCancelBtn = document.getElementById('confirmCancel');

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
            <span>${reservation.user_id}</span>
        </div>
        <div class="reservation-info">
            <label>User Name:</label>
            <span>${reservation.username}</span>
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
        <span class="status-indicator" data-status="${reservation.status}">${reservation.status}</span>
        <div class="reservation-info">
            <label>Reason:</label>
            <span data-reason="${reservation.reason || 'No reason provided'}">${reservation.reason || 'No reason provided'}</span>
        </div>
        <button class="cancel-btn">Cancel Reservation</button>
    </div>
    `;
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
            const response = await fetch(`http://127.0.0.1:8000/bookings`);
            const { bookings } = await response.json();


//            // Filter bookings to only show approved and future ones
//            const filteredBookings = bookings.filter(booking =>
//                (booking.status === 'approved' || booking.status === 'canceled') && isBookingInFuture(booking)
//            );


            reservationsContainer.innerHTML = bookings
                .map(reservation => renderReservation(reservation))
                .join('');

            document.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.addEventListener('click', showCancelModal);
            });

        } catch (error) {
            console.error('Error:', error);
            reservationsContainer.innerHTML = `<p class="error">Failed to load reservations</p>`;
        } finally {
            hideLoading();
        }
    }

    function showCancelModal(e) {
        const card = e.target.closest('.reservation-card');
        const reservationData = {
            booking_id: card.dataset.reservationId,
            booking_date: card.querySelector('[data-date]').dataset.date,
            start_time: card.querySelector('[data-time]').dataset.time.split(' - ')[0],
            end_time: card.querySelector('[data-time]').dataset.time.split(' - ')[1],
            room_name: card.querySelector('[data-room]').dataset.room,
            status: 'canceled',
            reason: card.querySelector('[data-reason]').dataset.reason// Add reason to the reservation data
        };

        modal.dataset.reservation = JSON.stringify(reservationData);
        modal.style.display = 'flex';
    }

    confirmCancelBtn.addEventListener('click', async () => {
      const reservation = JSON.parse(modal.dataset.reservation);

      try {
        // 正确构造 URL：使用模板字符串插入 booking_id
        const response = await fetch(
          `http://127.0.0.1:8000/cancel-booking/${reservation.booking_id}`, // 移除多余符号并插入变量
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        // 后续逻辑保持不变
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

    loadReservations();

    closeModalBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => e.target === modal && (modal.style.display = 'none'));
});


document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    hamburger.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });

    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
});
