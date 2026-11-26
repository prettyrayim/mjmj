
import streamlit as st
import pandas as pd
import numpy as np
import requests
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="오존 농도 데이터 분석",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ 기온·일사량과 오존 농도의 관계")
st.caption("2025년 6월 ~ 8월 | 대기오염 데이터와 과거 기상 자료 분석")

DATA_DIR = Path(__file__).parent / "data"

FILES = [
    DATA_DIR / "2025년 6월.xlsx",
    DATA_DIR / "2025년 7월.xlsx",
    DATA_DIR / "2025년 8월.xlsx"
]

# ==========================================
# 2. 대기오염 데이터 불러오기
# ==========================================

@st.cache_data(show_spinner="대기오염 데이터를 불러오는 중...")
def load_air_data():

    frames = []

    required = [
        "지역", "측정소코드", "측정소명",
        "측정일시", "O3", "NO2"
    ]

    for file in FILES:

        if not file.exists():
            raise FileNotFoundError(
                f"파일을 찾을 수 없습니다: {file}"
            )

        df = pd.read_excel(
            file,
            usecols=required,
            engine="openpyxl"
        )

        df["측정일시"] = (
            pd.to_numeric(df["측정일시"], errors="coerce")
            .astype("Int64")
            .astype("string")
        )

        df["datetime"] = pd.to_datetime(
            df["측정일시"],
            format="%Y%m%d%H",
            errors="coerce"
        )

        df["O3"] = pd.to_numeric(
            df["O3"], errors="coerce"
        )

        df["NO2"] = pd.to_numeric(
            df["NO2"], errors="coerce"
        )

        df["측정소코드"] = (
            df["측정소코드"].astype(str)
        )

        frames.append(df)

    result = pd.concat(frames, ignore_index=True)

    result = result.dropna(
        subset=["datetime"]
    )

    return result


# ==========================================
# 3. 지역 좌표 찾기
# ==========================================

@st.cache_data(ttl=86400)
def get_coordinates(region):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    response = requests.get(
        url,
        params={
            "name": region,
            "count": 5,
            "language": "ko",
            "format": "json"
        },
        timeout=30
    )

    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        raise ValueError(
            f"{region} 지역의 좌표를 찾지 못했습니다."
        )

    # 한국 검색 결과 우선 선택
    korean = [
        x for x in results
        if x.get("country_code") == "KR"
    ]

    result = korean[0] if korean else results[0]

    return (
        result["latitude"],
        result["longitude"],
        result.get("name", region)
    )


# ==========================================
# 4. 과거 기상 데이터 가져오기
# ==========================================

@st.cache_data(ttl=86400)
def get_weather(latitude, longitude):

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2025-06-01",
        "end_date": "2025-08-31",
        "hourly": "temperature_2m,shortwave_radiation",
        "timezone": "Asia/Seoul",
        "temperature_unit": "celsius"
    }

    response = requests.get(
        url,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    weather = pd.DataFrame({
        "datetime": data["hourly"]["time"],
        "기온": data["hourly"]["temperature_2m"],
        "일사량": data["hourly"]["shortwave_radiation"]
    })

    weather["datetime"] = pd.to_datetime(
        weather["datetime"]
    )

    return weather


# ==========================================
# 5. 회귀분석 함수
# ==========================================

def regression_analysis(df, x_col, y_col):

    data = df[[x_col, y_col]].dropna()

    if len(data) < 3 or data[x_col].nunique() < 2:
        return None

    x = data[x_col].to_numpy()
    y = data[y_col].to_numpy()

    slope, intercept = np.polyfit(x, y, 1)

    predicted = slope * x + intercept

    ss_res = np.sum((y - predicted) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)

    r_squared = (
        1 - ss_res / ss_tot
        if ss_tot != 0 else np.nan
    )

    correlation = np.corrcoef(x, y)[0, 1]

    return {
        "상관계수": correlation,
        "결정계수": r_squared,
        "기울기": slope,
        "절편": intercept,
        "개수": len(data)
    }


# ==========================================
# 6. 데이터 실행
# ==========================================

try:

    air = load_air_data()

except Exception as e:

    st.error(f"대기오염 데이터 오류: {e}")
    st.stop()


# ==========================================
# 7. 측정소 선택
# ==========================================

st.subheader("📍 분석할 측정소 선택")

stations = (
    air[["지역", "측정소명", "측정소코드"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

selected = st.selectbox(
    "측정소",
    stations.to_dict("records"),
    format_func=lambda x:
        f'{x["지역"]} | {x["측정소명"]} ({x["측정소코드"]})'
)

region = selected["지역"]

selected_air = air[
    (air["지역"] == region) &
    (air["측정소명"] == selected["측정소명"]) &
    (air["측정소코드"] == selected["측정소코드"])
].copy()

st.info(
    f"선택한 측정소: {region} / {selected['측정소명']}"
)


# ==========================================
# 8. 기상 자료 결합
# ==========================================

if st.button("🌤️ 기상 데이터 불러오기 및 분석", type="primary"):

    try:

        with st.spinner("지역 좌표를 찾는 중..."):

            latitude, longitude, location_name = (
                get_coordinates(region)
            )

        with st.spinner("2025년 과거 기상 자료를 가져오는 중..."):

            weather = get_weather(
                latitude,
                longitude
            )

        # 대기오염 데이터와 기상 데이터 시간 기준 결합
        merged = pd.merge(
            selected_air,
            weather,
            on="datetime",
            how="inner"
        )

        merged = merged.dropna(
            subset=["O3", "기온", "일사량"]
        )

        if merged.empty:
            st.error("결합할 수 있는 데이터가 없습니다.")
            st.stop()

        # 날짜별 데이터
        merged["날짜"] = merged["datetime"].dt.date

        # 오존: 하루 중 최고 농도
        ozone_daily = (
            merged.groupby("날짜")
            .agg(
                오존최고=("O3", "max"),
                오존평균=("O3", "mean"),
                이산화질소평균=("NO2", "mean")
            )
        )

        # 기상: 해당 지역의 시간별 기상 자료 전체 이용
        weather["날짜"] = weather["datetime"].dt.date

        weather_daily = (
            weather.groupby("날짜")
            .agg(
                기온최고=("기온", "max"),
                기온평균=("기온", "mean"),
                일사량합계=("일사량", "sum")
            )
        )

        # 시간별 일사량(W/m²)을 하루 누적 에너지(MJ/m²)로 환산
        weather_daily["일사량합계"] *= 0.0036

        daily = weather_daily.join(
            ozone_daily,
            how="inner"
        ).dropna()

        daily.index = pd.to_datetime(daily.index)

        daily.index.name = "날짜"

        if daily.empty:
            st.error("분석 가능한 날짜가 없습니다.")
            st.stop()

        # ----------------------------------
        # 9. 결과 요약
        # ----------------------------------

        st.divider()
        st.header("📊 분석 결과")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "분석 날짜",
            f"{len(daily)}일"
        )

        col2.metric(
            "최고 기온",
            f'{daily["기온최고"].max():.1f} ℃'
        )

        col3.metric(
            "최고 오존 농도",
            f'{daily["오존최고"].max():.4f} ppm'
        )

        col4.metric(
            "최고 오존 발생일",
            daily["오존최고"].idxmax().strftime("%m월 %d일")
        )

        st.caption(
            f"기상 좌표: {location_name} "
            f"({latitude:.3f}, {longitude:.3f})"
        )

        # ----------------------------------
        # 10. 날짜별 오존 농도
        # ----------------------------------

        st.subheader("① 날짜별 오존 농도 변화")

        st.line_chart(
            daily[["오존최고", "오존평균"]]
        )

        # ----------------------------------
        # 11. 기온과 오존 관계
        # ----------------------------------

        st.divider()
        st.subheader("② 기온과 오존 농도의 관계")

        st.scatter_chart(
            daily,
            x="기온최고",
            y="오존최고"
        )

        temp_result = regression_analysis(
            daily.reset_index(),
            "기온최고",
            "오존최고"
        )

        if temp_result:

            a, b, c = st.columns(3)

            a.metric(
                "상관계수",
                f'{temp_result["상관계수"]:.3f}'
            )

            b.metric(
                "결정계수",
                f'{temp_result["결정계수"]:.3f}'
            )

            c.metric(
                "회귀 기울기",
                f'{temp_result["기울기"]:.5f}'
            )

            st.write(
                f'회귀식: 오존 농도 = '
                f'{temp_result["기울기"]:.5f} × 기온 '
                f'+ {temp_result["절편"]:.5f}'
            )

            x = daily["기온최고"].to_numpy()

            predicted = (
                temp_result["기울기"] * x
                + temp_result["절편"]
            )

            temp_line = pd.DataFrame({
                "실제 오존 농도": daily["오존최고"].values,
                "회귀 예측 오존 농도": predicted
            })

            st.line_chart(temp_line)

        # ----------------------------------
        # 12. 일사량과 오존 관계
        # ----------------------------------

        st.divider()
        st.subheader("③ 일사량과 오존 농도의 관계")

        st.scatter_chart(
            daily,
            x="일사량합계",
            y="오존최고"
        )

        solar_result = regression_analysis(
            daily.reset_index(),
            "일사량합계",
            "오존최고"
        )

        if solar_result:

            a, b, c = st.columns(3)

            a.metric(
                "상관계수",
                f'{solar_result["상관계수"]:.3f}'
            )

            b.metric(
                "결정계수",
                f'{solar_result["결정계수"]:.3f}'
            )

            c.metric(
                "회귀 기울기",
                f'{solar_result["기울기"]:.5f}'
            )

            st.write(
                f'회귀식: 오존 농도 = '
                f'{solar_result["기울기"]:.5f} × 일사량 '
                f'+ {solar_result["절편"]:.5f}'
            )

            x = daily["일사량합계"].to_numpy()

            predicted = (
                solar_result["기울기"] * x
                + solar_result["절편"]
            )

            solar_line = pd.DataFrame({
                "실제 오존 농도": daily["오존최고"].values,
                "회귀 예측 오존 농도": predicted
            })

            st.line_chart(solar_line)

        # ----------------------------------
        # 13. 월별 비교
        # ----------------------------------

        st.divider()
        st.subheader("④ 월별 평균 비교")

        monthly = daily.copy()

        monthly["월"] = monthly.index.month

        monthly = (
            monthly.groupby("월")
            .agg(
                평균기온=("기온평균", "mean"),
                평균오존=("오존평균", "mean"),
                평균일사량=("일사량합계", "mean")
            )
        )

        st.write("월별 평균 기온 (℃)")
        st.bar_chart(monthly[["평균기온"]])

        st.write("월별 평균 오존 농도 (ppm)")
        st.bar_chart(monthly[["평균오존"]])

        st.write("월별 평균 일사량 (MJ/m²)")
        st.bar_chart(monthly[["평균일사량"]])

        # ----------------------------------
        # 14. 일별 상세 데이터
        # ----------------------------------

        st.divider()
        st.subheader("⑤ 날짜별 상세 데이터")

        st.dataframe(
            daily.style.format({
                "기온최고": "{:.1f}",
                "기온평균": "{:.1f}",
                "일사량합계": "{:.2f}",
                "오존최고": "{:.4f}",
                "오존평균": "{:.4f}",
                "이산화질소평균": "{:.4f}"
            }),
            use_container_width=True
        )

        # CSV 다운로드
        csv = daily.reset_index().to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            "📥 분석 결과 CSV 다운로드",
            data=csv,
            file_name="오존_기상_분석결과.csv",
            mime="text/csv"
        )

        # ----------------------------------
        # 15. 해석 시 주의사항
        # ----------------------------------

        st.divider()
        st.subheader("🔎 분석 시 주의할 점")

        st.warning(
            """
            1. 기온과 일사량은 Open-Meteo의 과거 기상 재분석 자료입니다.
            2. 일사량은 시간별 자료를 합산한 일일 누적값입니다.
            3. 상관관계가 높다고 해서 인과관계가 증명되는 것은 아닙니다.
            4. 오존 생성에는 기온과 일사량뿐 아니라 NOx, VOCs 등
               다양한 요인이 관여합니다.
            5. 측정소 주변의 실제 기상 환경과 격자 기상 자료에는
               차이가 있을 수 있습니다.
            """
        )

        st.success("분석이 완료되었습니다!")

    except Exception as e:

        st.error(f"분석 중 오류가 발생했습니다: {e}")

