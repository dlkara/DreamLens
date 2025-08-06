document.addEventListener('DOMContentLoaded', () => {
    // 1) 날짜별 일기 데이터를 JSON으로 파싱
    const entriesByDay = JSON.parse(
        document.getElementById('entriesByDayData').textContent
    );

    // 2) 상세보기 URL 템플릿 (".../diary/detail/0/") 에서 pk=0 부분을 교체해서 사용
    const urlTemplate = window.diaryDetailUrlTemplate;

    // 3) 모달 구조 생성 및 이벤트 바인딩
    const modal = document.createElement('div');
    modal.id = 'diaryModal';
    modal.className = 'modal';
    modal.innerHTML = `
    <div class="modal-content">
      <span class="modal-close">&times;</span>
      <ul id="diaryEntriesList"></ul>
    </div>
  `;
    document.body.appendChild(modal);

    const entryList = modal.querySelector('#diaryEntriesList');
    const closeBtn = modal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', e => {
        if (e.target === modal) modal.style.display = 'none';
    });

    // 4) 각 날짜 셀에 클릭 핸들러 등록
    document.querySelectorAll('td[data-day]').forEach(td => {
        td.addEventListener('click', () => {
            const day = td.getAttribute('data-day');
            const entries = entriesByDay[day] || [];

            // 일기 없으면 모달 열지 않음
            if (entries.length === 0) return;

            // 기존 목록 초기화
            entryList.innerHTML = '';

            // 제목이 20자 초과 시 자르고 '...' 추가
            entries.forEach(entry => {
                const title = entry.title.length > 20
                    ? entry.title.slice(0, 20) + '…'
                    : entry.title;

                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = urlTemplate.replace('0', entry.pk);
                a.textContent = title;
                li.appendChild(a);
                entryList.appendChild(li);
            });

            // 모달 띄우기
            modal.style.display = 'block';
        });
    });
});
