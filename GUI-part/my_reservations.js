document.addEventListener('DOMContentLoaded', () => {
    const reservationsContainer = document.querySelector('.reservations-container');
    const modal = document.getElementById('cancelModal');
    const closeModalBtn = document.getElementById('closeModal');
    const confirmCancelBtn = document.getElementById('confirmCancel');

    // 渲染预约卡片函数（适配数据库字段）
    function renderReservation(reservation) {
        return `
            <div class="reservation-card" data-reservation-id="${reservation.booking_id}">
                <div class="card-header">
                    <span class="room-tag" data-room-id="${reservation.room_id}">Room ${reservation.room_id}</span>
                    <span class="status-indicator" style="background: ${reservation.status === 'approved' ? 'var(--success-color)' : 'var(--danger-color)'}">
                        ${reservation.status}
                    </span>
                </div>
                <div class="card-body">
                    <p><span data-booking-date="${reservation.booking_date}">📅 ${reservation.booking_date}</span></p>
                    <p><span data-time-range="${reservation.start_time}-${reservation.end_time}">⏰ ${reservation.start_time} - ${reservation.end_time}</span></p>
                </div>
                ${['approved', 'pending'].includes(reservation.status) ?
                    `<button class="cancel-btn">Cancel Reservation</button>` :
                    `<button class="cancel-btn" disabled>Canceled</button>`}
            </div>
        `;
    }

    // 获取并展示预约信息（字段名对齐）
    async function loadReservations() {
        try {
            const response = await fetch('http://localhost:5000/bookings');
            const { bookings } = await response.json(); // 注意后端返回的数据结构

            reservationsContainer.innerHTML = bookings
                .map(reservation => renderReservation(reservation))
                .join('');

            // 重新绑定事件
            document.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.addEventListener('click', showCancelModal);
            });

        } catch (error) {
            console.error('Error:', error);
            reservationsContainer.innerHTML = `<p class="error">Failed to load reservations</p>`;
        }
    }

    // 弹窗逻辑（使用正确字段）
    function showCancelModal(e) {
        const card = e.target.closest('.reservation-card');
        const reservationData = {
            booking_id: card.dataset.reservationId, // 使用 booking_id
            booking_date: card.querySelector('[data-booking-date]').dataset.bookingDate,
            start_time: card.querySelector('[data-time-range]').dataset.timeRange.split('-')[0],
            end_time: card.querySelector('[data-time-range]').dataset.timeRange.split('-')[1],
            room_id: card.querySelector('[data-room-id]').dataset.roomId,
            status: 'canceled' // 注意数据库中是 canceled 不是 cancelled
        };

        modal.dataset.reservation = JSON.stringify(reservationData);
        modal.style.display = 'flex';
    }

    // 确认取消（发送正确数据结构）
    confirmCancelBtn.addEventListener('click', async () => {
        const reservation = JSON.parse(modal.dataset.reservation);

        try {
            const response = await fetch('http://127.0.0.1:5000/delete/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    booking_id: reservation.booking_id, // 关键字段
                    start_time:reservation.start_time,
                    end_time:reservation.end_time,
                    booking_date: reservation.booking_date,
                    status: 'canceled',
                })
            });

            if (response.ok) {
                const card = document.querySelector(`[data-reservation-id="${reservation.booking_id}"]`);
                card.querySelector('.status-indicator').textContent = 'canceled';
                card.querySelector('.status-indicator').style.backgroundColor = 'var(--danger-color)';
                card.querySelector('.cancel-btn').disabled = true;
                modal.style.display = 'none';
                loadReservations(); // 重新加载数据确保同步
            } else {
                alert('Failed to cancel reservation');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred');
        }
    });

    // 初始化加载
    loadReservations();

    // 其他事件监听保持不变...
    closeModalBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => e.target === modal && (modal.style.display = 'none'));
});