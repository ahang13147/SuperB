document.getElementById('eventForm').addEventListener('submit', function (event) {
    event.preventDefault();

    // 获取表单输入的数据
    const subject = document.getElementById('subject').value;
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;
    const busy = parseInt(document.getElementById('busy').value);
    const location = document.getElementById('location').value;
    const reminder_minutes = parseInt(document.getElementById('reminder_minutes').value);

    // 创建请求数据对象
    const data = {
        subject: subject,
        start: start,
        end: end,
        busy: busy,
        location: location,
        reminder_minutes: reminder_minutes
    };

    // 发送POST请求到后端
    fetch('https://101.200.197.132:5000/create_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else if (data.error) {
                alert('发生错误: ' + data.error);
            }
        })
        .catch(error => {
            alert('请求失败: ' + error);
        });
});
