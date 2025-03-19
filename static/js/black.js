document.addEventListener("DOMContentLoaded", () => {
    const banReasonEl = document.getElementById("banReason");
    const banDurationEl = document.getElementById("banDuration");
    const randomMessageEl = document.getElementById("randomMessage");
    const apologyButton = document.getElementById("apologyButton");
    const soundEffect = document.getElementById("soundEffect");

    const funnyMessages = [
        "Your account needs a little break.",
        "Our system elves are cleaning up your mess.",
        "This operation confused the server.",
        "Detected your unique talent. Enjoy this timeout!",
        "Your actions were too awesome. Triggered safety mode.",
    ];

    // 获取随机消息
    const getRandomMessage = () => {
        return funnyMessages[Math.floor(Math.random() * funnyMessages.length)];
    };

    // 播放音效
    const playSound = () => {
        if (soundEffect) {
            soundEffect.play();
        }
    };

    // 获取黑名单数据
    const fetchBlacklistData = async () => {
        try {
            const response = await fetch("http://localhost:8000/get-blacklist-reason");
            const data = await response.json();
            console.log("Blacklist data:", data);  // 确保数据正确获取

            if (data.blacklists && data.blacklists.length > 0) {
                const blacklistEntry = data.blacklists[0]; // 取第一条黑名单数据
                banReasonEl.textContent = blacklistEntry.reason;
                banDurationEl.textContent = `From ${blacklistEntry.start_date} ${blacklistEntry.start_time} to ${blacklistEntry.end_date} ${blacklistEntry.end_time}`;
            } else {
                banReasonEl.textContent = "Unknown";
                banDurationEl.textContent = "Indefinite";
            }
        } catch (error) {
            console.error("Failed to fetch blacklist data:", error);
            banReasonEl.textContent = "Error loading data";
            banDurationEl.textContent = "Unknown";
        }
    };

    // 初始化页面数据
    randomMessageEl.textContent = getRandomMessage();
    fetchBlacklistData();

    // 绑定按钮点击事件
    apologyButton.addEventListener("click", playSound);
});
