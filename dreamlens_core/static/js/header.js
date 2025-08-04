document.addEventListener("DOMContentLoaded", function () {
    const sidePanel = document.getElementById("sidePanel");
    const hamburgerBtn = document.getElementById("hamburgerBtn");
    const closeBtn = document.getElementById("closePanelBtn");

    if (hamburgerBtn && sidePanel) {
        hamburgerBtn.addEventListener("click", () => {
            sidePanel.classList.add("open");
            hamburgerBtn.style.display = "none";  // 햄버거 버튼 숨김
        });
    }

    if (closeBtn && sidePanel) {
        closeBtn.addEventListener("click", () => {
            sidePanel.classList.remove("open");
            hamburgerBtn.style.display = "block";  // 햄버거 버튼 다시 표시
        });
    }
});
