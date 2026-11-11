const btnStart = document.querySelector(".start");

if (btnStart) {
    btnStart.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/buttons/start", { method: "POST" });
            const data = await res.json();
            if (data.status === "error") {
                alert(data.message); // ينبهك إذا نسيت تشغيل مفتاح الباور On
            } else {
                console.log(data.message);
            }
        } catch (err) {
            console.error("❌ خطأ في إرسال أمر Start:", err);
        }
    });
}

