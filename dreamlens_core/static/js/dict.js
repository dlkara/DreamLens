document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("category");
    const keywordWrapper = document.getElementById("keyword-wrapper");

    function updateKeywordVisibility() {
        if (categorySelect.value) {
            keywordWrapper.style.display = "inline";
        } else {
            keywordWrapper.style.display = "none";
        }
    }

    updateKeywordVisibility();

    categorySelect.addEventListener("change", updateKeywordVisibility);
});
