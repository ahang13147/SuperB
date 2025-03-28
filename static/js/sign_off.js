document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('logout-btn').addEventListener('click', async function(event) {
        event.preventDefault(); // 阻止链接默认跳转行为
        try {
            // 添加await的请求
            const response = await fetch('https://www.diicsu.top:8000/log_out', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('请求失败');
            const data = await response.json();
            
            // 清除前端会话数据
            localStorage.clear();
            sessionStorage.clear();
            
            // 跳转到登录页
            window.location.href = '/login';
        } catch (error) {
            console.error('登出失败:', error);
            alert('登出操作异常，请检查网络连接');
        }
    });
});
