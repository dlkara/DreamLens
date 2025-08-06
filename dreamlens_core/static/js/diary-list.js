document.addEventListener('DOMContentLoaded', () => {
    const entriesByDay = JSON.parse(
        document.getElementById('entriesByDayData').textContent
    );

    // 팝업 요소 생성
    const popup = document.createElement('div');
    popup.id = 'diary-popup';
    popup.className = 'diary-popup hidden';
    popup.innerHTML = `
        <div class="popup-content">
            <button class="popup-close" aria-label="닫기">&times;</button>
            <h2 class="popup-title"><span id="popup-date"></span>의 일기장</h2>
            <ul class="popup-list" id="popup-list"></ul>
        </div>
    `;
    document.body.appendChild(popup);

    const popupDate = popup.querySelector('#popup-date');
    const popupList = popup.querySelector('#popup-list');
    const popupClose = popup.querySelector('.popup-close');

    // 닫기 버튼
    popupClose.addEventListener('click', () => {
        popup.classList.add('hidden');
    });

    // 외부 클릭 시 팝업 닫기
    window.addEventListener('click', (e) => {
        if (e.target === popup) {
            popup.classList.add('hidden');
        }
    });

    // 날짜 셀 클릭 이벤트 등록
    document.querySelectorAll('td[data-day]').forEach(td => {
        td.addEventListener('click', () => {
            const day = td.getAttribute('data-day');
            const entries = entriesByDay[day] || [];

            if (entries.length === 0) return;

            // 날짜 타이틀 설정
            const year = document.querySelector('.calendar-nav span')?.textContent?.split('년')[0]?.trim();
            const month = document.querySelector('.calendar-nav span')?.textContent?.split('년')[1]?.replace('월','')?.trim();
            const dateStr = `${year}/${month.padStart(2, '0')}/${day.padStart(2, '0')}`;
            popupDate.textContent = dateStr;

            // 리스트 초기화
            popupList.innerHTML = '';

            // 일기 리스트 렌더링
            entries.forEach(entry => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = window.diaryDetailUrlTemplate.replace('0', entry.pk);
                a.textContent = entry.title.length > 20 ? entry.title.slice(0, 20) + '…' : entry.title;
                li.appendChild(a);
                popupList.appendChild(li);
            });

            popup.classList.remove('hidden');
        });
    });
});
