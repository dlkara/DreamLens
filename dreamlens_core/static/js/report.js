/* static/js/report.js */

document.addEventListener('DOMContentLoaded', () => {
    const typeTab = document.getElementById('typeTab');
    const emotionTab = document.getElementById('emotionTab');
    const ctx = document.getElementById('reportChart').getContext('2d');
    let chart;

    // 1) 꿈 종류 키→한글 레이블 매핑 & 순서 & 컬러
    const DREAM_TYPE_LABELS = {
        good: '길몽',
        bad: '흉몽',
        normal: '일반몽'
    };
    const DREAM_TYPE_ORDER = ['good', 'bad', 'normal'];
    const DREAM_TYPE_COLORS = {
        good: '#28a745', // 초록
        bad: '#dc3545', // 붉은
        normal: '#6c757d'  // 회색
    };

    // 2) 감정별 컬러 매핑
    const EMOTION_COLOR_MAP = {
        '기쁨': '#FFD700',
        '행복': '#FFD700',
        '설렘': '#FF8C00',
        '즐거움': '#FF8C00',
        '평온': '#87CEEB',
        '무감정': '#808080',
        '불안': '#8A2BE2',
        '걱정': '#8A2BE2',
        '공포': '#4B0082',
        '두려움': '#4B0082',
        '슬픔': '#1E90FF',
        '외로움': '#1E90FF',
        '분노': '#DC143C',
        '짜증': '#DC143C',
        '기억': '#A9A9A9',
        '복합적': '#A9A9A9'
    };

    // 부분 일치(includes)로 색상을 찾아주는 함수
    function getEmotionColor(label) {
        for (const key in EMOTION_COLOR_MAP) {
            if (label.includes(key)) {
                return EMOTION_COLOR_MAP[key];
            }
        }
        return '#cccccc';  // 매핑 없을 때 기본 회색
    }

    // 3) 차트 생성 공통 함수
    function createChart(labels, data, colors) {
        if (chart) {
            chart.destroy();
        }
        chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                cutout: '50%',
                plugins: {
                    legend: {position: 'bottom'},
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.label}: ${ctx.formattedValue}건`
                        }
                    }
                }
            }
        });
    }

    // 4) “꿈 종류 분석” 탭 클릭 시
    function showDream() {
        const labels = DREAM_TYPE_ORDER.map(key => DREAM_TYPE_LABELS[key]);
        const data = DREAM_TYPE_ORDER.map(key => {
            const idx = dreamLabels.indexOf(key);
            return idx > -1 ? dreamData[idx] : 0;
        });
        const colors = DREAM_TYPE_ORDER.map(key => DREAM_TYPE_COLORS[key]);

        createChart(labels, data, colors);
        typeTab.classList.add('active');
        emotionTab.classList.remove('active');
    }

    // 5) “감정 분석” 탭 클릭 시
    function showEmotion() {
        const labels = emotionIcons.map((icon, i) =>
            `${icon} ${emotionLabels[i]}`
        );
        const data = emotionData;
        const colors = labels.map(lbl => getEmotionColor(lbl));

        createChart(labels, data, colors);
        emotionTab.classList.add('active');
        typeTab.classList.remove('active');
    }

    // 이벤트 바인딩 & 초기 표시
    typeTab.addEventListener('click', showDream);
    emotionTab.addEventListener('click', showEmotion);
    showDream();
});
