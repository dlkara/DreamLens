document.addEventListener('DOMContentLoaded', () => {
    const typeTab = document.getElementById('typeTab');
    const emotionTab = document.getElementById('emotionTab');
    const resultText = document.getElementById('resultText');
    const ctx = document.getElementById('reportChart').getContext('2d');
    const infoBox = document.getElementById('reportInfo');
    const year = infoBox.dataset.year;
    const month = infoBox.dataset.month;
    const hasData = infoBox.dataset.hasData === '1';
    let chart;

    // 색상 설정
    const DREAM_TYPE_LABELS = {good: '길몽', bad: '흉몽', normal: '일반몽'};
    const DREAM_TYPE_ORDER = ['good', 'bad', 'normal'];
    const DREAM_TYPE_COLORS = {
        good: '#28a745',
        bad: '#dc3545',
        normal: '#6c757d'
    };
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
            if (label.includes(key)) return EMOTION_COLOR_MAP[key];
        }
        return '#cccccc';
    }

    function hexToRgba(hex, alpha) {
        const match = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
        if (!match) return hex;
        const [, r, g, b] = match;
        return `rgba(${parseInt(r, 16)}, ${parseInt(g, 16)}, ${parseInt(b, 16)}, ${alpha})`;
    }

    function createChart(labels, data, colors) {
        if (chart) chart.destroy();
        chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: colors.map(c => hexToRgba(c, 0.3)),
                    borderColor: colors,
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

    function renderResult(prefix, label) {
        resultText.innerHTML = `${prefix} <strong id="resultLabel">"${label}"</strong>이네요!`;
    }

    function showDream() {
        if (!hasData) {
            resultText.innerHTML = `<span style="color: #888;">${year}년 ${month}월에는 꿈 일기가 없습니다.</span>`;
            createChart(["데이터 없음"], [1], ["#dddddd"]);
        } else {
            const labels = DREAM_TYPE_ORDER.map(k => DREAM_TYPE_LABELS[k]);
            const data = DREAM_TYPE_ORDER.map(k => {
                const idx = dreamLabels.indexOf(k);
                return idx > -1 ? dreamData[idx] : 0;
            });
            const colors = DREAM_TYPE_ORDER.map(k => DREAM_TYPE_COLORS[k]);
            createChart(labels, data, colors);
            renderResult('가장 많이 꾼 꿈 종류는', labels[data.indexOf(Math.max(...data))]);
        }
        typeTab.classList.add('active');
        emotionTab.classList.remove('active');
    }

    function showEmotion() {
        if (!hasData) {
            resultText.innerHTML = `<span style="color: #888;">${year}년 ${month}월에는 꿈 일기가 없습니다.</span>`;
            createChart(["데이터 없음"], [1], ["#dddddd"]);
        } else {
            const labels = emotionIcons.map((ico, i) => `${ico} ${emotionLabels[i]}`);
            const data = emotionData;
            const colors = labels.map(l => getEmotionColor(l));
            createChart(labels, data, colors);
            renderResult('가장 많이 느낀 감정은', labels[data.indexOf(Math.max(...data))]);
        }
        emotionTab.classList.add('active');
        typeTab.classList.remove('active');
    }

    typeTab.addEventListener('click', showDream);
    emotionTab.addEventListener('click', showEmotion);
    showDream();

    // 드롭다운 연/월 선택기 동작
    const monthText = document.getElementById('monthText');
    const selectorBox = document.getElementById('selectorBox');
    const yearSel = document.getElementById('yearSelect');
    const monthSel = document.getElementById('monthSelect');

    monthText.addEventListener('click', () => {
        selectorBox.classList.toggle('hidden');
    });

    function goToSelected() {
        const y = yearSel.value;
        const m = monthSel.value.padStart(2, '0');
        window.location.href = `/report/${y}${m}/`;
    }

    yearSel.addEventListener('change', goToSelected);
    monthSel.addEventListener('change', goToSelected);

    // 드롭다운 외부 클릭 시 닫기
    document.addEventListener('click', (e) => {
        if (!selectorBox.contains(e.target) && e.target !== monthText) {
            selectorBox.classList.add('hidden');
        }
    });
});
