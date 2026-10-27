import concurrent.futures
import streamlit as st
from groq import Groq

# 1. Cấu hình giao diện ứng dụng Web nâng cao
st.set_page_config(page_title="Hội Đồng AI Học Tập Tối Cao", layout="wide", page_icon="🏛️")
st.title("🏛️ HỘI ĐỒNG AI HỌC TẬP - 10 AGENT SONG SONG")
st.write("Hệ thống kết hợp sức mạnh lý luận của 10 AI Agent chuyên biệt theo chuẩn Groq mới nhất.")

# Khởi tạo bộ nhớ lịch sử cuộc trò chuyện
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Cấu hình mô hình AI - CẬP NHẬT CHUẨN THEO TÀI LIỆU CỦA GROQ
MODEL_NAME = st.sidebar.selectbox(
    "Chọn mô hình AI nền tảng:", 
    ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.6-27b"]
)

# Quản lý API Key bảo mật
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_API_KEY = st.sidebar.text_input("Nhập Groq API Key của bạn:", type="password")

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.sidebar.error(f"Lỗi khởi tạo cổng Groq: {e}")
else:
    st.sidebar.warning("Vui lòng cấu hình GROQ_API_KEY để hệ thống hoạt động.")

if st.sidebar.button("🗑️ Làm mới cuộc trò chuyện"):
    st.session_state.chat_history = []
    st.rerun()

# Hàm gọi một khối AI độc lập
def call_groq_agent(system_prompt, user_query, agent_id):
    if not GROQ_API_KEY:
        return {"id": agent_id, "content": "Chưa có API Key."}
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": str(user_query)}
            ],
            model=MODEL_NAME,
            temperature=0.15
        )
        res_text = chat_completion.choices[0].message.content
        return {"id": agent_id, "content": str(res_text)}
    except Exception as e:
        return {"id": agent_id, "content": f"Lỗi từ Agent này: {e}"}

# Hàm gọi AI Trọng Tài Tổng Hợp Hội Đồng
def call_referee_with_history(system_prompt, current_data, history):
    if not GROQ_API_KEY:
        return "Chưa có API Key."
    
    messages = [{"role": "system", "content": str(system_prompt)}]
    for chat in history:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["bot"]})
    
    messages.append({"role": "user", "content": f"Báo cáo tổng hợp từ hội đồng 10 AI:\n{current_data}"})
    
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            temperature=0.3
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Lỗi từ Trọng tài Tổng hợp: {e}"

# Khử nhiễu cấu trúc Markdown KaTeX toán học
def fix_latex_format(text):
    if not text:
        return ""
    text = text.replace(r"\[", "$$").replace(r"\]", "$$")
    text = text.replace(r"\(", "$").replace(r"\)", "$")
    return text

# --- 3. HIỂN THỊ LỊCH SỬ KHUNG CHAT MƯỢT MÀ ---
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.markdown(fix_latex_format(chat["bot"]))

# --- 4. XỬ LÝ ĐA LUỒNG 10 AI AGENT SONG SONG ---
if user_query := st.chat_input("Gửi câu hỏi hoặc đề bài cho Hội đồng 10 AI tại đây..."):
    
    with st.chat_message("user"):
        st.write(user_query)
        
    if not GROQ_API_KEY:
        st.error("Hệ thống chưa được cấu hình API Key.")
    else:
        with st.chat_message("assistant"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("⚙️ Hội đồng 10 AI đang phân tích dữ liệu song song...")
            progress_bar.progress(20)
            
            fix_slang_prompt = " Phải hiểu các từ viết tắt, teencode tiếng Việt (ko=không, j=gì, dc=được, tui=tôi, mn=mọi người, môn j=môn gì)."

            # Tên đại diện hiển thị của từng Agent
            agent_names = {
                "Agent_1": "1. 🎓 Học giả Uyên bác",
                "Agent_2": "2. 🏫 Gia sư Sư phạm",
                "Agent_3": "3. 🔬 Nhà Khoa học Thực nghiệm",
                "Agent_4": "4. 📐 Chuyên gia Toán học & Logic",
                "Agent_5": "5. 🌐 Chuyên gia Ngôn ngữ",
                "Agent_6": "6. ⚖️ Nhà Phê bình Biện chứng",
                "Agent_7": "7. 📚 Biên tập viên Sách GK",
                "Agent_8": "8. 📝 Chuyên gia Tóm tắt Siêu tốc",
                "Agent_9": "9. 💡 Nhà Sáng tạo Minh họa",
                "Agent_10": "10. 🗺️ Trợ lý Sơ đồ Tư duy"
            }

            agents_config = {
                "Agent_1": "Bạn là Học giả Uyên bác. Trả lời chính xác tuyệt đối, khoa học và ngắn gọn khái niệm cốt lõi." + fix_slang_prompt,
                "Agent_2": "Bạn là Gia sư Sư phạm. Bẻ nhỏ bài toán thành các bước giải logic, dễ tiếp thu nhất." + fix_slang_prompt,
                "Agent_3": "Bạn là Nhà Khoa học Thực nghiệm. Chỉ ra ứng dụng thực tiễn của kiến thức này trong đời sống." + fix_slang_prompt,
                "Agent_4": "Bạn là Chuyên gia Toán học & Logic. Kiểm tra chặt chẽ tính chính xác của các công thức, hằng số, phương trình." + fix_slang_prompt,
                "Agent_5": "Bạn là Chuyên gia Dịch thuật Ngôn ngữ. Giải mã chính xác câu hỏi lóng, teencode của người dùng sang ngôn ngữ học thuật chuẩn chỉnh." + fix_slang_prompt,
                "Agent_6": "Bạn là Nhà Phê bình Biện chứng. Đóng vai trò phản biện, tìm ra các điểm dễ bẫy hoặc giả định sai lầm trong đề bài." + fix_slang_prompt,
                "Agent_7": "Bạn là Biên tập viên Sách giáo khoa. Định hình câu trả lời theo chuẩn kiến thức sư phạm hiện hành." + fix_slang_prompt,
                "Agent_8": "Bạn là Chuyên gia Tóm tắt Siêu tốc. Chắt lọc câu trả lời thành 3 dòng ghi nhớ (Takeaway) ngắn nhất." + fix_slang_prompt,
                "Agent_9": "Bạn là Nhà Sáng tạo Minh họa. Thiết kế một ví dụ hoặc câu chuyện ẩn dụ thực tế sống động cho bài học." + fix_slang_prompt,
                "Agent_10": "Bạn là Trợ lý Cấu trúc. Đưa ra dàn ý, sơ đồ tư duy dạng text (Mindmap) để người dùng dễ hệ thống." + fix_slang_prompt,
            }
            
            raw_results = {}
            progress_bar.progress(50)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(call_groq_agent, prompt, user_query, key) for key, prompt in agents_config.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]
            
            progress_bar.progress(80)
            status_text.text("⚖️ Đang trình báo lên AI Trọng tài tổng hợp kết quả tối ưu...")
            
            data_gom = f"Câu hỏi gốc: {user_query}\n"
            for k in agents_config.keys():
                data_gom += f"[{k}]: {raw_results.get(k, 'Lỗi kết nối.')}\n"
            
            prompt_trong_tai = """
            Bạn là Giảng viên Đại học Ưu tú - Trọng tài tối cao của hội đồng học thuật.
            Nhiệm vụ của bạn là kết hợp tất cả các góc nhìn tinh túy nhất từ 10 AI Agent cấp dưới để tạo ra một câu trả lời hoàn hảo, toàn diện và sâu sắc nhất cho học sinh.
            
            Quy tắc nghiêm ngặt:
            1. Trình bày bài học liền mạch bằng Markdown. Tuyệt đối không nhận xét kiểu "Agent 1 nói thế này...".
            2. Trả lời bám sát câu hỏi người dùng, liên kết mạch lạc với ngữ cảnh lịch sử trò chuyện.
            3. QUY ĐỊNH CÔNG THỨC: Bắt buộc bọc toán học/vật lý/hóa học bằng dấu $ (cùng dòng) hoặc $$ (xuống dòng).
            """ + fix_slang_prompt
            
            ket_qua_cuoi = call_referee_with_history(prompt_trong_tai, data_gom, st.session_state.chat_history)
            ket_qua_sach = fix_latex_format(ket_qua_cuoi)
            
            progress_bar.empty()
            status_text.empty()
            
            # --- 5. HIỂN THỊ ĐỒNG THỜI CẢ HỘI ĐỒNG RA MÀN HÌNH CHAT ---
            # Đầu tiên: In bài tổng hợp của Trọng tài lên đầu
            st.markdown("### 🏛️ KẾT LUẬN TỪ AI TRỌNG TÀI TỔNG HỢP:")
            st.markdown(ket_qua_sach)
            
            st.write("---")
            st.markdown("### 🔬 Ý KIẾN CHI TIẾT TỪ 10 AI THÀNH VIÊN TRONG HỘI ĐỒNG:")
            
            # Tiếp theo: Duyệt qua 10 Agent và in trực tiếp ra màn hình dạng text
            for key, display_name in agent_names.items():
                st.markdown(f"#### {display_name}")
                st.write(raw_results.get(key, "Không có phản hồi."))
            
            st.session_state.chat_history.append({"user": user_query, "bot": ket_qua_sach})
