
import streamlit as st
import pandas as pd
import numpy as np

# --------------------------------
# 기본 설정
# --------------------------------
st.set_page_config(
    page_title="기온과 오존 농도 탐구",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ 기온과 일사량이 높아질수록 대기 중 오존 농도는 정말 증가할까?")
st.caption("데이터 과학 탐구 | 화학·환경화학 | 2025년")

st.markdown("""
이 앱은 실제 기상 및 대기오염 데이터를 이용하여
기온과 일사량이 대기 중 오존 농도에 미치는 영향을 분석합니다.
""")

# --------------------------------
# 사이드바
# --------------------------------
st.sidebar.title("🔍 탐구 메뉴")

menu = st.sidebar.radio(
    "분석할 항목을 선택하세요.",
    [
        "탐구 개요",
        "월별 극값 비교",
        "기온과 오존 분석",
        "일사량과 오존 분석",
        "월별 종합 분석",
        "결론 및 한계"
    ]
)

# --------------------------------
# 사용자가 조사한 데이터
# --------------------------------
extreme_data = pd.DataFrame({
    "월": ["6월", "7월", "8월"],
    "최고 기온 날짜": ["6월 19일", "7월 24일", "8월 24일"],
    "최고 기온(℃)": [33, np.nan, np.nan],
    "최고 기온일 오존 농도": [0.0276, 0.0231, 0.0247],
    "최고 오존 날짜": ["6월 5일", "7월 3일", "8월 16일"],
    "최고 오존 농도": [0.0407, 0.0303, 0.0321]
})

# --------------------------------
# 탐구 개요
# --------------------------------
if menu == "탐구 개요":

    st.header("1. 탐구 주제")

    st.info(
        "기온과 일사량이 높아질수록 대기 중 오존 농도는 정말 증가할까?"
    )

    st.subheader("주제 선정 이유")

    st.write("""
    여름철에는 오존주의보가 자주 발생한다는 점에 주목하였다.
    오존은 햇빛에 의한 광화학 반응을 통해 생성되므로
    기온과 일사량이 오존 농도에 어떤 영향을 미치는지 궁금해졌다.

    이에 실제 기상 및 대기오염 데이터를 활용하여
    기온과 일사량이 높아질수록 오존 농도도 증가하는지
    확인하고자 본 주제를 선정하였다.
    """)

    st.subheader("화학적 배경")

    st.write("""
    대기 중 오존은 질소산화물(NOx)과 휘발성유기화합물(VOCs)이
    햇빛에 의해 일으키는 광화학 반응과 관련이 있다.

    따라서 오존 농도는 기온과 일사량뿐 아니라
    전구물질의 농도, 풍속, 대기 정체 등
    다양한 환경 요인의 영향을 받는다.
    """)

    st.subheader("탐구 과정")

    steps = [
        "공공데이터를 활용하여 기온·일사량·오존 농도 수집",
        "분석에 필요한 변수 선택 및 데이터 정제",
        "산점도와 상관계수를 이용한 관계 분석",
        "회귀분석을 통한 변수 간 관계 파악",
        "월별 비교 및 화학적 원인 해석"
    ]

    for i, step in enumerate(steps, 1):
        st.write(f"**{i}.** {step}")

# --------------------------------
# 월별 극값 비교
# --------------------------------
elif menu == "월별 극값 비교":

    st.header("2. 2025년 여름철 월별 극값 비교")

    st.write(
        "직접 조사한 월별 최고 기온일과 최고 오존 농도일의 자료입니다."
    )

    st.dataframe(
        extreme_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("최고 기온일의 오존 농도와 월별 최고 오존 농도")

    chart_data = extreme_data.set_index("월")[
        ["최고 기온일 오존 농도", "최고 오존 농도"]
    ]

    st.bar_chart(chart_data)

    st.caption("단위: ppm")

    st.subheader("월별 최고 오존 농도")

    st.bar_chart(
        extreme_data,
        x="월",
        y="최고 오존 농도"
    )

    st.subheader("분석 결과")

    st.write("""
    6월 19일에는 기온이 33℃로 가장 높았으며,
    당시 오존 농도는 0.0276ppm이었다.
    그러나 오존 농도는 6월 5일 0.0407ppm으로 가장 높았다.

    7월 24일에는 기온이 가장 높았고,
    당시 오존 농도는 0.0231ppm이었다.
    반면 7월 3일 오존 농도가 0.0303ppm으로 가장 높았다.

    8월 24일에도 기온이 가장 높았지만,
    당시 오존 농도는 0.0247ppm이었다.
    오존 농도는 8월 16일 0.0321ppm으로 가장 높았다.
    """)

    st.warning(
        "세 달 모두 최고 기온일과 최고 오존 농도일이 일치하지 않았다. "
        "다만 극값 날짜 비교만으로 기온과 오존 농도의 전체적인 "
        "상관관계를 판단할 수는 없다."
    )

# --------------------------------
# CSV 데이터 업로드 및 분석
# --------------------------------
else:

    st.header("📊 실제 관측 데이터 분석")

    st.write("""
    기온·오존 농도·일사량이 포함된 CSV 파일을 업로드하세요.
    업로드한 데이터로 산점도, 상관계수, 회귀분석을 수행합니다.
    """)

    uploaded = st.file_uploader(
        "관측 데이터 CSV 파일",
        type=["csv"]
    )

    if uploaded is None:

        st.info(
            "CSV 파일을 업로드하면 해당 분석 메뉴를 이용할 수 있습니다."
        )

    else:

        df = None

        for encoding in ["utf-8-sig", "cp949", "euc-kr"]:

            try:
                uploaded.seek(0)
                df = pd.read_csv(uploaded, encoding=encoding)
                break

            except UnicodeDecodeError:
                continue

        if df is None:

            st.error("CSV 파일을 읽지 못했습니다.")
            st.stop()

        st.subheader("1. 데이터 열 설정")

        columns = list(df.columns)

        def find_column(candidates):

            for candidate in candidates:

                for col in columns:

                    if str(col).strip().lower() == candidate.lower():
                        return col

            return columns[0]

        date_candidates = [
            "날짜", "일시", "측정일시", "date", "datetime"
        ]

        temp_candidates = [
            "기온", "평균기온", "평균 기온",
            "기온(℃)", "temperature", "temp"
        ]

        ozone_candidates = [
            "오존농도", "오존 농도", "오존",
            "o3", "ozone", "o₃"
        ]

        solar_candidates = [
            "일사량", "합계 일사량",
            "일사량(mj/m2)", "solar radiation"
        ]

        c1, c2 = st.columns(2)

        with c1:

            date_col = st.selectbox(
                "날짜 열",
                columns,
                index=columns.index(find_column(date_candidates))
            )

            temp_col = st.selectbox(
                "기온 열",
                columns,
                index=columns.index(find_column(temp_candidates))
            )

        with c2:

            ozone_col = st.selectbox(
                "오존 농도 열",
                columns,
                index=columns.index(find_column(ozone_candidates))
            )

            solar_options = ["없음"] + columns

            solar_default = find_column(solar_candidates)

            solar_col = st.selectbox(
                "일사량 열 (없으면 없음 선택)",
                solar_options,
                index=(
                    solar_options.index(solar_default)
                    if solar_default in columns
                    else 0
                )
            )

        # --------------------------------
        # 데이터 정제
        # --------------------------------

        data = pd.DataFrame()

        data["날짜"] = pd.to_datetime(
            df[date_col].astype(str),
            errors="coerce"
        )

        data["기온"] = pd.to_numeric(
            df[temp_col].astype(str).str.replace(",", ""),
            errors="coerce"
        )

        data["오존농도"] = pd.to_numeric(
            df[ozone_col].astype(str).str.replace(",", ""),
            errors="coerce"
        )

        if solar_col != "없음":

            data["일사량"] = pd.to_numeric(
                df[solar_col].astype(str).str.replace(",", ""),
                errors="coerce"
            )

        data = data.replace([-999, -9999], np.nan)

        data = data.dropna(
            subset=["날짜", "기온", "오존농도"]
        )

        data = data[
            (data["오존농도"] >= 0) &
            (data["기온"].between(-60, 60))
        ]

        if data.empty:

            st.error("유효한 관측 데이터가 없습니다.")
            st.stop()

        data["월"] = data["날짜"].dt.month

        st.success(
            f"데이터 정제 완료! 유효한 관측 자료: {len(data)}개"
        )

        st.subheader("데이터 미리보기")

        st.dataframe(
            data.head(20),
            use_container_width=True
        )

        # --------------------------------
        # 분석 메뉴 1: 기온과 오존
        # --------------------------------

        if menu == "기온과 오존 분석":

            st.header("3. 기온과 오존 농도의 관계")

            correlation = data["기온"].corr(
                data["오존농도"]
            )

            a, b = st.columns(2)

            a.metric(
                "기온과 오존의 상관계수",
                f"{correlation:.4f}"
            )

            if correlation > 0:
                b.metric("관계 방향", "양의 상관관계")

            elif correlation < 0:
                b.metric("관계 방향", "음의 상관관계")

            else:
                b.metric("관계 방향", "상관관계 없음")

            st.subheader("기온과 오존 농도 산점도")

            st.scatter_chart(
                data,
                x="기온",
                y="오존농도"
            )

            st.caption(
                "각 점은 하나의 관측 자료를 나타냅니다. "
                "상관계수는 -1부터 1 사이의 값입니다."
            )

            if (
                len(data) >= 3
                and data["기온"].nunique() >= 2
            ):

                slope, intercept = np.polyfit(
                    data["기온"],
                    data["오존농도"],
                    1
                )

                predicted = (
                    slope * data["기온"] + intercept
                )

                ss_res = (
                    (data["오존농도"] - predicted) ** 2
                ).sum()

                ss_tot = (
                    (data["오존농도"] -
                     data["오존농도"].mean()) ** 2
                ).sum()

                r2 = (
                    1 - ss_res / ss_tot
                    if ss_tot != 0 else np.nan
                )

                st.subheader("회귀분석")

                c1, c2 = st.columns(2)

                c1.metric("회귀 기울기", f"{slope:.6f}")

                c2.metric(
                    "결정계수 R²",
                    f"{r2:.4f}" if pd.notna(r2) else "계산 불가"
                )

                st.write(
                    f"회귀식: 오존 농도 = "
                    f"{slope:.6f} × 기온 + ({intercept:.6f})"
                )

                x_grid = np.linspace(
                    data["기온"].min(),
                    data["기온"].max(),
                    100
                )

                regression = pd.DataFrame({
                    "기온": x_grid,
                    "회귀선": slope * x_grid + intercept
                })

                st.subheader("회귀직선")

                st.line_chart(
                    regression,
                    x="기온",
                    y="회귀선"
                )

        # --------------------------------
        # 분석 메뉴 2: 일사량과 오존
        # --------------------------------

        elif menu == "일사량과 오존 분석":

            st.header("4. 일사량과 오존 농도의 관계")

            if "일사량" not in data.columns:

                st.warning(
                    "일사량 열을 선택한 CSV 파일을 업로드하세요."
                )

            else:

                solar_data = data.dropna(
                    subset=["일사량", "오존농도"]
                )

                if (
                    len(solar_data) < 3
                    or solar_data["일사량"].nunique() < 2
                ):

                    st.warning(
                        "일사량 분석에 필요한 데이터가 부족합니다."
                    )

                else:

                    corr = solar_data["일사량"].corr(
                        solar_data["오존농도"]
                    )

                    st.metric(
                        "일사량과 오존 농도의 상관계수",
                        f"{corr:.4f}"
                    )

                    st.subheader("일사량과 오존 농도 산점도")

                    st.scatter_chart(
                        solar_data,
                        x="일사량",
                        y="오존농도"
                    )

                    st.write("""
                    산점도의 분포와 상관계수를 통해
                    일사량과 오존 농도 사이의 관계를 살펴볼 수 있습니다.
                    """)

        # --------------------------------
        # 분석 메뉴 3: 월별 종합 분석
        # --------------------------------

        elif menu == "월별 종합 분석":

            st.header("5. 월별 종합 분석")

            monthly = data.groupby("월").agg(
                평균기온=("기온", "mean"),
                평균오존=("오존농도", "mean"),
                최고오존=("오존농도", "max"),
                관측수=("오존농도", "count")
            )

            st.subheader("월별 통계표")

            st.dataframe(
                monthly.round(4),
                use_container_width=True
            )

            st.subheader("월별 평균 기온")

            st.bar_chart(monthly, y="평균기온")

            st.subheader("월별 평균 오존 농도")

            st.bar_chart(monthly, y="평균오존")

            st.subheader("월별 최고 오존 농도")

            st.bar_chart(monthly, y="최고오존")

            st.subheader("날짜별 기온 변화")

            temperature_chart = data.sort_values("날짜").set_index("날짜")

            st.line_chart(
                temperature_chart["기온"]
            )

            st.subheader("날짜별 오존 농도 변화")

            st.line_chart(
                temperature_chart["오존농도"]
            )

        # --------------------------------
        # 결론 및 한계
        # --------------------------------

        elif menu == "결론 및 한계":

            st.header("6. 탐구 결과 해석")

            st.write("""
            데이터 분석 결과를 바탕으로 기온과 일사량이
            오존 농도에 미치는 영향을 해석합니다.
            """)

            if len(data) >= 3:

                corr = data["기온"].corr(
                    data["오존농도"]
                )

                st.metric(
                    "기온과 오존의 상관계수",
                    f"{corr:.4f}"
                )

                if corr > 0:
                    st.write(
                        "기온과 오존 농도 사이에 양의 상관관계가 관찰됩니다."
                    )

                elif corr < 0:
                    st.write(
                        "기온과 오존 농도 사이에 음의 상관관계가 관찰됩니다."
                    )

                else:
                    st.write(
                        "뚜렷한 선형 상관관계가 관찰되지 않습니다."
                    )

            st.warning("""
            [탐구의 한계]

            1. 기온과 오존 농도의 상관관계가 인과관계를 의미하지는 않는다.
            2. 일사량, 풍속, 질소산화물, 휘발성유기화합물 등의
               영향을 충분히 통제하지 못할 수 있다.
            3. 관측 기간과 관측소의 위치에 따라 결과가 달라질 수 있다.
            """)

            st.subheader("후속 탐구")

            st.write("""
            1. 일사량과 풍속을 추가한 다중회귀분석
            2. 질소산화물과 휘발성유기화합물의 영향 분석
            3. 여러 해의 데이터를 활용한 계절별 비교
            """)

        # --------------------------------
        # 데이터 다운로드
        # --------------------------------

        st.divider()

        st.download_button(
            "📥 정제된 데이터 다운로드",
            data.to_csv(index=False).encode("utf-8-sig"),
            file_name="ozone_analysis.csv",
            mime="text/csv"
        )

# --------------------------------
# 하단
# --------------------------------

st.divider()

st.caption(
    "데이터 과학 탐구 | 기온·일사량과 대기 중 오존 농도의 관계"
)
