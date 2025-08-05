document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('dict-form');
    const category = document.getElementById('category');
    const subcat = document.getElementById('subcategory');

    // 대분류 변경 시 → 소분류 활성화 & 폼 제출
    category.addEventListener('change', () => {
        if (category.value) {
            subcat.disabled = false;
        } else {
            subcat.value = '';
            subcat.disabled = true;
        }
        form.submit();
    });

    // 소분류 변경 시 → 폼 제출
    subcat.addEventListener('change', () => {
        form.submit();
    });
});
