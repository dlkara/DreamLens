document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("dream-form");
    const btn = document.getElementById("combine-btn");

    form.addEventListener("submit", function () {
        btn.disabled = true;

        const loadingDiv = document.createElement("div");
        loadingDiv.id = "loading-message";
        loadingDiv.innerText = "🔄 해몽 중입니다...";
        loadingDiv.style.marginTop = "15px";
        loadingDiv.style.color = "#555";

        form.parentNode.insertBefore(loadingDiv, form.nextSibling);
    });
});
