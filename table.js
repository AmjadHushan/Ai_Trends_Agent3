const tableEl = document.querySelector(".table");
const letters = ["a", "b", "c", "d", "e", "f", "g", "h"];
const timers = {};

function assignCellIds() {
    const trs = tableEl.querySelectorAll("tr");
    for (let r = 2; r < trs.length; r++) {
        const rowNum = r - 1;
        const tds = trs[r].querySelectorAll("td");
        for (let c = 1; c <= 8; c++) {
            if (tds[c]) {
                const letter = letters[c - 1];
                const id = `${letter}${rowNum}`;
                tds[c].dataset.cellId = id;
                tds[c].dataset.colLetter = letter;
                tds[c].dataset.rowNum = rowNum;
                tds[c].title = `خلية: ${id}`;
            }
        }
    }
}

tableEl.addEventListener("input", (e) => {
    const cell = e.target;
    if (cell.tagName === "TD" && cell.dataset.cellId) {
        const id = cell.dataset.cellId;
        clearTimeout(timers[id]);
        timers[id] = setTimeout(async () => {
            await fetch("/api/table/cell", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    cell_id: id,
                    col_letter: cell.dataset.colLetter,
                    row_num: parseInt(cell.dataset.rowNum),
                    value: cell.innerText.trim()
                })
            });
            console.log(`💾 تم الحفظ التلقائي: [${id}] = ${cell.innerText.trim()}`);
        }, 500);
    }
});

async function restoreCells() {
    try {
        const res = await fetch("/api/table/cells");
        const data = await res.json();
        const saved = data.cells || {};
        document.querySelectorAll(".table td[data-cell-id]").forEach(td => {
            const id = td.dataset.cellId;
            if (saved[id] !== undefined) {
                td.innerText = saved[id];
            }
        });
    } catch (err) {
        console.error("خطأ في استرجاع الخلايا:", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    assignCellIds();
    restoreCells();
});

