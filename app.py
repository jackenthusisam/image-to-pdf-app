import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="高级图片转PDF工具", layout="wide")

st.title("🛠️ 高级图片转 PDF 转换器")

# --- 侧边栏设置 ---
st.sidebar.header("转换设置")
quality = st.sidebar.slider("图片质量 (压缩率)", 1, 100, 80)
page_size = st.sidebar.selectbox("页面尺寸", ["原始尺寸", "A4 (等比缩放)"])
export_name = st.sidebar.text_input("导出文件名", "my_document")

# --- 主界面 ---
uploaded_files = st.file_uploader(
    "1. 上传图片", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 将上传的文件转为字典，方便后续按顺序提取
    file_dict = {f.name: f for f in uploaded_files}
    file_names = list(file_dict.keys())

    st.write("---")
    st.subheader("2. 调整顺序与预览")
    
    # 核心功能：使用 multiselect 让用户决定排序（或者手动拖拽）
    sorted_names = st.multiselect(
        "请按顺序选择/排列图片（未选中的图片将不会被包含在 PDF 中）:",
        options=file_names,
        default=file_names
    )

    # 预览区域
    if sorted_names:
        cols = st.columns(5)
        for i, name in enumerate(sorted_names):
            with cols[i % 5]:
                img = Image.open(file_dict[name])
                st.image(img, caption=f"第 {i+1} 页", use_container_width=True)

    st.write("---")
    
    # --- 转换逻辑 ---
    if st.button("✨ 生成并压缩 PDF"):
        if not sorted_names:
            st.error("请至少选择一张图片！")
        else:
            with st.spinner("正在处理图片并生成 PDF..."):
                pdf_buffer = io.BytesIO()
                processed_images = []

                for name in sorted_names:
                    # 1. 处理图片
                    img = Image.open(file_dict[name]).convert("RGB")
                    
                    # 2. 如果选了 A4，进行简单的等比缩放计算（可选增强）
                    if page_size == "A4 (等比缩放)":
                        # A4 比例大约是 1:1.414，这里做简单处理
                        img.thumbnail((1240, 1754), Image.Resampling.LANCZOS)
                    
                    processed_images.append(img)

                # 3. 写入 PDF
                if processed_images:
                    # 利用 Pillow 的 save 功能，通过 quality 参数控制体积
                    processed_images[0].save(
                        pdf_buffer,
                        format="PDF",
                        save_all=True,
                        append_images=processed_images[1:],
                        quality=quality, # 这里的 quality 会影响 PDF 内部 JPEG 的压缩率
                        optimize=True
                    )
                    
                    st.success("✅ PDF 生成成功！")
                    st.download_button(
                        label="📥 下载 PDF 文件",
                        data=pdf_buffer.getvalue(),
                        file_name=f"{export_name}.pdf",
                        mime="application/pdf"
                    )

# 运行方法：streamlit run app_v2.py
