import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import os

st.set_page_config(page_title="🎤 K-pop 아이돌 분석기", page_icon="🎤", layout="wide")

def get_photo(idol):
    """로컬 photos/ 폴더 우선, 없으면 CSV URL, 없으면 None"""
    eng = str(idol.get("영문이름", ""))
    safe = eng.replace("/","_").replace(".","_").replace(" ","_")
    local = f"photos/{safe}.jpg"
    if os.path.exists(local):
        return local
    url = idol.get("photo_url", "")
    return url if url else None

@st.cache_data
def load():
    df = pd.read_csv("kpop_idol.csv", encoding="utf-8")
    df["데뷔연도"] = pd.to_datetime(df["데뷔일"], errors="coerce").dt.year
    df["출생연도"] = pd.to_numeric(df["출생연도"], errors="coerce")
    df["키(cm)"] = pd.to_numeric(df["키(cm)"], errors="coerce")
    df["나이"] = 2026 - df["출생연도"]
    return df

df = load()

st.title("🎤 K-pop 아이돌 분석기")
st.caption(f"총 {len(df)}명 · {df['그룹'].nunique()}개 그룹 · 남자 {(df['성별']=='남').sum()}명 · 여자 {(df['성별']=='여').sum()}명")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 소속사·그룹",
    "📏 키 분석",
    "🔍 아이돌 검색",
    "👥 그룹 비교",
    "💕 이상형 월드컵"
])

# ══════════════════════════════════════
# TAB 1: 소속사·그룹
# ══════════════════════════════════════
with tab1:
    st.header("🏢 소속사별 아이돌 수")

    col1, col2 = st.columns([2, 1])
    with col1:
        company_cnt = df.groupby("소속사").size().reset_index(name="아이돌 수")
        company_cnt = company_cnt.sort_values("아이돌 수", ascending=False)
        fig = px.bar(company_cnt, x="아이돌 수", y="소속사", orientation="h",
                     color="아이돌 수", color_continuous_scale="Pinkyl",
                     text="아이돌 수", title="소속사별 아이돌 수")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400, showlegend=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 성별 비율")
        gender_cnt = df["성별"].value_counts().reset_index()
        gender_cnt.columns = ["성별", "수"]
        gender_cnt["라벨"] = gender_cnt["성별"].map({"남": "남자 아이돌", "여": "여자 아이돌"})
        fig2 = px.pie(gender_cnt, values="수", names="라벨",
                      color_discrete_sequence=["#74b9ff", "#fd79a8"])
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("🏷️ 그룹별 멤버 수")
    grp_cnt = df.groupby(["그룹", "소속사"]).size().reset_index(name="멤버 수").sort_values("멤버 수", ascending=False)
    st.dataframe(grp_cnt, hide_index=True, use_container_width=True)

# ══════════════════════════════════════
# TAB 2: 키 분석
# ══════════════════════════════════════
with tab2:
    st.header("📏 K-pop 아이돌 키 분석")

    df_h = df[df["키(cm)"].notna()]
    df_m = df_h[df_h["성별"] == "남"]
    df_f = df_h[df_h["성별"] == "여"]

    col1, col2, col3 = st.columns(3)
    col1.metric("전체 평균", f"{df_h['키(cm)'].mean():.1f} cm")
    col2.metric("남자 아이돌 평균", f"{df_m['키(cm)'].mean():.1f} cm", "👨")
    col3.metric("여자 아이돌 평균", f"{df_f['키(cm)'].mean():.1f} cm", "👩")

    # 남/녀 히스토그램 비교
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df_m["키(cm)"], name="남자 아이돌", nbinsx=15,
                               marker_color="#74b9ff", opacity=0.7))
    fig.add_trace(go.Histogram(x=df_f["키(cm)"], name="여자 아이돌", nbinsx=15,
                               marker_color="#fd79a8", opacity=0.7))
    fig.update_layout(barmode="overlay", title="남/여 아이돌 키 분포 비교",
                      xaxis_title="키 (cm)", yaxis_title="명수", height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🏆 키 TOP 10 (전체)")
        top10 = df_h.nlargest(10, "키(cm)")[["영문이름", "한국이름", "그룹", "키(cm)", "성별"]]
        st.dataframe(top10.reset_index(drop=True), hide_index=True, use_container_width=True)
    with col_r:
        st.subheader("📊 그룹별 평균 키")
        grp_h = df_h.groupby("그룹")["키(cm)"].mean().round(1).reset_index()
        grp_h.columns = ["그룹", "평균 키"]
        grp_h = grp_h.sort_values("평균 키", ascending=False)
        fig3 = px.bar(grp_h, x="그룹", y="평균 키", color="평균 키",
                      color_continuous_scale="RdYlGn", text="평균 키")
        fig3.update_traces(textposition="outside", texttemplate="%{text:.1f}")
        fig3.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════
# TAB 3: 아이돌 검색
# ══════════════════════════════════════
with tab3:
    st.header("🔍 아이돌 검색")

    c1, c2 = st.columns([2, 1])
    with c1:
        keyword = st.text_input("이름·그룹 검색", placeholder="예: 카리나, aespa, BTS, 정국 ...")
    with c2:
        gender_filter = st.radio("성별", ["전체", "남자 아이돌", "여자 아이돌"], horizontal=True)

    result = df.copy()
    if gender_filter == "남자 아이돌":
        result = result[result["성별"] == "남"]
    elif gender_filter == "여자 아이돌":
        result = result[result["성별"] == "여"]
    if keyword:
        mask = (
            result["영문이름"].str.contains(keyword, case=False, na=False) |
            result["한국이름"].str.contains(keyword, na=False) |
            result["그룹"].str.contains(keyword, case=False, na=False)
        )
        result = result[mask]

    st.write(f"**{len(result)}명** 검색됨")
    cols_show = ["한국이름", "영문이름", "그룹", "소속사", "키(cm)", "생년월일", "데뷔일", "성별"]
    st.dataframe(result[cols_show].reset_index(drop=True), hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("🎲 랜덤 아이돌 뽑기")
    gen_pick = st.radio("성별 선택", ["전체", "남자만", "여자만"], horizontal=True, key="rand_gen")
    if st.button("🎰 랜덤 아이돌 뽑기!", use_container_width=True):
        pool = df if gen_pick == "전체" else df[df["성별"] == ("남" if gen_pick == "남자만" else "여")]
        pick = pool.sample(1).iloc[0]
        st.balloons()
        c1, c2, c3 = st.columns(3)
        c1.metric("이름", f"{pick['한국이름']}")
        c2.metric("그룹", pick["그룹"])
        c3.metric("키", f"{pick['키(cm)']:.0f} cm" if pd.notna(pick["키(cm)"]) else "-")

# ══════════════════════════════════════
# TAB 4: 그룹 비교
# ══════════════════════════════════════
with tab4:
    st.header("👥 그룹 비교")
    all_groups = sorted(df["그룹"].unique())

    col1, col2 = st.columns(2)
    with col1:
        grp_a = st.selectbox("그룹 1", all_groups,
                             index=all_groups.index("BTS") if "BTS" in all_groups else 0)
    with col2:
        grp_b = st.selectbox("그룹 2", all_groups,
                             index=all_groups.index("aespa") if "aespa" in all_groups else 1)

    data_a = df[df["그룹"] == grp_a]
    data_b = df[df["그룹"] == grp_b]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"🎵 {grp_a}")
        st.metric("멤버 수", len(data_a))
        avg_h = data_a["키(cm)"].mean()
        st.metric("평균 키", f"{avg_h:.1f} cm" if pd.notna(avg_h) else "-")
        debut = data_a["데뷔일"].dropna().iloc[0] if not data_a["데뷔일"].dropna().empty else "-"
        st.metric("데뷔일", debut)
        st.dataframe(data_a[["한국이름","영문이름","키(cm)","생년월일"]].reset_index(drop=True),
                     hide_index=True, use_container_width=True)
    with c2:
        st.subheader(f"🎵 {grp_b}")
        st.metric("멤버 수", len(data_b))
        avg_h_b = data_b["키(cm)"].mean()
        st.metric("평균 키", f"{avg_h_b:.1f} cm" if pd.notna(avg_h_b) else "-")
        debut_b = data_b["데뷔일"].dropna().iloc[0] if not data_b["데뷔일"].dropna().empty else "-"
        st.metric("데뷔일", debut_b)
        st.dataframe(data_b[["한국이름","영문이름","키(cm)","생년월일"]].reset_index(drop=True),
                     hide_index=True, use_container_width=True)

    if pd.notna(avg_h) and pd.notna(avg_h_b):
        winner = grp_a if avg_h > avg_h_b else grp_b
        diff = abs(avg_h - avg_h_b)
        st.success(f"📏 평균 키 승자: **{winner}** (차이: {diff:.1f} cm)")

# ══════════════════════════════════════
# TAB 5: 이상형 월드컵
# ══════════════════════════════════════
with tab5:
    st.header("💕 아이돌 이상형 월드컵")
    st.caption("토너먼트 방식으로 나만의 최애 아이돌을 찾아보세요!")

    # 초기화
    if "wc_started" not in st.session_state:
        st.session_state.wc_started = False
    if "wc_candidates" not in st.session_state:
        st.session_state.wc_candidates = []
    if "wc_winners" not in st.session_state:
        st.session_state.wc_winners = []
    if "wc_round" not in st.session_state:
        st.session_state.wc_round = 1
    if "wc_match" not in st.session_state:
        st.session_state.wc_match = 1
    if "wc_gender" not in st.session_state:
        st.session_state.wc_gender = "여자 아이돌"

    if not st.session_state.wc_started:
        st.subheader("⚙️ 설정")
        wc_gender = st.radio("누구와 해볼까요?", ["여자 아이돌", "남자 아이돌"], horizontal=True)
        pool = df[df["성별"] == ("여" if wc_gender == "여자 아이돌" else "남")]
        st.write(f"참가 아이돌: **{len(pool)}명**")

        size_options = [s for s in [8, 16, 32] if s <= len(pool)]
        wc_size = st.selectbox("토너먼트 인원", size_options, index=len(size_options)-1)

        if st.button("💕 월드컵 시작!", use_container_width=True, type="primary"):
            selected = pool.sample(wc_size).to_dict("records")
            random.shuffle(selected)
            st.session_state.wc_candidates = selected
            st.session_state.wc_winners = []
            st.session_state.wc_round = 1
            st.session_state.wc_match = 1
            st.session_state.wc_gender = wc_gender
            st.session_state.wc_started = True
            st.session_state.wc_size = wc_size
            st.rerun()

    else:
        candidates = st.session_state.wc_candidates
        winners = st.session_state.wc_winners

        total_in_round = len(candidates) + len(winners)
        remaining_matches = len(candidates) // 2

        # 최종 우승자
        if len(candidates) == 0 and len(winners) == 1:
            champ = winners[0]
            st.balloons()
            st.success("🏆 최종 우승!")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                photo = get_photo(champ)
                if photo:
                    st.image(photo, width=280)
                st.markdown(f"""
                <div style="text-align:center; padding:20px; background:linear-gradient(135deg,#ffecd2,#fcb69f); border-radius:20px;">
                    <h1>💕 {champ['한국이름']}</h1>
                    <h2>{champ['영문이름']}</h2>
                    <h3>🎵 {champ['그룹']}</h3>
                    <p>키: {champ['키(cm)']} cm | 생년월일: {champ['생년월일']}</p>
                    <p>소속사: {champ['소속사']}</p>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🔄 다시 하기", use_container_width=True):
                st.session_state.wc_started = False
                st.rerun()

        # 다음 라운드 진입 (현 후보 소진)
        elif len(candidates) == 0:
            st.session_state.wc_candidates = winners
            st.session_state.wc_winners = []
            st.session_state.wc_round += 1
            st.session_state.wc_match = 1
            st.rerun()

        else:
            size = st.session_state.wc_size
            round_num = st.session_state.wc_round
            match_num = st.session_state.wc_match

            # 라운드 이름
            total_this_round = total_in_round
            if total_this_round == 2:
                round_name = "🏆 결승"
            elif total_this_round == 4:
                round_name = "4강"
            elif total_this_round == 8:
                round_name = "8강"
            elif total_this_round == 16:
                round_name = "16강"
            elif total_this_round == 32:
                round_name = "32강"
            else:
                round_name = f"{total_this_round}강"

            st.subheader(f"{round_name} · {match_num}경기")
            progress_total = size - 1
            progress_done = size - total_in_round - len(winners) + match_num - 1
            st.progress(min(progress_done / progress_total, 1.0))

            idol_a = candidates[0]
            idol_b = candidates[1]

            col1, vs_col, col2 = st.columns([5, 1, 5])

            with col1:
                photo_a = get_photo(idol_a)
                if photo_a:
                    st.image(photo_a, use_container_width=True)
                else:
                    st.markdown(
                        "<div style='height:260px;background:#ffecd2;border-radius:12px;"
                        "display:flex;align-items:center;justify-content:center;font-size:80px'>🎤</div>",
                        unsafe_allow_html=True)
                st.markdown(f"""
                <div style="text-align:center; padding:14px; background:linear-gradient(135deg,#ffecd2,#fcb69f);
                     border-radius:12px;">
                    <h2 style="margin:4px">💖 {idol_a['한국이름']}</h2>
                    <p style="margin:2px"><strong>{idol_a['그룹']}</strong></p>
                    <p style="margin:2px; color:#555">키 {idol_a['키(cm)']} cm · {idol_a['생년월일'][:4]}년생</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"💕 {idol_a['한국이름']} 선택!", key="pick_a", use_container_width=True, type="primary"):
                    st.session_state.wc_winners.append(idol_a)
                    st.session_state.wc_candidates = candidates[2:]
                    st.session_state.wc_match += 1
                    st.rerun()

            with vs_col:
                st.markdown("<br><br><br><br><br><h2 style='text-align:center'>VS</h2>", unsafe_allow_html=True)

            with col2:
                photo_b = get_photo(idol_b)
                if photo_b:
                    st.image(photo_b, use_container_width=True)
                else:
                    st.markdown(
                        "<div style='height:260px;background:#c2e9fb;border-radius:12px;"
                        "display:flex;align-items:center;justify-content:center;font-size:80px'>🎤</div>",
                        unsafe_allow_html=True)
                st.markdown(f"""
                <div style="text-align:center; padding:14px; background:linear-gradient(135deg,#a1c4fd,#c2e9fb);
                     border-radius:12px;">
                    <h2 style="margin:4px">💙 {idol_b['한국이름']}</h2>
                    <p style="margin:2px"><strong>{idol_b['그룹']}</strong></p>
                    <p style="margin:2px; color:#555">키 {idol_b['키(cm)']} cm · {idol_b['생년월일'][:4]}년생</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"💕 {idol_b['한국이름']} 선택!", key="pick_b", use_container_width=True, type="primary"):
                    st.session_state.wc_winners.append(idol_b)
                    st.session_state.wc_candidates = candidates[2:]
                    st.session_state.wc_match += 1
                    st.rerun()

            st.divider()
            if st.button("🔄 처음부터 다시", use_container_width=False):
                st.session_state.wc_started = False
                st.rerun()
