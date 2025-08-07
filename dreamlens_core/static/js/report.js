document.addEventListener("DOMContentLoaded", function () {
    console.log('🚀 Report.js 로드 시작');
    console.log('📊 데이터 확인:', { hasData, dreamData, emotionData, keywords });

    // ========================
    // 탭 전환 기능 (새로운 HTML 구조에 맞게 수정)
    // ========================
    document.querySelectorAll(".tab-btn").forEach(tab => {
        tab.addEventListener("click", () => {
            console.log('🎯 탭 클릭:', tab.getAttribute("data-target"));

            // 모든 탭에서 active 제거
            document.querySelectorAll(".tab-btn").forEach(t => t.classList.remove("active"));
            // 현재 탭에 active 추가
            tab.classList.add("active");

            const target = tab.getAttribute("data-target");

            // 모든 차트 박스 숨기기
            document.querySelectorAll(".chart-box").forEach(box => box.classList.add("hidden"));

            // 선택된 차트 박스 표시
            const targetBoxId = target === "emotion" ? "emotionChartBox" : "dreamChartBox";
            const targetBox = document.getElementById(targetBoxId);

            if (targetBox) {
                targetBox.classList.remove("hidden");
                console.log('📈 차트 표시:', targetBoxId);
            } else {
                console.error('❌ 차트 박스를 찾을 수 없음:', targetBoxId);
            }

            // 차트 설명 텍스트 변경
            const resultLabel = document.getElementById("resultLabel");
            if (!hasData) {
                if (resultLabel) {
                    resultLabel.innerHTML = `${currentYear}년 ${currentMonth}월에는 꿈 일기가 없습니다.`;
                }
                return;
            }

            if (target === "emotion" && emotionData && emotionData.length > 0) {
                const maxIndex = emotionData.indexOf(Math.max(...emotionData));
                if (maxIndex !== -1 && emotionLabels[maxIndex] && emotionIcons[maxIndex]) {
                    const label = `${emotionIcons[maxIndex]} ${emotionLabels[maxIndex]}`;
                    if (resultLabel) {
                        resultLabel.innerHTML = `가장 많이 느낀 감정은 ${label}이네요!`;
                    }
                }
            } else if (target === "dream" && dreamData && dreamData.length > 0) {
                const maxIndex = dreamData.indexOf(Math.max(...dreamData));
                if (maxIndex !== -1 && dreamLabels[maxIndex]) {
                    const mapped = dreamLabelMap[dreamLabels[maxIndex]] || dreamLabels[maxIndex];
                    if (resultLabel) {
                        resultLabel.innerHTML = `가장 많이 꾼 꿈 종류는 ${mapped}이네요!`;
                    }
                }
            }
        });
    });

    // ========================
    // 월 선택 드롭다운 열기/닫기 (새로운 HTML 구조에 맞게 수정)
    // ========================
    const monthDisplay = document.querySelector(".month-display");
    const selectorBox = document.getElementById("selectorBox");
    const dropdownIcon = document.querySelector(".dropdown-icon");

    if (monthDisplay && selectorBox) {
        monthDisplay.addEventListener("click", () => {
            console.log('📅 월 선택 드롭다운 토글');
            selectorBox.classList.toggle("hidden");
            monthDisplay.classList.toggle("active");
        });

        // 외부 클릭시 드롭다운 닫기
        document.addEventListener("click", (e) => {
            if (!selectorBox.contains(e.target) && !monthDisplay.contains(e.target)) {
                selectorBox.classList.add("hidden");
                monthDisplay.classList.remove("active");
            }
        });
    }

    // ========================
    // 이동 버튼 처리
    // ========================
    const moveBtn = document.getElementById("moveBtn");
    if (moveBtn) {
        moveBtn.addEventListener("click", () => {
            const year = document.getElementById("yearSelect").value;
            const month = document.getElementById("monthSelect").value;
            const yyyymm = year + String(month).padStart(2, "0");
            console.log('🚀 페이지 이동:', yyyymm);
            window.location.href = `/report/${yyyymm}`;
        });
    }

    // ========================
    // 색상 정의
    // ========================
    const pastelColors = [
        '#A5DEE5', '#BFFDAB', '#FAE88E', '#F8C3CD',
        '#CBCBFF', '#92F4BB', '#FFC8AF', '#DDA0DD',
        '#98FB98', '#F0E68C', '#FFB6C1', '#87CEEB'
    ];

    const vividColors = [
        '#FF6B6B', '#4ECDC4', '#FFB400', '#1A535C',
        '#4EBBFF', '#6A0572', '#3A86FF', '#8338EC',
        '#FF006E', '#4C4C4C'
    ];

    const dreamColorMap = {
        "길몽": "#22c55e",      // 초록색 (캘린더와 동일)
        "흉몽": "#ef4444",      // 빨간색 (캘린더와 동일)
        "일반몽": "#9ca3af"     // 회색 (캘린더와 동일)
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
    let sortedDreamLabels = [];
    let sortedDreamData = [];
    let sortedDreamColors = [];

    if (hasData && dreamLabels && dreamData) {
        let labelDataPairs = dreamLabels.map((label, i) => {
            const mapped = dreamLabelMap[label] || label;
            return {
                label: mapped,
                value: dreamData[i],
                color: dreamColorMap[mapped] || "#ccc"
            };
        });

        // 정렬
        labelDataPairs.sort((a, b) => {
            return labelOrder.indexOf(a.label) - labelOrder.indexOf(b.label);
        });

        sortedDreamLabels = labelDataPairs.map(item => item.label);
        sortedDreamData = labelDataPairs.map(item => item.value);
        sortedDreamColors = labelDataPairs.map(item => item.color);
    }

    // ========================
    // 꿈 종류 분석 차트
    // ========================
    const dreamChartCanvas = document.getElementById("dreamChart");
    if (dreamChartCanvas) {
        const dreamChartCtx = dreamChartCanvas.getContext("2d");

        new Chart(dreamChartCtx, {
            type: "pie",
            data: {
                labels: hasData ? sortedDreamLabels : ["데이터 없음"],
                datasets: [{
                    data: hasData ? sortedDreamData : [1],
                    backgroundColor: hasData ? sortedDreamColors : ["#e5e7eb"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: hasData,
                        position: "bottom",
                        labels: {
                            padding: 20,
                            font: {
                                size: 14,
                                family: "'Noto Sans KR', sans-serif"
                            }
                        }
                    },
                    tooltip: {
                        enabled: hasData,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        cornerRadius: 8
                    }
                },
            },
        });
        console.log('📊 꿈 종류 차트 생성 완료');
    }

    // ========================
    // 감정 분석 차트
    // ========================
    const emotionChartCanvas = document.getElementById("emotionChart");
    if (emotionChartCanvas) {
        const emotionChartCtx = emotionChartCanvas.getContext("2d");

        new Chart(emotionChartCtx, {
            type: "pie",
            data: {
                labels: hasData && emotionLabels && emotionIcons ?
                    emotionLabels.map((label, i) => `${emotionIcons[i] || '💭'} ${label}`) :
                    ["데이터 없음"],
                datasets: [{
                    data: hasData && emotionData ? emotionData : [1],
                    backgroundColor: hasData ? pastelColors : ["#e5e7eb"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: hasData,
                        position: "bottom",
                        labels: {
                            padding: 20,
                            font: {
                                size: 14,
                                family: "'Noto Sans KR', sans-serif"
                            }
                        }
                    },
                    tooltip: {
                        enabled: hasData,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        cornerRadius: 8
                    }
                },
            },
        });
        console.log('💖 감정 차트 생성 완료');
    }

    // ========================
    // 워드 클라우드
    // ========================
    const wordCloudArea = document.getElementById("wordCloudArea");

    if (wordCloudArea) {
        if (hasData && keywords && keywords.length > 0) {
            const wordEntries = keywords.map(([text, weight]) => [text, Math.max(weight, 10)]);
            wordCloudArea.classList.remove("nodata");

            // WordCloud 라이브러리가 로드되었는지 확인
            if (typeof WordCloud !== 'undefined') {
                try {
                    WordCloud(wordCloudArea, {
                        list: wordEntries,
                        gridSize: Math.round(16 * wordCloudArea.offsetWidth / 1024),
                        weightFactor: function (size) {
                            return Math.pow(size, 1.3) * wordCloudArea.offsetWidth / 1024;
                        },
                        fontFamily: "'Noto Sans KR', Arial, sans-serif",
                        color: function () {
                            return vividColors[Math.floor(Math.random() * vividColors.length)];
                        },
                        rotateRatio: 0.1,
                        backgroundColor: "transparent",
                        drawOutOfBound: false
                    });
                    console.log('☁️ 워드클라우드 생성 완료');
                } catch (error) {
                    console.error('❌ 워드클라우드 생성 오류:', error);
                    wordCloudArea.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">워드클라우드 생성 중 오류가 발생했습니다.</div>';
                }
            } else {
                console.warn('⚠️ WordCloud 라이브러리가 로드되지 않음');
                wordCloudArea.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">워드클라우드 라이브러리 로딩 중...</div>';
            }
        } else {
            wordCloudArea.classList.add("nodata");
            wordCloudArea.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999; font-style: italic;">표시할 키워드가 없습니다</div>';
            console.log('📝 워드클라우드 데이터 없음');
        }
    }

    // ========================
    // 초기 설명 문구 설정
    // ========================
    const resultLabel = document.getElementById("resultLabel");

    if (resultLabel) {
        if (!hasData) {
            resultLabel.innerHTML = `${currentYear}년 ${currentMonth}월에는 꿈 일기가 없습니다.`;
        } else if (dreamData && dreamData.length > 0) {
            const maxIndex = dreamData.indexOf(Math.max(...dreamData));
            if (maxIndex !== -1 && dreamLabels && dreamLabels[maxIndex]) {
                const mapped = dreamLabelMap[dreamLabels[maxIndex]] || dreamLabels[maxIndex];
                resultLabel.innerHTML = `가장 많이 꾼 꿈 종류는 ${mapped}이네요!`;
            }
        }
    }

    // ========================
    // 데이터 검증 및 디버깅
    // ========================
    console.log('✅ Report.js 초기화 완료');
    console.log('📊 최종 데이터 상태:', {
        hasData,
        dreamLabels: dreamLabels?.length || 0,
        dreamData: dreamData?.length || 0,
        emotionLabels: emotionLabels?.length || 0,
        emotionData: emotionData?.length || 0,
        keywords: keywords?.length || 0
    });

    // 차트 캔버스 확인
    console.log('🎨 캔버스 상태:', {
        dreamChart: !!document.getElementById("dreamChart"),
        emotionChart: !!document.getElementById("emotionChart"),
        wordCloudArea: !!document.getElementById("wordCloudArea")
    });

    // 탭 버튼 확인
    const tabButtons = document.querySelectorAll(".tab-btn");
    console.log('🏷️ 탭 버튼:', tabButtons.length, '개 발견');

    if (tabButtons.length === 0) {
        console.error('❌ 탭 버튼을 찾을 수 없습니다. HTML 구조를 확인하세요.');
    }
});