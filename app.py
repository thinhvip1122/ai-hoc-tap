import concurrent.futures
import streamlit as st
from groq import Groq

# 1. Cấu hình giao diện ứng dụng Web
st.set_page_config(page_title="AI Học Tập Siêu Tốc Pro", layout="wide", page_icon="🎓")
st.title("🎓 AI HỖ TRỢ HỌC TẬP - MULTI-AGENT PRO")
st.write("Hệ thống song song 3 Agent kiểm tra chéo, xử lý siêu tốc và chống lan man.")

# 2. Cấu hình API Key (Khuyến khích dùng st.secrets khi deploy)
# Bạn có thể nhập key vào ô bên dưới hoặc cấu hình trong file .toml
GROQ_API_KEY = st.sidebar.text_input("Nhập Groq API Key của bạn:", value="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", type="password")
MODEL_NAME = st.sidebar.selectbox("Chọn mô hình AI:", ["llama-3.3-70b-specdec", "llama-3.1-8b-instant", "mixtral-8x7b-32768"])

# Khởi tạo client an toàn
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.error(f"Lỗi khởi tạo cổng Groq: {e}")
else:
    st.warning("Vui lòng nhập Groq API Key ở thanh bên để bắt đầu!")

# Hàm gọi một khối AI độc lập
def call_groq_agent(system_prompt, user_query, agent_id):
    if not GROQ_API_KEY:
        return "Chưa cấu hình API Key."
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": str(user_query)}
            ],
            model=MODEL_NAME, # Đã sửa sang model chuẩn của Groq
            temperature=0.1 # Giữ nguyên độ chính xác cao
        )
        res_text = chat_completion.choices[0].message.content
        return {"id": agent_id, "content": str(res_text)}
    except Exception as e:
        return {"id": agent_id, "content": f"Lỗi kết nối từ hệ thống AI {agent_id}: {e}"}

# Hàm chuẩn hóa công thức Toán/Hóa để Streamlit hiển thị KaTeX đẹp mắt
def fix_latex_format(text):
    if not text:
        return ""
    # Xử lý chuẩn hóa các ký hiệu toán học phổ biến từ markdown sang KaTeX của Streamlit
    text = text.replace(r"\[", "$$").replace(r"\]", "$$")
    text = text.replace(r"\(", "$").replace(r"\)", "$")
    return text

# 3. Giao diện nhận câu hỏi từ người dùng
user_query = st.text_area("Nhập câu hỏi học tập hoặc đề bài vào đây:", placeholder="Ví dụ: Giải phương trình bậc hai x^2 - 5x + 6 = 0")

if st.button("Thực thi phân tích siêu tốc", type="primary"):
    if not GROQ_API_KEY:
        st.error("Bạn không thể thực thi khi chưa điền API Key!")
    elif not user_query.strip():
        st.warning("Vui lòng nhập câu hỏi trước khi chạy!")
    else:
        with st.spinner("🚀 3 AI đang phản tích song song và tổng hợp dữ liệu..."):
            
            # Khai báo Prompt cho 3 AI chạy song song
            prompts = {
                "AI_1": "Bạn là một học giả uyên bác. Hãy trả lời câu hỏi học tập của người dùng một cách chính xác tuyệt đối, khoa học và ngắn gọn.",
                "AI_2": "Bạn là một gia sư giảng dạy. Hãy phân tích đề bài, đưa ra đáp án đúng kèm theo các bước giải thích cốt lõi, dễ hiểu nhất. Không nói lời thừa.",
                "AI_3": "Bạn là một chuyên gia thẩm định kiến thức học thuật. Hãy trả lời câu hỏi của người dùng một cách chính xác nhất dưới góc nhìn khoa học thực nghiệm, ngắn gọn và không có lời thừa."
            }
            
            # Sử dụng Dict để lưu kết quả cố định theo key, tránh lỗi tráo đổi vị trí do chạy đa luồng
            raw_results = {}
            
            # Chạy đa luồng song song thực sự
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Truyền thêm tham số ID để định danh chính xác kết quả trả về
                futures = [executor.submit(call_groq_agent, prompt, user_query, key) for key, prompt in prompts.items()]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    raw_results[res["id"]] = res["content"]
            
            # Gom dữ liệu có định danh rõ ràng cho Trọng Tài
            data_gom = f"""
            [Đáp án từ Học Giả Uyên Bác]: {raw_results.get('AI_1', 'Lỗi')}
            [Đáp án từ Gia Sư Giảng Dạy]: {raw_results.get('AI_2', 'Lỗi')}
            [Đáp án từ Chuyên Gia Thẩm Định]: {raw_results.get('AI_3', 'Lỗi')}
            """
            
            # Khối AI Trọng Tài cuối cùng
            prompt_trong_tai = """
            Bạn là một Giảng viên đại học ưu tú. Nhiệm vụ của bạn là tổng hợp dữ liệu từ 3 bài giải được cung cấp ở phần USER để tạo ra một bài học HOÀN CHỈNH, ĐẦY ĐỦ VÀ CHI TIẾT NHẤT cho học sinh.
            
            Hãy tuân thủ nghiêm ngặt các quy tắc sau:
            1. Không được viết lời nhận xét, đối chiếu hay so sánh kiểu "Đáp án 1 nói thế này, đáp án 2 nói thế kia".
            2. Tổng hợp tất cả các ý đúng và hay nhất: Định nghĩa chính xác, Công thức chuẩn, Định lý đảo/Mở rộng (nếu có), Ví dụ minh họa có lời giải chi tiết từng bước.
            3. Trình bày bài học khoa học bằng Markdown (tiêu đề, bôi đậm, danh sách gạch đầu dòng).
            4. QUY ĐỊNH BẮT BUỘC VỀ CÔNG THỨC: Toàn bộ công thức Toán học, phương trình Lý/Hóa PHẢI ĐƯỢC BỌC TRONG dấu $ (nếu viết cùng dòng) hoặc dấu $$ (nếu viết xuống dòng riêng). Tuyệt đối không dùng ký hiệu khác như \\[ hay \\(.
            """
            
            # Gọi Trọng Tài tổng hợp kết quả cuối
            res_trong_tai = call_groq_agent(prompt_trong_tai, data_gom, "TrongTai")
            ket_qua_cuoi = res_trong_tai["content"]
            
            # Làm sạch công thức hiển thị
            ket_qua_sach = fix_latex_format(ket_qua_cuoi)
            
            # 4. Xuất kết quả ra màn hình dạng Tabs trực quan
            st.success("Đã tổng hợp xong kết quả hoàn hảo!")
            
            tab1, tab2 = st.tabs(["📘 Bài học tổng hợp (Trọng tài)", "🔬 Chi tiết dữ liệu gốc (3 AI Agent)"])
            
            with tab1:
                st.markdown(ket_qua_sach)
                
            with tab2:
                st.info("Dưới đây là câu trả lời độc lập của từng AI trước khi được Trọng Tài tổng hợp:")
                st.markdown("#### 1. Học giả uyên bác:")
                st.write(raw_results.get('AI_1'))
                st.markdown("#### 2. Gia sư giảng dạy:")
                st.write(raw_results.get('AI_2'))
                st.markdown("#### 3. Chuyên gia thẩm định:")
                st.write(raw_results.get('AI_3'))
