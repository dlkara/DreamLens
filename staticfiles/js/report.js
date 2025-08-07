document.addEventListener("DOMContentLoaded", function () {
    // ========================
    // 탭 전환 기능
    // ========================
    document.querySelectorAll(".tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const target = tab.getAttribute("data-target");
            document.querySelectorAll(".chart-box").forEach(box => box.classList.add("hidden"));
            const targetBoxId = target === "emotion" ? "emotionChartBox" : "dreamChartBox";
            document.getElementById(targetBoxId).classList.remove("hidden");

            // 차트 설명 텍스트 변경
            const desc = document.getElementById("chartDesc");
            if (!hasData) {
                desc.innerHTML = `${currentYear}년 ${currentMonth}월에는 꿈 일기가 없습니다.`;
                return;
            }

            if (target === "emotion") {
                const maxIndex = emotionData.indexOf(Math.max(...emotionData));
                const label = `${emotionIcons[maxIndex]} ${emotionLabels[maxIndex]}`;
                desc.innerHTML = `가장 많이 느낀 감정은 <span id="resultLabel">${label}</span>이네요!`;
            } else {
                const maxIndex = dreamData.indexOf(Math.max(...dreamData));
                const mapped = dreamLabelMap[dreamLabels[maxIndex]] || dreamLabels[maxIndex];
                desc.innerHTML = `가장 많이 꾼 꿈 종류는 <span id="resultLabel">${mapped}</span>이네요!`;
            }
        });
    });

    // ========================
    // 월 선택 드롭다운 열기/닫기
    // ========================
    const monthText = document.getElementById("monthText");
    const selectorBox = document.getElementById("selectorBox");

    monthText?.addEventListener("click", () => {
        selectorBox.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
        if (!selectorBox.contains(e.target) && e.target !== monthText) {
            selectorBox.classList.add("hidden");
        }
    });

    // ========================
    // 이동 버튼 처리
    // ========================
    document.getElementById("moveBtn").addEventListener("click", () => {
        const year = document.getElementById("yearSelect").value;
        const month = document.getElementById("monthSelect").value;
        const yyyymm = year + String(month).padStart(2, "0");
        window.location.href = `/report/${yyyymm}`;
    });

    // ========================
    // 색상 정의
    // ========================
    const pastelColors = [
        '#A5DEE5', '#BFFDAB', '#FAE88E', '#F8C3CD',
        '#CBCBFF', '#92F4BB', '#FFC8AF'
    ];
    const vividColors = [
        '#FF6B6B', '#4ECDC4', '#FFB400', '#1A535C',
        '#4EBBFF', '#6A0572', '#3A86FF', '#8338EC',
        '#FF006E', '#4C4C4C'
    ];
    const dreamColorMap = {
        "길몽": "#BFFDAB",
        "흉몽": "#F8C3CD",
        "일반몽": "#C0C0C0"
    };
    const dreamLabelMap = {
        good: "길몽",
        normal: "일반몽",
        bad: "흉몽"
    };
    const labelOrder = ["길몽", "일반몽", "흉몽"];

    // ========================
    // 꿈 종류 분석 데이터 가공
    // ========================
    let labelDataPairs = dreamLabels.map((label, i) => {
        const mapped = dreamLabelMap[label] || label;
        return {
            label: mapped,
            value: dreamData[i],
            color: dreamColorMap[mapped] || "#ccc"
        };
    });

    labelDataPairs.sort((a, b) => {
        return labelOrder.indexOf(a.label) - labelOrder.indexOf(b.label);
    });

    const sortedDreamLabels = labelDataPairs.map(item => item.label);
    const sortedDreamData = labelDataPairs.map(item => item.value);
    const sortedDreamColors = labelDataPairs.map(item => item.color);

    // ========================
    // 꿈 종류 분석 차트 (기본 표시)
    // ========================
    const dreamChartCtx = document.getElementById("dreamChart").getContext("2d");
    new Chart(dreamChartCtx, {
        type: "pie",
        data: {
            labels: hasData ? sortedDreamLabels : [],
            datasets: [{
                data: hasData ? sortedDreamData : [1],
                backgroundColor: hasData ? sortedDreamColors : ["#ddd"],
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: hasData,
                    position: "bottom"
                },
                tooltip: {
                    enabled: hasData
                }
            },
        },
    });

    // ========================
    // 감정 분석 차트
    // ========================
    const emotionChartCtx = document.getElementById("emotionChart").getContext("2d");
    new Chart(emotionChartCtx, {
        type: "pie",
        data: {
            labels: hasData ? emotionLabels.map((label, i) => `${emotionIcons[i]} ${label}`) : [],
            datasets: [{
                data: hasData ? emotionData : [1],
                backgroundColor: hasData ? pastelColors : ["#ddd"],
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: hasData,
                    position: "bottom"
                },
                tooltip: {
                    enabled: hasData
                }
            },
        },
    });

    // ========================
    // 워드 클라우드
    // ========================
    const wordCloudArea = document.getElementById("wordCloudArea");

    if (hasData && keywords.length > 0) {
        const wordEntries = keywords.map(([text, weight]) => [text, weight]);
        wordCloudArea.classList.remove("nodata");

        WordCloud(wordCloudArea, {
            list: wordEntries,
            gridSize: 8,
            weightFactor: 12,
            fontFamily: 'Arial',
            color: () => vividColors[Math.floor(Math.random() * vividColors.length)],
            rotateRatio: 0,
            backgroundColor: "#fff"
        });
    } else {
        wordCloudArea.classList.add("nodata");

        WordCloud(wordCloudArea, {
            list: [],
            backgroundColor: "#ddd"
        });
    }

    // ========================
    // 초기 설명 문구 설정
    // ========================
    const chartDesc = document.getElementById("chartDesc");

    if (!hasData) {
        chartDesc.classList.add("no-data");
        chartDesc.innerHTML = `${currentYear}년 ${currentMonth}월에는 꿈 일기가 없습니다.`;
    } else {
        chartDesc.classList.remove("no-data");
        const maxIndex = dreamData.indexOf(Math.max(...dreamData));
        const mapped = dreamLabelMap[dreamLabels[maxIndex]] || dreamLabels[maxIndex];
        chartDesc.innerHTML = `가장 많이 꾼 꿈 종류는 <span id="resultLabel">${mapped}</span>이네요!`;
    }

});
