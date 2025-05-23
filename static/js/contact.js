document.addEventListener('DOMContentLoaded', () => {
    const floatingButton = document.getElementById('contact-floatingButton');
    const modalOverlay = document.getElementById('contact-modalOverlay');
    const submitButton = document.getElementById('contact-submitButton');
    const userInput = document.getElementById('contact-userInput');

    if (floatingButton && modalOverlay && submitButton && userInput) {
        // 点击悬浮球
        floatingButton.addEventListener('click', () => {
            // 悬浮球缩小并消失
            floatingButton.style.transform = 'scale(0)';
            floatingButton.style.opacity = '0';
            floatingButton.style.pointerEvents = 'none';

            // 显示弹窗
            modalOverlay.classList.add('active');
        });

        // 点击遮罩层关闭弹窗
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                // 隐藏弹窗
                modalOverlay.classList.remove('active');

                // 恢复悬浮球
                floatingButton.style.transform = 'scale(1)';
                floatingButton.style.opacity = '1';
                floatingButton.style.pointerEvents = 'auto';
            }
        });

        // 点击提交按钮
        submitButton.addEventListener('click', () => {
            const message = userInput.value.trim();

            if (message) {
                // 使用 fetch 发送数据到 /email_admin
                fetch('/send_email/communicate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message }),
                })
                    .then(response => response.json())
                    .then(data => {
                        alert('Message sent successfully!');
                        userInput.value = ''; // 清空输入框
                        modalOverlay.classList.remove('active'); // 关闭弹窗
                        
                        // 新增：恢复悬浮球
                        floatingButton.style.transform = 'scale(1)';
                        floatingButton.style.opacity = '1';
                        floatingButton.style.pointerEvents = 'auto';
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Failed to send message.');
                    });
            } else {
                alert('Please enter a message.');
            }
        });
    } else {
        console.error('悬浮球组件未找到！请检查 HTML 结构。');
    }
});

