import concurrent.futures
import streamlit as st
from groq import Groq
from PIL import Image
import io

# 1. Cấu hình giao diện ứng dụng Web nâng cao
st.set_page_config(page_title="AI Học Tập Đa Phương Thức Siêu Tốc", layout="wide", page_icon="🎓")
st.title("🎓 AI HỖ TRỢ HỌC TẬP - SIÊU TỐC & ĐA PHƯƠNG THỨC")
st.write("Hệ thống Hội đồng AI chạy song song 1 vòng duy nhất, phản hồi siêu tốc và chống lan man.")

# Khởi tạo bộ nhớ lịch sử cuộc trò chuyện và bộ nhớ tạm của ảnh dán
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pasted_image_bytes" not in st.session_state:
    st.session_state.pasted_image_bytes = None

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
    st.session_state.pasted_image_bytes = None
    st.rerun()

# Hàm gọi một khối AI lý luận độc lập (Tối ưu hóa tốc độ với temperature=0.0)
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
            temperature=0.0
        )
        res_text = chat_completion.choices[0].message.content
        return {"id": agent_id, "content": str(res_text)}
    except Exception as e:
        return {"id": agent_id, "content": f"Lỗi từ Agent: {e}"}

# Hàm Agent Thị Giác phân tích hình ảnh (Dùng Model Qwen chuyên xử lý ảnh)
def call_vision_agent(image_bytes):
    if not GROQ_API_KEY:
        return "Chưa có API Key."
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Bạn là chuyên gia quét chữ và đề bài từ hình ảnh. Hãy trích xuất và dịch toàn bộ nội dung câu hỏi, đề bài toán/lý/hóa hoặc văn bản có trong ảnh này thành văn bản thuần túy một cách chính xác nhất."
                }
            ],
            model="qwen/qwen3.6-27b",
            temperature=0.0
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"[Lỗi giải mã hình ảnh]: {e}"

# Hàm gọi AI Trọng tài tổng hợp kết quả (Hạ nhiệt độ xuống 0.0 để chốt chữ nhanh nhất)
def call_referee_with_history(system_prompt, current_data, history):
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
            temperature=0.0
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

# --- 4. CƠ CHẾ NHÚNG JAVASCRIPT HACK ĐỂ BẮT SỰ KIỆN CTRL + V TRỰC TIẾP ---
st.components.v1.html(
    """
    <script>
    document.addEventListener('paste', async (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (const item of items) {
            if (item.type.indexOf('image') === 0) {
                const blob = item.getAsFile();
                const reader = new FileReader();
                reader.onload = function(event) {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: event.target.result
                    }, '*');
                };
                reader.readAsDataURL(blob);
            }
        }
    });
    </script>
    """,
    height=0,
)

# Khu vực hỗ trợ kéo thả ảnh hoặc dán qua Clipboard tự động nhận diện
uploaded_file = st.file_uploader("📷 Để gửi ảnh, bạn có thể dán (Ctrl+V) hoặc kéo thả trực tiếp file vào đây:", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.session_state.pasted_image_bytes = uploaded_file.read()
    st.image(st.session_state.pasted_image_bytes, caption="📷 Ảnh đính kèm trong hàng đợi gửi...", width=150)

# --- 5. Ô NHẬP LIỆU DƯỚI CÙNG ---
if user_query := st.chat_input("Hỏi bất cứ điều gì... (Nhấp vào đây, dán ảnh hoặc gõ chữ)"):
    
    full_user_prompt = user_query
    
    if st.session_state.pasted_image_bytes is not None:
        with st.spinner("🔍 Agent Thị Giác đang đọc quét nội dung bức ảnh bạn gửi..."):
            extracted_image_text = call_vision_agent(st.session_state.pasted_image_bytes)
            full_user_prompt = f"[Nội dung từ hình ảnh bài tập]:\n{extracted_image_text}\n\n[Lời nhắn của học sinh]: {user_query}"

    with st.chat_message("user"):
        if st.session_state.pasted_image_bytes is not None:
            st.write(f"📷 [Gửi kèm 1 hình ảnh] — {user_query}")
        else:
            st.write(user_query)
        
    if not GROQ_API_KEY:
        st.error("Hệ thống chưa được cấu hình API Key.")
    else:
        with st.chat_message("assistant"):
            progress_bar = st.progress(0)
            st_status = st.empty()
            
            st_status.text("⚡ Hội đồng AI đang xử lý song song siêu tốc 1 vòng duy nhất...")
            progress_bar.progress(40)
            
            fix_slang_prompt = " Hiểu các từ viết tắt tiếng Việt (ko=không, j=gì, dc=được, tui=tôi, môn j=môn gì)."
            
            raw_results = {}

            # Tối ưu hóa: Gom tất cả 5 Agent cốt lõi chạy song song 1 vòng duy nhất để triệt tiêu độ trễ mạng
            agents_config = {
                "Agent_1": "Bạn là Học giả Uyên bác. Đưa ra định nghĩa chính xác, khoa học và ngắn gọn nhất." + fix_slang_prompt,
                "Agent_2": "Bạn là Gia sư Sư phạm. Đưa ra các bước giải logic ngắn gọn." + fix_slang_prompt,
                "Agent_3": "Bạn là Chuyên gia Toán học. Kiểm tra và tối ưu hóa các công thức, phương trình." + fix_slang_prompt,
                "Agent_4": "Bạn là Nhà Biện chứng. Phản biện, tìm lỗi sai, bẫy lừa trong đề bài để đảm bảo tính chính xác.",
                "Agent_5": "Bạn là Chuyên gia Tóm tắt & Ứng dụng. Trích xuất cốt lõi và ứng dụng thực tiễn của bài học."
            }

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(call_groq_agent, prompt, full_user_prompt, key) for key, prompt in agents_config.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]

            st_status.text("🏛️ AI Trọng tài tối cao chốt đáp án đồng thuận...")
            progress_bar.progress(85)

            data_toan_bo_hoi_dong = f"Câu hỏi của học sinh: {full_user_prompt}\n\n"
            for i in range(1, 6):
                data_toan_bo_hoi_dong += f"[Dữ liệu Agent {i}]:\n{raw_results.get(f'Agent_{i}')}\n\n"

            prompt_trong_tai = "Bạn là Giảng viên Đại học Ưu tú. Hãy dựa vào báo cáo song song từ các AI cấp dưới ở phần USER để viết ra MỘT câu trả lời HOÀN CHỈNH, ĐẦY ĐỦ VÀ CHÍNH XÁC NHẤT dưới dạng Markdown (tiêu đề bôi đậm, gạch đầu dòng). Không viết lời mở đầu thừa thãi. Bắt buộc bọc biểu thức toán/lý/hóa bằng dấu $ hoặc $$." + fix_slang_prompt

            ket_qua_cuoi = call_referee_with_history(prompt_trong_tai, data_toan_bo_hoi_dong, st.session_state.chat_history)
            ket_qua_sach = fix_latex_format(ket_qua_cuoi)

            progress_bar.empty()
            st_status.empty()

            st.markdown(ket_qua_sach)

            # Lưu vào bộ nhớ lịch sử cuộc trò chuyện và làm sạch hàng đợi ảnh
            st.session_state.chat_history.append({"user": user_query, "bot": ket_qua_sach})
            st.session_state.pasted_image_bytes = None
            st.rerun()
