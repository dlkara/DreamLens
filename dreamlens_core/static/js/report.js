document.addEventListener('DOMContentLoaded', () => {
    const typeTab = document.getElementById('typeTab');
    const emotionTab = document.getElementById('emotionTab');
    const resultLabel = document.getElementById('resultLabel');
    const ctx = document.getElementById('reportChart').getContext('2d');
    let chart;

    // 1) 꿈 종류 매핑: 키→한글, 순서, 색상
    const DREAM_TYPE_LABELS = {good: '길몽', bad: '흉몽', normal: '일반몽'};
    const DREAM_TYPE_ORDER = ['good', 'bad', 'normal'];
    const DREAM_TYPE_COLORS = {
        good: '#28a745',
        bad: '#dc3545',
        normal: '#6c757d'
    };

    // 2) 감정별 색상 매핑
    const EMOTION_COLOR_MAP = {
        '기쁨': '#FFD700', '행복': '#FFD700',
        '설렘': '#FF8C00', '즐거움': '#FF8C00',
        '평온': '#87CEEB', '무감정': '#808080',
        '불안': '#8A2BE2', '걱정': '#8A2BE2',
        '공포': '#4B0082', '두려움': '#4B0082',
        '슬픔': '#1E90FF', '외로움': '#1E90FF',
        '분노': '#DC143C', '짜증': '#DC143C',
        '기억': '#A9A9A9', '복합적': '#A9A9A9'
    };

    function getEmotionColor(label) {
        for (const key in EMOTION_COLOR_MAP) {
            if (label.includes(key)) {
                return EMOTION_COLOR_MAP[key];
            }
        }
        return '#cccccc';
    }

    // 3) HEX → RGBA 변환 (투명도 조절용)
    function hexToRgba(hex, alpha) {
        const match = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
        if (!match) return hex;
        const [, r, g, b] = match;
        return `rgba(${parseInt(r, 16)}, ${parseInt(g, 16)}, ${parseInt(b, 16)}, ${alpha})`;
    }

    // 4) 차트 생성 공통 함수 (배경 80% 투명, 테두리 원색 1px)
    function createChart(labels, data, colors) {
        if (chart) chart.destroy();
        const bgColors = colors.map(c => hexToRgba(c, 0.6));
        const bdColors = colors;
        chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: bgColors,
                    borderColor: bdColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
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

    // 5) 결과 문구 업데이트
    function updateResultText(labels, data) {
        if (!data.length) {
            resultLabel.innerText = '–';
            return;
        }
        const maxIdx = data.reduce(
            (best, cur, i, arr) => (cur > arr[best] ? i : best),
            0
        );
        resultLabel.innerText = `"${labels[maxIdx]}"`;
    }

    // 6) “꿈 종류 분석” 표시
    function showDream() {
        const labels = DREAM_TYPE_ORDER.map(k => DREAM_TYPE_LABELS[k]);
        const data = DREAM_TYPE_ORDER.map(k => {
            const idx = dreamLabels.indexOf(k);
            return idx > -1 ? dreamData[idx] : 0;
        });
        const colors = DREAM_TYPE_ORDER.map(k => DREAM_TYPE_COLORS[k]);

        createChart(labels, data, colors);
        updateResultText(labels, data);
        typeTab.classList.add('active');
        emotionTab.classList.remove('active');
    }

    // 7) “감정 분석” 표시
    function showEmotion() {
        const labels = emotionIcons.map((ico, i) => `${ico} ${emotionLabels[i]}`);
        const data = emotionData;
        const colors = labels.map(l => getEmotionColor(l));

        createChart(labels, data, colors);
        updateResultText(labels, data);
        emotionTab.classList.add('active');
        typeTab.classList.remove('active');
    }

    // 8) 이벤트 바인딩 & 초기 로드
    typeTab.addEventListener('click', showDream);
    emotionTab.addEventListener('click', showEmotion);
    showDream();
});
