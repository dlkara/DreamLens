document.addEventListener("DOMContentLoaded", function () {
    console.log('🚀 Report.js 로드 시작');
    console.log('📊 데이터 확인:', { hasData, dreamData, emotionData, keywords });

    // ========================
    // 중복 실행 방지
    // ========================
    if (window.reportJsLoaded) {
        console.warn('⚠️ Report.js가 이미 로드됨. 중복 실행 방지');
        return;
    }
    window.reportJsLoaded = true;

    // ========================
    // 탭 전환 기능
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
            updateChartDescription(target);
        });
    });

    // ========================
    // 월 선택 드롭다운 토글 (수정된 부분)
    // ========================
    const monthDisplay = document.querySelector(".month-display");
    const selectorBox = document.getElementById("selectorBox");
    const dropdownIcon = document.querySelector(".dropdown-icon");

    console.log('🔍 드롭다운 요소 확인:', {
        monthDisplay: !!monthDisplay,
        selectorBox: !!selectorBox,
        dropdownIcon: !!dropdownIcon
    });

    if (monthDisplay && selectorBox) {
        // 기존 이벤트 리스너 제거 (중복 방지)
        monthDisplay.removeEventListener("click", toggleDropdown);

        // 새 이벤트 리스너 등록
        monthDisplay.addEventListener("click", toggleDropdown);

        console.log('✅ 드롭다운 이벤트 리스너 등록 완료');

        // 외부 클릭시 드롭다운 닫기
        document.addEventListener("click", (e) => {
            if (!selectorBox.contains(e.target) && !monthDisplay.contains(e.target)) {
                closeDropdown();
            }
        });
    } else {
        console.error('❌ 드롭다운 요소를 찾을 수 없음:', {
            monthDisplay: !!monthDisplay,
            selectorBox: !!selectorBox
        });
    }

    // 드롭다운 토글 함수
    function toggleDropdown() {
        console.log('🎯 드롭다운 토글 실행');
        console.log('현재 상태:', {
            selectorBoxHidden: selectorBox.classList.contains('hidden'),
            monthDisplayActive: monthDisplay.classList.contains('active')
        });

        const isHidden = selectorBox.classList.contains('hidden');

        if (isHidden) {
            // 드롭다운 열기
            selectorBox.classList.remove("hidden");
            monthDisplay.classList.add("active");
            console.log('📖 드롭다운 열림');
        } else {
            // 드롭다운 닫기
            selectorBox.classList.add("hidden");
            monthDisplay.classList.remove("active");
            console.log('📕 드롭다운 닫힘');
        }
    }

    // 드롭다운 닫기 함수
    function closeDropdown() {
        if (selectorBox && monthDisplay) {
            selectorBox.classList.add("hidden");
            monthDisplay.classList.remove("active");
        }
    }

    // ========================
    // 이동 버튼 처리
    // ========================
    const moveBtn = document.getElementById("moveBtn");
    if (moveBtn) {
        moveBtn.addEventListener("click", () => {
            const yearSelect = document.getElementById("yearSelect");
            const monthSelect = document.getElementById("monthSelect");

            if (yearSelect && monthSelect) {
                const year = yearSelect.value;
                const month = monthSelect.value;
                const yyyymm = year + String(month).padStart(2, "0");
                console.log('🚀 페이지 이동:', yyyymm);
                window.location.href = `/report/${yyyymm}`;
            } else {
                console.error('❌ 년도/월 선택 요소를 찾을 수 없음');
            }
        });
    }

    // ========================
    // 차트 설명 업데이트 함수
    // ========================
    function updateChartDescription(target) {
        const resultLabel = document.getElementById("resultLabel");

        if (!resultLabel) return;

        if (!hasData) {
            resultLabel.innerHTML = `${currentYear}년 ${currentMonth}월에는 꿈 일기가 없습니다.`;
            return;
        }

        if (target === "emotion" && emotionData && emotionData.length > 0) {
            const maxIndex = emotionData.indexOf(Math.max(...emotionData));
            if (maxIndex !== -1 && emotionLabels[maxIndex] && emotionIcons[maxIndex]) {
                const label = `${emotionIcons[maxIndex]} ${emotionLabels[maxIndex]}`;
                resultLabel.innerHTML = `가장 많이 느낀 감정은 ${label}이네요!`;
            }
        } else if (target === "dream" && dreamData && dreamData.length > 0) {
            const maxIndex = dreamData.indexOf(Math.max(...dreamData));
            if (maxIndex !== -1 && dreamLabels[maxIndex]) {
                const mapped = dreamLabelMap[dreamLabels[maxIndex]] || dreamLabels[maxIndex];
                resultLabel.innerHTML = `가장 많이 꾼 꿈 종류는 ${mapped}이네요!`;
            }
        }
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
        "길몽": "#22c55e",      // 초록색
        "흉몽": "#ef4444",      // 빨간색
        "일반몽": "#9ca3af"     // 회색
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

            // WordCloud 라이브러리 로딩 대기
            const initWordCloud = () => {
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
                    setTimeout(initWordCloud, 100);
                }
            };

            initWordCloud();
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

    console.log('🎨 캔버스 상태:', {
        dreamChart: !!document.getElementById("dreamChart"),
        emotionChart: !!document.getElementById("emotionChart"),
        wordCloudArea: !!document.getElementById("wordCloudArea")
    });

    const tabButtons = document.querySelectorAll(".tab-btn");
    console.log('🏷️ 탭 버튼:', tabButtons.length, '개 발견');

    if (tabButtons.length === 0) {
        console.error('❌ 탭 버튼을 찾을 수 없습니다. HTML 구조를 확인하세요.');
    }
});