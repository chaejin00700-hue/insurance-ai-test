import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime

st.set_page_config(page_title="푸본현대생명 AI 심사 테스트", page_icon="🏥", layout="centered")

st.title("🏥 보험금 자동심사 AI (개인 테스트용)")
st.caption("⚠️ 개인 학습 목적 전용 | 실제 고객 정보 사용 금지")

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Google AI Studio에서 발급받은 키 입력"
    )
    st.markdown("[API 키 발급받기](https://aistudio.google.com)")

    st.divider()
    st.subheader("🔍 1) 사용 가능한 모델 확인")
    if st.button("모델 목록 조회"):
        if not api_key:
            st.warning("먼저 API 키를 입력해주세요!")
        else:
            try:
                genai.configure(api_key=api_key)
                names = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        names.append(m.name.replace('models/', ''))
                if names:
                    st.success(f"{len(names)}개 모델 인식됨")
                    for n in names:
                        st.code(n)
                else:
                    st.error("인식된 모델이 없습니다.")
            except Exception as e:
                st.error(f"조회 오류: {e}")

    st.divider()
    st.subheader("🛠️ 2) 심사에 사용할 모델")
    selected_model = st.text_input(
        "모델명을 직접 입력하세요 (위 조회 결과에서 복사해 붙여넣기)",
        value="gemini-2.0-flash-lite"
    )
    st.caption(f"현재 선택: `{selected_model}`")

st.subheader("📋 심사 조건 설정")
col1, col2 = st.columns(2)
with col1:
    insurance_type = st.selectbox("보험 종류", ["실손의료비", "정기보험", "암보험", "입원일당", "수술비"])
with col2:
    document_type = st.selectbox("서류 종류", ["진단서", "입퇴원확인서", "의료비영수증", "수술확인서", "처방전"])

st.subheader("📎 서류 업로드")
st.warning("⚠️ 반드시 개인정보(이름/주민번호/연락처)를 가린 테스트용 서류만 업로드!")

uploaded_file = st.file_uploader("서류 사진을 업로드하세요", type=['jpg', 'jpeg', 'png'])

if uploaded_file and api_key:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 서류", use_container_width=True)

    if st.button("🔍 AI 자동심사 시작", type="primary", use_container_width=True):
        with st.spinner(f"[{selected_model}] 모델로 분석 중... (10~20초 소요)"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)

                prompt = f"""
당신은 푸본현대생명 보험금 심사 전문가입니다.
아래 조건과 업로드된 서류를 참고하여 심사 결과를 정리해주세요.

[심사 조건]
- 보험 종류: {insurance_type}
- 서류 종류: {document_type}

【추출 정보】
1. 진단명 및 질병코드(KCD)
2. 입원/통원 구분 및 일수
3. 총 진료비 및 본인부담금
4. 주요 치료 내용 (수술, 시술 등)

【심사 의견】
1. 지급 가능성 (가능 / 불가 / 추가확인필요)
2. 판단 근거
3. 추가로 확인해야 할 서류나 사항

【심사자 코멘트】
전체 의견을 2~3줄로 요약해주세요.

※ 서류에서 확인 불가한 항목은 "확인불가"로 표기
※ 이름/주민번호 등 개인정보는 절대 출력하지 마세요
"""
                response = model.generate_content([prompt, image])

                st.success(f"✅ 심사 분석 완료! (사용 모델: {selected_model})")
                st.markdown("---")
                st.markdown(response.text)
                st.markdown("---")

                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 결과 저장 (TXT)",
                    data=response.text,
                    file_name=f"심사결과_{now}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ [{selected_model}] 오류\n\n상세: {e}")
                st.info("👈 좌측 사이드바에서 모델명을 바꾼 후 다시 버튼만 눌러보세요! (GitHub 재수정 불필요)")

elif uploaded_file and not api_key:
    st.warning("👈 왼쪽 상단 '>>' 메뉴를 열어 API Key를 먼저 입력해주세요!")

st.divider()
st.caption("🔒 AI 판단은 참고용이며 최종 결정은 반드시 담당자가 확인해야 합니다.")
