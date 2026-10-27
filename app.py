import concurrent.futures
import streamlit as st
from groq import Groq

# 1. Cấu hình giao diện ứng dụng Web nâng cao
st.set_page_config(page_title="Hội Đồng AI Thống Nhất Tối Cao", layout="wide", page_icon="🏛️")
st.title("🏛️ HỘI ĐỒNG AI HỌC TẬP - 10 AGENT THỐNG NHẤT")
st.write("Hệ thống đa tác nhân nâng cao: 10 AI liên kết dữ liệu, phản biện chéo và đồng thuận kết quả.")

# Khởi tạo bộ nhớ lịch sử cuộc trò chuyện
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Cấu hình mô hình AI nền tảng của Groq
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

# Hàm gọi AI có kèm theo toàn bộ lịch sử cuộc trò chuyện
def call_agent_with_history(system_prompt, current_data, history):
    if not GROQ_API_KEY:
        return "Chưa có API Key."
    
    messages = [{"role": "system", "content": str(system_prompt)}]
    for chat in history:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["bot"]})
    
    messages.append({"role": "user", "content": str(current_data)})
    
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            temperature=0.2
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Lỗi kết nối hệ thống: {e}"

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

# --- 4. XỬ LÝ QUY TRÌNH ĐỒNG THUẬN 10 AI ---
if user_query := st.chat_input("Gửi câu hỏi hoặc đề bài cho Hội đồng 10 AI tại đây..."):
    
    with st.chat_message("user"):
        st.write(user_query)
        
    if not GROQ_API_KEY:
        st.error("Hệ thống chưa được cấu hình API Key.")
    else:
        with st.chat_message("assistant"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            fix_slang_prompt = " Phải hiểu các từ viết tắt, teencode tiếng Việt (ko=không, j=gì, dc=được, tui=tôi, môn j=môn gì)."
            
            agent_names = {
                "Agent_1": "1. 🎓 Học giả Uyên bác",
                "Agent_2": "2. 🏫 Gia sư Sư phạm",
                "Agent_3": "3. 📐 Chuyên gia Toán học & Logic",
                "Agent_4": "4. 🌐 Chuyên gia Ngôn ngữ",
                "Agent_5": "5. 📚 Biên tập viên Sách GK",
                "Agent_6": "6. ⚖️ Nhà Phê bình Biện chứng",
                "Agent_7": "7. 🔬 Nhà Khoa học Thực nghiệm",
                "Agent_8": "8. 📝 Chuyên gia Tóm tắt Siêu tốc",
                "Agent_9": "9. 💡 Nhà Sáng tạo Minh họa",
                "Agent_10": "10. 🗺️ Trợ lý Sơ đồ Tư duy"
            }

            raw_results = {}

            # --- VÒNG 1: 5 AGENT ĐẦU ĐƯA RA BẢN THẢO CHUYÊN MÔN ---
            status_text.text("⏳ Vòng 1: Nhóm Chuyên môn (Agent 1-5) đang lập bản thảo giải đề bài...")
            progress_bar.progress(15)
            
            vong1_config = {
                "Agent_1": "Bạn là Học giả Uyên bác. Đưa ra định nghĩa chính xác tuyệt đối, khoa học và ngắn gọn nhất về chủ đề này." + fix_slang_prompt,
                "Agent_2": "Bạn là Gia sư Sư phạm. Dựa vào câu hỏi, bẻ nhỏ bài toán hoặc lý thuyết thành các bước giải logic." + fix_slang_prompt,
                "Agent_3": "Bạn là Chuyên gia Toán học & Logic. Kiểm tra chặt chẽ tính chính xác của các công thức, hằng số, phương trình trong đề." + fix_slang_prompt,
                "Agent_4": "Bạn là Chuyên gia Dịch thuật Ngôn ngữ. Giải mã chính xác câu hỏi lóng, teencode của người dùng sang ngôn ngữ học thuật chuẩn chỉnh." + fix_slang_prompt,
                "Agent_5": "Bạn là Biên tập viên Sách giáo khoa. Định hình câu trả lời bám sát theo khung kiến thức sư phạm hiện hành." + fix_slang_prompt,
            }

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(call_groq_agent, prompt, user_query, key) for key, prompt in vong1_config.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]

            # --- VÒNG 2: 5 AGENT SAU ĐỌC BẢN THẢO, PHẢN BIỆN VÀ THỐNG NHẤT ---
            status_text.text("⚖️ Vòng 2: Nhóm Phản biện & Ứng dụng (Agent 6-10) đang thẩm định bản thảo để thống nhất kết quả...")
            progress_bar.progress(50)

            # Tổng hợp dữ liệu vòng 1 để làm đầu vào cho vòng 2
            ban_thao_vong1 = f"Câu hỏi của học sinh: {user_query}\n"
            for i in range(1, 6):
                ban_thao_vong1 += f"[{agent_names[f'Agent_{i}']}] đề xuất:\n{raw_results[f'Agent_{i}']}\n\n"

            vong2_config = {
                "Agent_6": "Bạn là Nhà Phê bình Biện chứng. Đọc kỹ đề xuất của nhóm chuyên môn 1-5 ở phần USER. Thực hiện tìm kẽ hở logic, chỉ ra điểm bẫy, sửa đổi các phần chưa chính xác để thống nhất đáp án đúng nhất.",
                "Agent_7": "Bạn là Nhà Khoa học Thực nghiệm. Đọc đề xuất từ nhóm 1-5 ở phần USER. Đưa ra ứng dụng thực tiễn của đáp án này vào đời sống để bổ trợ kiến thức.",
                "Agent_8": "Bạn là Chuyên gia Tóm tắt Siêu tốc. Đọc đề xuất từ nhóm 1-5 ở phần USER. Chắt lọc toàn bộ các ý kiến thống nhất thành 3 dòng ghi nhớ (Takeaway) ngắn gọn nhất.",
                "Agent_9": "Bạn là Nhà Sáng tạo Minh họa. Đọc đề xuất từ nhóm 1-5 ở phần USER. Thiết kế một ví dụ hoặc câu chuyện ẩn dụ thực tế sống động ăn khớp hoàn toàn với đáp án của nhóm.",
                "Agent_10": "Bạn là Trợ lý Cấu trúc. Đọc đề xuất từ nhóm 1-5 ở phần USER. Cấu trúc lại toàn bộ các ý kiến đã thống nhất thành một sơ đồ tư duy bằng chữ (Mindmap) rõ ràng.",
            }

            # Chạy song song vòng 2 dựa trên kết quả vòng 1
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(call_groq_agent, prompt, ban_thao_vong1, key) for key, prompt in vong2_config.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]

            # --- VÒNG 3: TRỌNG TÀI CHỐT KẾT LUẬN CUỐI CÙNG ---
            status_text.text("🏛️ AI Trọng tài tối cao đang phê duyệt báo cáo đồng thuận của toàn Hội đồng...")
            progress_bar.progress(85)

            data_toan_bo_hoi_dong = f"Câu hỏi của học sinh: {user_query}\n\n"
            for k, display_name in agent_names.items():
                data_toan_bo_hoi_dong += f"[{display_name}]:\n{raw_results.get(k)}\n\n"

            prompt_trong_tai = """
            Bạn là Giảng viên Đại học Ưu tú - Trọng tài tối cao của hội đồng học thuật.
            Nhiệm vụ của bạn là dựa vào lịch sử cuộc trò chuyện và báo cáo THỐNG NHẤT ĐỒNG THUẬN từ 10 AI Agent cấp dưới ở phần USER để viết ra một bài học HOÀN CHỈNH, ĐẦY ĐỦ VÀ CHÍNH XÁC NHẤT.
            
            Quy tắc nghiêm ngặt:
            1. Trình bày bài học liền mạch bằng Markdown sạch đẹp. Tuyệt đối không nhận xét rời rạc kiểu "Agent 1 nói thế này...".
            2. Toàn bộ nội dung phải đồng bộ, thống nhất một kết quả, bổ sung đầy đủ từ khái niệm, bước giải, ứng dụng, ví dụ đến sơ đồ.
            3. QUY ĐỊNH CÔNG THỨC: Bắt buộc bọc biểu thức/phương trình bằng dấu $ hoặc $$.
            """ + fix_slang_prompt

            ket_qua_cuoi = call_agent_with_history(prompt_trong_tai, data_toan_bo_hoi_dong, st.session_state.chat_history)
            ket_qua_sach = fix_latex_format(ket_qua_cuoi)

            progress_bar.empty()
            status_text.empty()

            # --- 5. HIỂN THỊ KẾT QUẢ ĐỒNG THUẬN RA KHUNG CHAT ---
            st.markdown("### 🏛️ KẾT LUẬN THỐNG NHẤT TỪ AI TRỌNG TÀI TỐI CAO:")
            st.markdown(ket_qua_sach)
            
            st.write("---")
            st.markdown("### 🔬 TIẾN TRÌNH ĐỒNG THUẬN CHI TIẾT CỦA 10 AI THÀNH VIÊN:")
            
            for key, display_name in agent_names.items():
                with st.expander(f"➔ Xem đóng góp từ: {display_name}"):
                    st.write(raw_results.get(key, "Không có phản hồi."))
            
            # Lưu vào bộ nhớ lịch sử
