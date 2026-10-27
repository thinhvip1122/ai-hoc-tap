import concurrent.futures
import streamlit as st
from groq import Groq

# 1. Cấu hình giao diện ứng dụng Web
st.set_page_config(page_title="AI Học Tập Siêu Tốc Pro", layout="wide", page_icon="🎓")
st.title("🎓 AI HỖ TRỢ HỌC TẬP - MULTI-AGENT PRO (CÓ BỘ NHỚ)")
st.write("Hệ thống song song 3 Agent kiểm tra chéo, xử lý siêu tốc và ghi nhớ lịch sử hội thoại.")

# Khởi tạo bộ nhớ lịch sử cuộc trò chuyện nếu chưa có
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. Cấu hình mô hình AI
MODEL_NAME = st.sidebar.selectbox(
    "Chọn mô hình AI:", 
    ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
)

# Lấy API Key an toàn từ mục Secrets của Streamlit
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_API_KEY = st.sidebar.text_input("Nhập Groq API Key của bạn:", type="password")

# Khởi tạo cổng kết nối Groq Client
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.error(f"Lỗi khởi tạo cổng Groq: {e}")
else:
    st.warning("Vui lòng cấu hình GROQ_API_KEY trong mục Advanced settings -> Secrets để chạy ứng dụng!")

# Hàm gọi một khối AI độc lập (Dành cho 3 Agent phân tích độc lập câu hỏi mới)
def call_groq_agent(system_prompt, user_query, agent_id):
    if not GROQ_API_KEY:
        return {"id": agent_id, "content": "Chưa cấu hình API Key."}
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": str(user_query)}
            ],
            model=MODEL_NAME,
            temperature=0.1
        )
        res_text = chat_completion.choices[0].message.content
        return {"id": agent_id, "content": str(res_text)}
    except Exception as e:
        return {"id": agent_id, "content": f"Lỗi kết nối từ hệ thống AI {agent_id}: {e}"}

# Hàm gọi AI Trọng Tài có kèm theo toàn bộ lịch sử cuộc trò chuyện
def call_referee_with_history(system_prompt, current_data, history):
    if not GROQ_API_KEY:
        return "Chưa cấu hình API Key."
    
    # Xây dựng danh sách tin nhắn bao gồm lịch sử
    messages = [{"role": "system", "content": str(system_prompt)}]
    
    # Thêm các câu hội thoại cũ vào để AI nhớ ngữ cảnh
    for chat in history:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["bot"]})
    
    # Cuối cùng đưa dữ liệu phân tích mới nhất của câu hỏi hiện tại vào
    messages.append({"role": "user", "content": f"Câu hỏi mới và dữ liệu gợi ý:\n{current_data}"})
    
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            temperature=0.3 # Tăng nhẹ để AI linh hoạt liên kết câu chữ
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Lỗi kết nối từ Trọng Tài: {e}"

# Hàm chuẩn hóa công thức Toán/Hóa để Streamlit hiển thị hiển thị đẹp mắt
def fix_latex_format(text):
    if not text:
        return ""
    text = text.replace(r"\[", "$$").replace(r"\]", "$$")
    text = text.replace(r"\(", "$").replace(r"\)", "$")
    return text

# 3. Giao diện nhận câu hỏi từ người dùng
user_query = st.text_area("Nhập câu hỏi học tập hoặc đề bài vào đây:", placeholder="Ví dụ: Định lý Pytago là gì? (Sau đó có thể hỏi tiếp: Hãy cho tôi ví dụ về nó)")

if st.button("Thực thi phân tích siêu tốc", type="primary"):
    if not GROQ_API_KEY:
        st.error("Hệ thống chưa nhận được API Key. Vui lòng kiểm tra lại cấu hình Advanced settings.")
    elif not user_query.strip():
        st.warning("Vui lòng nhập câu hỏi trước khi chạy!")
    else:
        with st.spinner("🚀 AI đang liên kết dữ liệu hội thoại và phân tích..."):
            
            # Khai báo Prompt cho 3 AI chạy song song để mổ xẻ câu hỏi hiện tại
            prompts = {
                "AI_1": "Bạn là một học giả uyên bác. Hãy trả lời câu hỏi học tập của người dùng một cách chính xác tuyệt đối, khoa học và ngắn gọn.",
                "AI_2": "Bạn là một gia sư giảng dạy. Hãy phân tích đề bài, đưa ra đáp án đúng kèm theo các bước giải thích cốt lõi, dễ hiểu nhất. Không nói lời thừa.",
                "AI_3": "Bạn là một chuyên gia thẩm định kiến thức học thuật. Hãy trả lời câu hỏi của người dùng một cách chính xác nhất dưới góc nhìn khoa học thực nghiệm, ngắn gọn và không có lời thừa."
            }
            
            raw_results = {}
            
            # Chạy đa luồng song song xử lý câu hỏi hiện tại
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(call_groq_agent, prompt, user_query, key) for key, prompt in prompts.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]
            
            # Gom dữ liệu thô từ 3 Agent
            data_gom = f"""
            Câu hỏi hiện tại của người dùng: {user_query}
            [Gợi ý giải 1]: {raw_results.get('AI_1', 'Lỗi')}
            [Gợi ý giải 2]: {raw_results.get('AI_2', 'Lỗi')}
            [Gợi ý giải 3]: {raw_results.get('AI_3', 'Lỗi')}
            """
            
            # Khối AI Trọng Tài cuối cùng (Có nhiệm vụ đọc cả lịch sử hội thoại được truyền vào hệ thống)
            prompt_trong_tai = """
            Bạn là một Giảng viên đại học ưu tú. Nhiệm vụ của bạn là dựa vào lịch sử trò chuyện và dữ liệu gợi ý từ 3 bài giải [Gợi ý giải] ở phần USER để tạo ra câu trả lời HOÀN CHỈNH, ĐẦY ĐỦ VÀ PHÙ HỢP NGỮ CẢNH NHẤT cho học sinh.
            
            Hãy tuân thủ nghiêm ngặt các quy tắc sau:
            1. Tuyệt đối không viết lời nhận xét, đối chiếu hay so sánh kiểu "Đáp án 1 nói thế này, đáp án 2 nói thế kia".
            2. Trả lời trực tiếp vào vấn đề người dùng đang hỏi, liên kết logic với các câu hỏi trước đó trong lịch sử trò chuyện (nếu có).
            3. Trình bày bài học khoa học bằng Markdown (tiêu đề bôi đậm, danh sách gạch đầu dòng).
            4. Toàn bộ công thức Toán học, phương trình Lý/Hóa PHẢI ĐƯỢC BỌC TRONG dấu $ (nếu viết cùng dòng) hoặc dấu $$ (nếu viết xuống dòng riêng).
            """
            
            # Gọi Trọng Tài và truyền kèm st.session_state.chat_history (Bộ nhớ cuộc trò chuyện)
            ket_qua_cuoi = call_referee_with_history(prompt_trong_tai, data_gom, st.session_state.chat_history)
            
            # Làm sạch công thức hiển thị
            ket_qua_sach = fix_latex_format(ket_qua_cuoi)
            
            # Lưu lượt hội thoại mới này vào bộ nhớ hệ thống
            st.session_state.chat_history.append({"user": user_query, "bot": ket_qua_sach})

# 4. Hiển thị lịch sử cuộc trò chuyện ra màn hình theo dạng dòng thời gian (Chat Timeline)
if st.session_state.chat_history:
    st.write("---")
    st.markdown("### 💬 Lịch sử cuộc trò chuyện của bạn:")
    
    # Duyệt qua từng tin nhắn trong bộ nhớ và in ra giao diện
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        # Hiển thị câu hỏi của người dùng
        st.markdown(f"**🧑 Bạn:** {chat['user']}")
        # Hiển thị câu trả lời tổng hợp của AI Trọng tài
        st.markdown(f"**📘 AI Trọng Tài:**\n{chat['bot']}")
        st.write("---")

# Nút bấm để xóa bộ nhớ làm lại từ đầu nếu muốn ở thanh sidebar
if st.sidebar.button("🗑️ Xóa lịch sử hội thoại"):
    st.session_state.chat_history = []
    st.rerun()
