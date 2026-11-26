
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="기온과 오존 농도 탐구",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ 기온과 일사량이 높아질수록 대기 중 오존 농도는 정말 증가할까?")
st.caption("데이터 과학 탐구 | 화학·환경화학")

st.sidebar.title("🌱 탐구 메뉴")

menu = st.sidebar.radio(
    "메뉴 선택",
    ["탐구 개요", "월별 데이터 분석", "전체 데이터 분석", "결론 및 한계"]
)

data = pd.DataFrame({
    "월": ["6월", "7월", "8월"],
    "최고 기온 날짜": ["6월 19일", "7월 24일", "8월 24일"],
    "최고 기온(℃)": [33, np.nan, np.nan],
    "최고 기온일 오존 농도": [0.0276, 0.0231, 0.0247],
    "최고 오존 날짜": ["6월 5일", "7월 3일", "8월 16일"],
    "최고 오존 농도": [0.0407, 0.0303, 0.0321]
})

# 1. 탐구 개요
if menu == "탐구 개요":

    st.header("1. 탐구 주제")

    st.info(
        "기온과 일사량이 높아질수록 대기 중 오존 농도는 정말 증가할까?"
    )

    st.subheader("주제 선정 이유")

    st.write("""
    여름철에는 오존주의보가 자주 발생한다는 점에 주목하였다.
    오존은 햇빛에 의한 광화학 반응으로 생성되는 물질이므로
    기온과 일사량이 오존 농도에 어떤 영향을 미치는지 궁금해졌다.

    이에 실제 기상 및 대기오염 데이터를 활용하여
    기온과 일사량이 높아질수록 오존 농도도 증가하는지
    확인하고자 본 주제를 선정하였다.
    """)

    st.subheader("화학적 배경")

    st.write("""
    대기 중 오존은 질소산화물(NOx)과 휘발성유기화합물(VOCs)이
    햇빛에 의해 일으키는 광화학 반응과 관련이 있다.

    따라서 오존 농도는 기온뿐 아니라 일사량,
    전구물질의 농도 등 여러 환경 요인의 영향을 받는다.
    """)

    c1, c2, c3 = st.columns(3)
    c1.metric("탐구 기간", "2025년 6~8월")
    c2.metric("분석 월", "3개월")
    c3.metric("핵심 변수", "기온·오존·일사량")

# 2. 월별 데이터 분석
elif menu == "월별 데이터 분석":

    st.header("2. 월별 데이터 분석")

    st.subheader("월별 관측 결과")

    st.dataframe(data, use_container_width=True, hide_index=True)

    st.caption("7월과 8월의 최고 기온 수치는 아직 입력되지 않았습니다.")

    st.subheader("월별 최고 오존 농도")

    st.bar_chart(
        data,
        x="월",
        y="최고 오존 농도"
    )

    st.subheader("최고 기온일과 최고 오존 농도 비교")

    compare = data.set_index("월")[
        ["최고 기온일 오존 농도", "최고 오존 농도"]
    ]

    st.bar_chart(compare)

    st.subheader("분석 결과")

    st.write("""
    6월에는 19일 기온이 33℃로 가장 높았으며,
    당시 오존 농도는 0.0276ppm이었다.
    하지만 오존 농도는 6월 5일 0.0407ppm으로 가장 높았다.

    7월에는 24일 기온이 가장 높았고,
    해당일 오존 농도는 0.0231ppm이었다.
    반면 7월 3일 오존 농도가 0.0303ppm으로 가장 높았다.

    8월에도 24일 기온이 가장 높았고,
    해당일 오존 농도는 0.0247ppm이었다.
    그러나 8월 16일 오존 농도가 0.0321ppm으로 가장 높았다.
    """)

    st.success("""
    세 달 모두 최고 기온일과 최고 오존 농도일이
    서로 일치하지 않았다.
    """)

# 3. 전체 데이터 분석
elif menu == "전체 데이터 분석":

    st.header("3. 전체 데이터 분석")

    st.write("""
    기온과 오존 농도가 포함된 CSV 파일을 업로드하면
    상관관계와 회귀분석을 진행합니다.
    """)

    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded is not None:

        try:
            df = None

            for encoding in ["utf-8-sig", "cp949", "euc-kr"]:
                try:
                    uploaded.seek(0)
                    df = pd.read_csv(uploaded, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                st.error("CSV 파일을 읽을 수 없습니다.")
                st.stop()

            aliases = {
                "일시": "날짜",
                "측정일시": "날짜",
                "기온(℃)": "기온",
                "평균기온": "기온",
                "오존": "오존농도",
                "오존 농도": "오존농도",
                "O3": "오존농도",
                "O₃": "오존농도",
                "일사": "일사량"
            }

            df = df.rename(columns=aliases)

            required = ["날짜", "기온", "오존농도"]

            if not all(col in df.columns for col in required):
                st.error("날짜, 기온, 오존농도 열이 필요합니다.")
                st.write("현재 CSV 열:", list(df.columns))
                st.stop()

            df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

            for col in ["기온", "오존농도", "일사량"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.replace([-999, -9999], np.nan)

            df = df.dropna(
                subset=["날짜", "기온", "오존농도"]
            )

            if len(df) < 3:
                st.error("분석할 데이터가 부족합니다.")
                st.stop()

            st.success(f"유효한 관측 자료 {len(df)}개")

            st.subheader("데이터 미리보기")
            st.dataframe(df.head(30), use_container_width=True)

            # 기온과 오존
            st.subheader("기온과 오존 농도의 관계")

            corr = df["기온"].corr(df["오존농도"])

            a, b = st.columns(2)
            a.metric("상관계수", f"{corr:.3f}")

            if corr > 0:
                b.write("양의 상관관계")
            elif corr < 0:
                b.write("음의 상관관계")
            else:
                b.write("상관관계가 거의 없음")

            st.scatter_chart(
                df,
                x="기온",
                y="오존농도"
            )

            # 회귀분석
            st.subheader("기온에 따른 회귀분석")

            slope, intercept = np.polyfit(
                df["기온"],
                df["오존농도"],
                1
            )

            predicted = slope * df["기온"] + intercept

            ss_res = ((df["오존농도"] - predicted) ** 2).sum()
            ss_tot = ((df["오존농도"] - df["오존농도"].mean()) ** 2).sum()

            r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan

            c1, c2 = st.columns(2)

            c1.metric("회귀 기울기", f"{slope:.6f}")
            c2.metric(
                "결정계수 R²",
                f"{r2:.3f}" if pd.notna(r2) else "계산 불가"
            )

            st.write(
                f"회귀식: 오존 농도 = {slope:.6f} × 기온 + ({intercept:.6f})"
            )

            # 일사량
            if "일사량" in df.columns:

                sun = df.dropna(subset=["일사량", "오존농도"])

                if len(sun) >= 3 and sun["일사량"].nunique() > 1:

                    st.subheader("일사량과 오존 농도의 관계")

                    sun_corr = sun["일사량"].corr(sun["오존농도"])

                    st.metric("일사량과 오존 상관계수", f"{sun_corr:.3f}")

                    st.scatter_chart(
                        sun,
                        x="일사량",
                        y="오존농도"
                    )

            # 월별 분석
            st.subheader("월별 평균 데이터")

            df["월"] = df["날짜"].dt.month

            monthly = df.groupby("월").agg(
                평균기온=("기온", "mean"),
                평균오존=("오존농도", "mean"),
                최고오존=("오존농도", "max"),
                관측수=("오존농도", "count")
            )

            st.dataframe(monthly, use_container_width=True)

            st.subheader("월별 평균 오존 농도")

            st.bar_chart(monthly, y="평균오존")

            st.download_button(
                "분석 데이터 다운로드",
                df.to_csv(index=False).encode("utf-8-sig"),
                file_name="ozone_analysis.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {e}")

    else:
        st.info("CSV 파일을 업로드하면 분석이 시작됩니다.")

# 4. 결론 및 한계
elif menu == "결론 및 한계":

    st.header("4. 탐구 결론")

    st.write("""
    2025년 6~8월의 월별 최고 기온일과 최고 오존 농도일을
    비교한 결과, 세 달 모두 두 날짜가 서로 일치하지 않았다.

    이를 통해 기온이 가장 높은 날에 오존 농도도
    반드시 가장 높게 나타나는 것은 아니라는 점을 확인했다.

    오존 농도는 기온뿐 아니라 일사량,
    질소산화물과 휘발성유기화합물 등
    여러 환경 요인의 영향을 받을 수 있다.
    """)

    st.header("5. 탐구의 한계")

    st.warning("""
    - 2025년 6~8월의 3개월 자료만 분석했다.
    - 각 달의 극값 비교만으로 전체 상관관계를 판단할 수 없다.
    - 일사량과 다른 대기오염물질의 영향을 충분히 통제하지 못했다.
    - 관측소의 위치와 관측 시간 차이가 결과에 영향을 줄 수 있다.
    """)

    st.header("6. 후속 탐구")

    st.write("""
    1. 시간별 기온과 오존 농도를 비교한다.
    2. 일사량과 풍속 등의 변수를 추가한다.
    3. 질소산화물과 휘발성유기화합물까지 고려한 다중회귀분석을 수행한다.
    """)

st.divider()
st.caption("데이터 과학 탐구 | 기온·일사량과 대기 중 오존 농도의 관계")
