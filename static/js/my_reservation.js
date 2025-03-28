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
            const response = await fetch(`https://www.diicsu.top:8000/user-bookings`);
            const { bookings } = await response.json();

            reservationsContainer.innerHTML = bookings
                .map(reservation => renderReservation(reservation))
                .join('');
            document.querySelectorAll('.reservation-card').forEach(card => {
                card.style.display = 'block'; 
            });

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
                const result = await response.json();
                const card = document.querySelector(`[data-reservation-id="${reservation.booking_id}"]`);
                card.querySelector('.status-indicator').textContent = 'canceled';
                card.querySelector('.status-indicator').style.backgroundColor = 'var(--danger-color)';
                card.querySelector('.cancel-btn').disabled = true;
                modal.style.display = 'none';

                 // todo :add send email to user
                const emailResponse = await fetch('https://www.diicsu.top:8000/send_email/cancelled_user', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        booking_id: reservation.booking_id
                    })
                });
                if (emailResponse.ok) {
                    console.log('Cancellation email sent successfully.');
                } else {
                    console.error('Failed to send cancellation email.');
                }

                    //todo:  if thr user cancel more than 3times a day
                if (result.cancel_count >= 3) {
                  
                  const breakFaithResponse = await fetch('https://www.diicsu.top:8000/send_email/broadcast_break_faith', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      user_id: result.user_id
                    })
                  });

                  if (breakFaithResponse.ok) {
                    const breakFaithData = await breakFaithResponse.json();
                    console.log('Break faith email result:', breakFaithData.message);
                  } else {
                    console.error('Failed to send break-faith email.');
                  }
                }

                loadReservations();
            } else {
                alert('Failed to cancel reservation');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred');
        }
    });

    const dateSearchInput = flatpickr("#dateSearchInput", {
        dateFormat: "Y-m-d",
        onChange: function(selectedDates) {
            filterReservationsByDate(selectedDates[0] || null);
        }
    });

    function filterReservationsByDate(date) {
        if (!date) { 
            document.querySelectorAll('.reservation-card').forEach(card => {
                card.style.display = 'block';
            });
            return;
        }
        
        const targetDate = formatDate(date);
        document.querySelectorAll('.reservation-card').forEach(card => {
            const cardDate = card.querySelector('[data-booking-date]').dataset.bookingDate;
            card.style.display = cardDate === targetDate ? 'block' : 'none';
        });
    }
    // New date formatting tool function
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    document.getElementById('clearDateSearch').addEventListener('click', () => {
        dateSearchInput.clear();
        loadReservations();
        document.querySelectorAll('.reservation-card').forEach(card => {
            card.style.display = 'block';
        });
    });

    loadReservations();


    closeModalBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => e.target === modal && (modal.style.display = 'none'));
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
  document.querySelector('.hamburger-menu').addEventListener('click', function() {
    document.querySelector('.sidebar').classList.toggle('active');
  });
});
