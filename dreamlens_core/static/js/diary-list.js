document.addEventListener('DOMContentLoaded', function () {
    // JSON 데이터 파싱
    const entriesByDayData = document.getElementById('entriesByDayData');
    let entriesByDay = {};

    if (entriesByDayData) {
        try {
            entriesByDay = JSON.parse(entriesByDayData.textContent);
        } catch (e) {
            console.error('JSON 파싱 오류:', e);
        }
    }

    // 팝업 요소들
    const popup = document.getElementById('diary-popup');
    const popupClose = popup.querySelector('.popup-close');
    const popupDate = document.getElementById('popup-date');
    const popupText = document.getElementById('popup-text');

    // 날짜 셀 클릭 이벤트 등록
    document.querySelectorAll('.calendar td[data-day]').forEach(td => {
        td.addEventListener('click', function () {
            const day = parseInt(this.dataset.day);
            const entries = entriesByDay[day] || [];

            // 날짜 업데이트
            popupDate.textContent = `${day}일`;

            // 팝업 내용 구성
            if (entries.length === 0) {
                popupText.innerHTML = `
                    <div class="popup-empty">
                        <div class="popup-empty-icon">😴</div>
                        <p>이 날에는 기록된 꿈이 없습니다.</p>
                        <p>새로운 꿈을 해몽해보세요!</p>
                    </div>
                `;
            } else {
                const listItems = entries.map(entry => {
                    const detailUrl = window.diaryDetailUrlTemplate.replace('0', entry.pk);

                    // result가 없을 경우 빈 문자열로 처리
                    let shortResult = entry.result || '';
                    if (shortResult.length > 80) {
                        shortResult = shortResult.substring(0, 80) + '...';
                    }

                    // 감정에 따른 이모지
                    let emotionEmoji = '💭';
                    if (entry.emotion) {
                        if (entry.emotion.includes('기쁨') || entry.emotion.includes('행복') || entry.emotion.includes('좋')) {
                            emotionEmoji = '😊';
                        } else if (entry.emotion.includes('슬픔') || entry.emotion.includes('우울') || entry.emotion.includes('나쁜')) {
                            emotionEmoji = '😢';
                        } else if (entry.emotion.includes('무서움') || entry.emotion.includes('두려움')) {
                            emotionEmoji = '😨';
                        } else if (entry.emotion.includes('화남') || entry.emotion.includes('분노')) {
                            emotionEmoji = '😠';
                        } else if (entry.emotion.includes('놀람')) {
                            emotionEmoji = '😲';
                        } else {
                            emotionEmoji = '😐';
                        }
                    }

                    return `
                        <li>
                            <a href="${detailUrl}">
                                <div class="entry-info">
                                    <div class="entry-header">
                                        <span class="entry-emotion">${emotionEmoji}</span>
                                        <span class="entry-type">${entry.dream_type || '꿈'}</span>
                                    </div>
                                    <div class="entry-content">${shortResult}</div>
                                    <div class="entry-preview">
                                        ${entry.title   
                                            ? (entry.title.length > 30 
                                                ? entry.title.substring(0, 30) + '···' 
                                                : entry.title)
                                            : '(내용 없음)'}
                                    </div>

                                </div>
                            </a>
                        </li>
                    `;
                }).join('');

                popupText.innerHTML = `<ul class="popup-list">${listItems}</ul>`;
            }

            // 팝업 표시
            showPopup();
        });
    });

    // 팝업 표시 함수
    function showPopup() {
        popup.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        setTimeout(() => {
            const content = popup.querySelector('.popup-content');
            content.style.animation = 'slideInUp 0.3s ease-out';
        }, 10);
    }

    // 팝업 닫기 함수
    function hidePopup() {
        popup.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // 닫기 버튼
    popupClose.addEventListener('click', hidePopup);

    // 배경 클릭 시 닫기
    popup.addEventListener('click', function (e) {
        if (e.target === popup) {
            hidePopup();
        }
    });

    // ESC 키로 닫기
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !popup.classList.contains('hidden')) {
            hidePopup();
        }
    });

    // 터치 디바이스에서 눌렀을 때 효과
    if ('ontouchstart' in window) {
        document.querySelectorAll('.calendar td[data-day]').forEach(td => {
            td.addEventListener('touchstart', function () {
                this.style.transform = 'translateY(-2px)';
            });

            td.addEventListener('touchend', function () {
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
    }

    // 데스크톱 호버 효과
    document.querySelectorAll('.calendar td[data-day]').forEach(td => {
        td.addEventListener('mouseenter', function () {
            if (window.innerWidth > 768) {
                this.style.transform = 'translateY(-2px) scale(1.02)';
                this.style.zIndex = '10';
            }
        });

        td.addEventListener('mouseleave', function () {
            if (window.innerWidth > 768) {
                this.style.transform = '';
                this.style.zIndex = '';
            }
        });
    });
});
