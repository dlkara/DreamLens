document.addEventListener("DOMContentLoaded", function () {
    // 탭 전환
    document.querySelectorAll(".tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const target = tab.getAttribute("data-target");
            document.querySelectorAll(".chart-box").forEach(box => box.classList.add("hidden"));
            const targetBoxId = target === "emotion" ? "emotionChartBox" : "dreamChartBox";
            document.getElementById(targetBoxId).classList.remove("hidden");
        });
    });

    // 드롭다운 열고 닫기
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

    // 이동 버튼
    document.getElementById("moveBtn").addEventListener("click", () => {
        const year = document.getElementById("yearSelect").value;
        const month = document.getElementById("monthSelect").value;
        const yyyymm = year + String(month).padStart(2, "0");
        window.location.href = `/report/${yyyymm}`;
    });

    // 색상
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
        "길몽": "#BFFDAB",    // 연두
        "흉몽": "#F8C3CD",    // 붉은색
        "일반몽": "#C0C0C0"   // 회색
    };

    // 꿈 종류 라벨 매핑 및 정렬
    const dreamLabelMap = {
        good: "길몽",
        normal: "일반몽",
        bad: "흉몽"
    };
    const labelOrder = ["길몽", "일반몽", "흉몽"];

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

    // 차트 공통 옵션
    const disabledOptions = {
        responsive: true,
        events: [],
        plugins: {
            legend: {display: false},
            tooltip: {enabled: false}
        },
        interaction: {
            mode: null
        },
        hover: {mode: null}
    };

    // 꿈 종류 분석 차트
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
        options: hasData ? {
            responsive: true,
            plugins: {
                legend: {position: "bottom"}
            }
        } : disabledOptions
    });

    // 감정 분석 차트
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
        options: hasData ? {
            responsive: true,
            plugins: {
                legend: {position: "bottom"}
            }
        } : disabledOptions
    });

    // 워드 클라우드
    const wordCloudArea = document.getElementById("wordCloudArea");
    wordCloudArea.classList.remove("nodata");   // 배경색 class 초기화

    if (hasData && keywords.length > 0) {
        const wordEntries = keywords.map(([text, weight]) => [text, weight]);
        WordCloud(wordCloudArea, {
            list: wordEntries,
            gridSize: 8,
            weightFactor: 12,
            fontFamily: 'Arial',
            color: () => vividColors[Math.floor(Math.random() * vividColors.length)],
            rotateRatio: 0,
            backgroundColor: "#fff"
        });
    } else {    // 데이터가 없으면 배경색을 회색으로 변경
        wordCloudArea.classList.add("nodata");

        WordCloud(wordCloudArea, {
            list: [], // 단어 없음
            backgroundColor: "#ddd"
        });
    }

});
