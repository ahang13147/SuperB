document.addEventListener('DOMContentLoaded', () => {
    const cancelButtons = document.querySelectorAll('.cancel-btn');
    const modal = document.getElementById('cancelModal');
    const closeModalBtn = document.getElementById('closeModal');
    const confirmCancelBtn = document.getElementById('confirmCancel');

    // 显示确认弹窗
    cancelButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const card = e.target.closest('.reservation-card');
            const reservationData = {
                date: card.querySelector('[data-date]').dataset.date,
                time: card.querySelector('[data-time]').dataset.time,
                room: card.querySelector('[data-room]').dataset.room,
                status: 'cancelled'
            };

            modal.dataset.reservation = JSON.stringify(reservationData);
            modal.style.display = 'flex';
        });
    });

    // 关闭弹窗
    closeModalBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // 确认取消
    confirmCancelBtn.addEventListener('click', async () => {
        const reservation = JSON.parse(modal.dataset.reservation);

        try {
            const response = await fetch('/api/cancel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reservation)
            });

            if (response.ok) {
                const card = document.querySelector(`[data-reservation-id="${reservation.id}"]`);
                card.querySelector('.status-indicator').textContent = 'Cancelled';
                card.querySelector('.status-indicator').style.backgroundColor = 'var(--danger-color)';
                card.querySelector('.cancel-btn').disabled = true;
                modal.style.display = 'none';
            } else {
                alert('Failed to cancel reservation');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred');
        }
    });

    // 点击外部关闭
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});