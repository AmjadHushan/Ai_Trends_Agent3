const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-in");
const chatSendBtn = document.getElementById("chat-send");

let lastMessageCount = 0;

// إرسال رسالة إلى الخادم
async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = "";

    try {
        await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        fetchStatus();
    } catch (err) {
        console.error("❌ خطأ في إرسال الرسالة:", err);
    }
}

// ربط زر الإرسال ومفتاح Enter في الكيبورد
chatSendBtn.addEventListener("click", sendChatMessage);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendChatMessage();
    }
});

// جلب الرسائل من قاعدة البيانات وتحديث الشات دورياً
async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        const data = await res.json();

        if (data.messages && data.messages.length !== lastMessageCount) {
            chatBox.innerHTML = "";
            data.messages.forEach(msg => {
                const div = document.createElement("div");
                div.className = `msg ${msg.sender}`;
                div.style.whiteSpace = "pre-line";
                div.innerText = msg.text;
                chatBox.appendChild(div);
            });
            chatBox.scrollTop = chatBox.scrollHeight;
            lastMessageCount = data.messages.length;
        }
    } catch (err) {
        console.error("خطأ في جلب رسائل الشات:", err);
    }
}

setInterval(fetchStatus, 1000);
fetchStatus();

