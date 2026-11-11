const progressElement = document.querySelector(".progress");

function initSmoothProgressBar() {
    if (!progressElement) return;
    progressElement.innerHTML = `
        <div id="pbar-track" style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; overflow: hidden;">
            <div id="pbar-fill" style="position: absolute; left: 0; top: 0; height: 100%; width: 0%; background: linear-gradient(90deg, #00c853, #64dd17); transition: width 0.35s ease; opacity: 0.65;"></div>
            <span id="pbar-label" style="position: relative; z-index: 2; color: #ffffff; font-weight: bold; padding-left: 15px; font-size: 14px;">🟢 النظام جاهز [0%]</span>
        </div>
    `;
}

async function fetchProgressBar() {
    const fillEl = document.getElementById("pbar-fill");
    const labelEl = document.getElementById("pbar-label");
    if (!fillEl || !labelEl) return;

    try {
        const res = await fetch("/api/progress");
        const data = await res.json();
        const pct = Math.max(0, Math.min(100, data.percentage));

        fillEl.style.width = `${pct}%`;
        labelEl.innerText = `⏳ ${data.stage_text}   [${pct}%]`;
    } catch (err) {
        console.error("خطأ في جلب شريط التقدم:", err);
    }
}

initSmoothProgressBar();
setInterval(fetchProgressBar, 500);

