import concurrent.futures
import streamlit as st
from groq import Groq
import base64

# 1. Cấu hình giao diện ứng dụng Web nâng cao
st.set_page_config(page_title="AI Học Tập Đa Phương Thức", layout="wide", page_icon="🎓")
st.title("🎓 AI HỖ TRỢ HỌC TẬP - ĐỒNG THUẬN & ĐỌC HÌNH ẢNH")
st.write("Hệ thống hội đồng 10 AI phản biện ngầm, hỗ trợ phân tích cả câu hỏi chữ và ảnh chụp đề bài.")

# Khởi tạo bộ nhớ lịch sử cuộc trò chuyện
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Cấu hình mô hình AI nền tảng của Groq (Ưu tiên mô hình hỗ trợ thị giác/đa phương thức)
MODEL_NAME = st.sidebar.selectbox(
    "Chọn mô hình AI nền tảng:", 
    ["qwen/qwen3.6-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]
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

# Hàm chuyển đổi file ảnh tải lên thành mã hóa Base64 để gửi qua API an toàn
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Hàm gọi một khối AI độc lập (Hỗ trợ cả văn bản và dữ liệu ảnh đa phương thức)
def call_groq_agent(system_prompt, user_query, agent_id, image_base64=None):
    if not GROQ_API_KEY:
        return {"id": agent_id, "content": "Chưa có API Key."}
    
    # Xây dựng nội dung tin nhắn đa phương thức
    content_list = [{"type": "text", "text": str(user_query)}]
    
    # Nếu người dùng có tải ảnh lên, đính kèm dữ liệu ảnh vào luồng xử lý của Agent
    if image_base64:
        content_list.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": content_list}
            ],
            model=MODEL_NAME,
            temperature=0.0  # Tối ưu tốc độ tối đa
        )
        res_text = chat_completion.choices[0].message.content
        return {"id": agent_id, "content": str(res_text)}
    except Exception as e:
        return {"id": agent_id, "content": f"Lỗi từ Agent này: {e}"}

# Hàm gọi AI Trọng tài tổng hợp cuối cùng có kèm lịch sử
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
            temperature=0.1
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Lỗi kết nối hệ thống: {e}"

# Khử nhiễu cấu trúc toán học KaTeX
def fix_latex_format(text):
    if not text:
        return ""
    text = text.replace(r"\[", "$$").replace(r"\]", "$$")
    text = text.replace(r"\(", "$").replace(r"\)", "$")
    return text

# --- 3. HIỂN THỊ LỊCH SỬ KHUNG CHAT ---
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.markdown(fix_latex_format(chat["bot"]))

# --- 4. Ô TẢI HÌNH ẢNH (Giao diện đính kèm file trực quan) ---
# Tạo một ô nhỏ cho phép người dùng bấm chọn hoặc kéo thả ảnh đề bài vào ứng dụng
uploaded_image = st.file_uploader("📸 Đính kèm hình ảnh đề bài (nếu có):", type=["png", "jpg", "jpeg"])

if uploaded_image:
    # Hiển thị ảnh xem trước thu nhỏ trên màn hình của người dùng
    st.image(uploaded_image, caption="Hình ảnh bạn đã tải lên", width=300)

# --- 5. Ô NHẬP LIỆU DƯỚI CÙNG ---
if user_query := st.chat_input("Nhập câu hỏi hoặc yêu cầu phân tích ảnh tại đây..."):
    
    # Hiển thị câu hỏi của bạn ra khung chat
    with st.chat_message("user"):
        st.write(user_query)
        
    if not GROQ_API_KEY:
        st.error("Hệ thống chưa được cấu hình API Key.")
    else:
        with st.chat_message("assistant"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("⚡ Toàn hội đồng 10 AI đang quét ảnh và thống nhất luận điểm...")
            progress_bar.progress(30)
            
            # Xử lý mã hóa ảnh nếu có tệp được tải lên
            image_b64 = encode_image(uploaded_image) if uploaded_image else None
            
            fix_slang_prompt = " Hiểu các từ viết tắt tiếng Việt (ko=không, j=gì, dc=được, tui=tôi, môn j=môn gì)."
            raw_results = {}

            # --- VÒNG 1: 5 AGENT ĐẦU LẬP BẢN THẢO (ĐỌC ẢNH VÀ CHỮ) ---
            vong1_config = {
                "Agent_1": "Bạn là Học giả Uyên bác. Trích xuất văn bản từ hình ảnh nếu có và đưa ra định nghĩa khái niệm cốt lõi chính xác." + fix_slang_prompt,
                "Agent_2": "Bạn là Gia sư Sư phạm. Phân tích hình ảnh/đề bài và bẻ nhỏ thành các bước giải logic cụ thể." + fix_slang_prompt,
                "Agent_3": "Bạn là Chuyên gia Toán học. Giải quyết và tối ưu hóa toàn bộ công thức, đồ thị, phương trình có trong văn bản hoặc ảnh." + fix_slang_prompt,
                "Agent_4": "Bạn là Chuyên gia Ngôn ngữ. Giải mã teencode, dịch nghĩa các câu chữ viết tắt từ học sinh." + fix_slang_prompt,
                "Agent_5": "Bạn là Biên tập viên Sách GK. Định hình bài giải bám sát khung kiến thức sư phạm quy chuẩn." + fix_slang_prompt,
            }

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(call_groq_agent, prompt, user_query, key, image_b64) for key, prompt in vong1_config.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]

            # --- VÒNG 2: 5 AGENT SAU PHẢN BIỆN CHÉO ---
            progress_bar.progress(65)
            ban_thao_vong1 = f"Câu hỏi/Hình ảnh đầu vào của học sinh.\n"
            for i in range(1, 6):
                ban_thao_vong1 += f"[Ý kiến nhóm {i}]: {raw_results[f'Agent_{i}']}\n"

            vong2_config = {
                "Agent_6": "Bạn là Nhà Biện chứng. Đối chiếu ảnh gốc và ý kiến vòng 1, tìm bẫy sai sót, đính chính đáp án chuẩn xác nhất.",
                "Agent_7": "Bạn là Nhà Khoa học. Đưa ra ứng dụng thực tiễn của bài toán/hình ảnh này vào thực tế.",
                "Agent_8": "Bạn là Chuyên gia Tóm tắt. Chắt lọc toàn bộ kết quả đồng thuận thành 3 dòng cốt lõi cực ngắn.",
                "Agent_9": "Bạn là Nhà Sáng tạo. Đưa ra ví dụ minh họa tương đồng hoàn toàn với đề bài trong ảnh.",
                "Agent_10": "Bạn là Trợ lý Cấu trúc. Kiến tạo sơ đồ tư duy bằng chữ (Mindmap) logic tổng hợp từ toàn bộ hệ thống.",
            }

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(call_groq_agent, prompt, ban_thao_vong1, key, image_b64) for key, prompt in vong2_config.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]

            # --- VÒNG 3: TRỌNG TÀI TỔNG HỢP ---
            status_text.text("🏛️ Đang kết xuất câu trả lời đồng thuận tối ưu...")
            progress_bar.progress(90)

            data_toan_bo_hoi_dong = f"Yêu cầu: {user_query}\n\n"
            for i in range(1, 11):
                data_toan_bo_hoi_dong += f"[Dữ liệu hội đồng {i}]:\n{raw_results.get(f'Agent_{i}')}\n\n"

            prompt_trong_tai = """
            Bạn là Giảng viên Đại học Ưu tú. Dựa vào báo cáo thống nhất ngầm từ 10 AI cấp dưới đối chiếu với hình ảnh/văn bản đầu vào để viết ra MỘT câu trả lời HOÀN CHỈNH, ĐẦY ĐỦ VÀ CHÍNH XÁC NHẤT.
            
            Quy tắc nghiêm ngặt:
            1. Trình bày bài học liền mạch bằng Markdown. Không ghi từ thừa như 'Dưới đây là...', 'Báo cáo của Agent...'.
            2. Trả lời trực tiếp, kết hợp đồng bộ định nghĩa, cách giải từ ảnh, ví dụ và sơ đồ chữ thành một trục bài học duy nhất.
            3. QUY ĐỊNH CÔNG THỨC: Bắt buộc bọc biểu thức bằng dấu $ hoặc $$.
            """ + fix_slang_prompt

            ket_qua_cuoi = call_referee_with_history(prompt_trong_tai, data_toan_bo_hoi_dong, st.session_state.chat_history)
            ket_qua_sach = fix_latex_format(ket_qua_cuoi)

            progress_bar.empty()
            status_text.empty()

            # Xuất 1 câu trả lời duy nhất ra màn hình
            st.markdown(ket_qua_sach)
            st.session_state.chat_history.append({"user": user_query, "bot": ket_qua_sach})
