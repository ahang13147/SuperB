document.addEventListener('DOMContentLoaded', () => {
    const reservationsContainer = document.querySelector('.reservations-container');
    const modal = document.getElementById('cancelModal');
    const closeModalBtn = document.getElementById('closeModal');
    const confirmCancelBtn = document.getElementById('confirmCancel');

    const DEFAULT_USER_ID = 3;

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
            <div class="card-header">
                <span class="room-tag" data-room-id="${reservation.room_id}">${reservation.room_name}</span>
                <span class="status-indicator" data-status="${reservation.status}">
                    ${reservation.status}
                </span>
            </div>
            <div class="card-body">
                <p><span data-booking-date="${reservation.booking_date}">📅 ${reservation.booking_date}</span></p>
                <p><span data-time-range="${reservation.start_time}-${reservation.end_time}">⏰ ${reservation.start_time} - ${reservation.end_time}</span></p>
                ${reservation.reason ? `<p><span>Reason: ${reservation.reason}</span></p>` : ''}
            </div>
            ${['approved', 'pending'].includes(reservation.status) ?
                `<button class="cancel-btn">Cancel Reservation</button>` :
                `<button class="cancel-btn" disabled>Canceled</button>`}
        </div>
    `;
    }

    // Get and display reservation information (field name alignment)
    async function loadReservations() {
        showLoading();

        try {
            const response = await fetch(`https://www.diicsu.top:8000/user-bookings?user_id=${DEFAULT_USER_ID}`);
            const { bookings } = await response.json();

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
            booking_date: card.querySelector('[data-booking-date]').dataset.bookingDate,
            start_time: card.querySelector('[data-time-range]').dataset.timeRange.split('-')[0],
            end_time: card.querySelector('[data-time-range]').dataset.timeRange.split('-')[1],
            room_id: card.querySelector('[data-room-id]').dataset.roomId,
            status: 'canceled'
        };

        modal.dataset.reservation = JSON.stringify(reservationData);
        modal.style.display = 'flex';
    }

    confirmCancelBtn.addEventListener('click', async () => {
        const reservation = JSON.parse(modal.dataset.reservation);

        try {
            const response = await fetch(`https://www.diicsu.top:8000/cancel-booking/${reservation.booking_id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
            });

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
