"""Giao diện Demo Dự đoán Khách hàng Rời bỏ Dịch vụ Viễn thông (Streamlit App).

Chạy ứng dụng từ thư mục gốc dự án:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from src.feature_engineering_b import tao_dac_trung_B

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "report" / "figures"
COMPARISON_CSV = ROOT / "report" / "model_comparison.csv"

st.set_page_config(
    page_title="Telco Churn Prediction - Nhóm 4",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS cho giao diện hiện đại
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .risk-high {
        background-color: #FEE2E2;
        border-left: 6px solid #DC2626;
        padding: 1.2rem;
        border-radius: 8px;
        color: #991B1B;
    }
    .risk-low {
        background-color: #ECFDF5;
        border-left: 6px solid #059669;
        padding: 1.2rem;
        border-radius: 8px;
        color: #065F46;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_models_and_preprocessors():
    """Tải trước toàn bộ mô hình và bộ tiền xử lý vào cache."""
    models = {
        "decision_tree_A": joblib.load(MODELS_DIR / "decision_tree_A.pkl"),
        "decision_tree_B": joblib.load(MODELS_DIR / "decision_tree_B.pkl"),
        "knn_A": joblib.load(MODELS_DIR / "knn_A.pkl"),
        "knn_B": joblib.load(MODELS_DIR / "knn_B.pkl"),
    }
    preprocessor_A = joblib.load(MODELS_DIR / "preprocessor_A.pkl")
    return models, preprocessor_A


def render_sidebar():
    st.sidebar.title("⚙️ Cấu hình Mô hình")
    model_choice = st.sidebar.selectbox(
        "Chọn mô hình thực thi:",
        options=[
            ("decision_tree_A", "Decision Tree - Luồng A (Đề xuất tối ưu theo F1-score: 0.6258 & Recall: 0.7914)"),
            ("decision_tree_B", "Decision Tree - Luồng B (Tối ưu Recall: 0.7995)"),
            ("knn_A", "K-NN - Luồng A (K-NN tối ưu F1: 0.5992)"),
            ("knn_B", "K-NN - Luồng B (Tối ưu Accuracy: 0.7906)"),
        ],
        format_func=lambda x: x[1],
    )[0]

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Bảng chỉ số tổng hợp")
    if COMPARISON_CSV.exists():
        df_comp = pd.read_csv(COMPARISON_CSV)
        st.sidebar.dataframe(
            df_comp[["model", "flow", "accuracy", "recall", "f1_score"]].rename(
                columns={
                    "model": "Mô hình",
                    "flow": "Luồng",
                    "accuracy": "Accuracy",
                    "recall": "Recall",
                    "f1_score": "F1-score",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.caption("Nhóm 4: Hùng (Trưởng nhóm), Mạnh, Đức, Hải")
    return model_choice


def main():
    st.markdown('<div class="main-title">📡 Dự Đoán Khách Hàng Rời Bỏ Dịch Vụ Viễn Thông</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ứng dụng demo hỗ trợ nhận diện sớm khách hàng có nguy cơ rời mạng (Customer Churn) - Đề tài 9</div>', unsafe_allow_html=True)

    models, preprocessor_A = load_models_and_preprocessors()
    selected_model_id = render_sidebar()

    tab_pred, tab_error, tab_about = st.tabs(["🔍 Dự đoán Khách hàng", "📉 Phân tích Lỗi & Đối sánh", "ℹ️ Thông tin Đề tài"])

    with tab_pred:
        col_preset1, col_preset2 = st.columns([2, 1])
        with col_preset1:
            preset = st.radio(
                "Tải hồ sơ mẫu nhanh:",
                ["Nhập tùy chỉnh", "Mẫu 1: Khách hàng nguy cơ rời bỏ cao (Churn)", "Mẫu 2: Khách hàng trung thành (Ở lại)"],
                horizontal=True,
            )

        # Thiết lập giá trị mặc định theo preset
        defaults = {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 3,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 79.85,
        }
        if preset == "Mẫu 2: Khách hàng trung thành (Ở lại)":
            defaults.update({
                "tenure": 58,
                "Partner": "Yes",
                "Dependents": "Yes",
                "Contract": "Two year",
                "OnlineSecurity": "Yes",
                "TechSupport": "Yes",
                "PaymentMethod": "Credit card (automatic)",
                "MonthlyCharges": 65.20,
            })

        with st.form("customer_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("👤 Nhân khẩu học")
                gender = st.selectbox("Giới tính:", ["Male", "Female"], index=0 if defaults["gender"] == "Male" else 1)
                senior = st.selectbox("Người cao tuổi (Senior Citizen):", [0, 1], format_func=lambda x: "Có" if x == 1 else "Không", index=defaults["SeniorCitizen"])
                partner = st.selectbox("Có bạn đời (Partner):", ["No", "Yes"], index=0 if defaults["Partner"] == "No" else 1)
                dependents = st.selectbox("Có người phụ thuộc (Dependents):", ["No", "Yes"], index=0 if defaults["Dependents"] == "No" else 1)

                st.subheader("💳 Hợp đồng & Thanh toán")
                contract = st.selectbox("Loại hợp đồng (Contract):", ["Month-to-month", "One year", "Two year"], index=["Month-to-month", "One year", "Two year"].index(defaults["Contract"]))
                paperless = st.selectbox("Hóa đơn điện tử (Paperless):", ["No", "Yes"], index=0 if defaults["PaperlessBilling"] == "No" else 1)
                payment = st.selectbox(
                    "Phương thức thanh toán:",
                    ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
                    index=["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"].index(defaults["PaymentMethod"]),
                )

            with col2:
                st.subheader("🌐 Dịch vụ Viễn thông")
                tenure = st.slider("Thời gian gắn bó (Tháng):", min_value=0, max_value=72, value=defaults["tenure"])
                phone = st.selectbox("Dịch vụ điện thoại cố định:", ["Yes", "No"], index=0 if defaults["PhoneService"] == "Yes" else 1)
                multilines = st.selectbox(
                    "Đa đường dây (Multiple Lines):",
                    ["No", "Yes", "No phone service"],
                    index=["No", "Yes", "No phone service"].index(defaults["MultipleLines"]),
                )
                internet = st.selectbox(
                    "Dịch vụ Internet:",
                    ["Fiber optic", "DSL", "No"],
                    index=["Fiber optic", "DSL", "No"].index(defaults["InternetService"]),
                )

                st.subheader("💵 Cước phí")
                monthly_charges = st.number_input("Cước hàng tháng ($):", min_value=15.0, max_value=150.0, value=defaults["MonthlyCharges"], step=0.5)
                auto_total = float(tenure * monthly_charges)
                total_charges = st.number_input("Tổng cước lũy kế ($):", min_value=0.0, max_value=10000.0, value=auto_total, step=10.0)

            with col3:
                st.subheader("🛡️ Dịch vụ Gia tăng & Bảo vệ")
                sec_options = ["No", "Yes", "No internet service"] if internet != "No" else ["No internet service"]
                security = st.selectbox("Bảo mật trực tuyến (Online Security):", sec_options, index=0 if defaults["OnlineSecurity"] in sec_options else 0)
                backup = st.selectbox("Sao lưu dữ liệu (Online Backup):", sec_options, index=0 if defaults["OnlineBackup"] in sec_options else 0)
                device_protect = st.selectbox("Bảo hiểm thiết bị (Device Protection):", sec_options, index=0 if defaults["DeviceProtection"] in sec_options else 0)
                support = st.selectbox("Hỗ trợ kỹ thuật chuyên sâu (Tech Support):", sec_options, index=0 if defaults["TechSupport"] in sec_options else 0)
                tv = st.selectbox("Truyền hình trực tuyến (Streaming TV):", sec_options, index=0 if defaults["StreamingTV"] in sec_options else 0)
                movies = st.selectbox("Phim ảnh theo yêu cầu (Streaming Movies):", sec_options, index=0 if defaults["StreamingMovies"] in sec_options else 0)

            submitted = st.form_submit_button("🚀 Thực Hiện Dự Đoán Nguy Cơ Rời Mạng", use_container_width=True)

        if submitted:
            # Tạo DataFrame 1 dòng tương ứng 19 đặc trưng gốc
            raw_dict = {
                "gender": [gender],
                "SeniorCitizen": [senior],
                "Partner": [partner],
                "Dependents": [dependents],
                "tenure": [tenure],
                "PhoneService": [phone],
                "MultipleLines": [multilines],
                "InternetService": [internet],
                "OnlineSecurity": [security],
                "OnlineBackup": [backup],
                "DeviceProtection": [device_protect],
                "TechSupport": [support],
                "StreamingTV": [tv],
                "StreamingMovies": [movies],
                "Contract": [contract],
                "PaperlessBilling": [paperless],
                "PaymentMethod": [payment],
                "MonthlyCharges": [monthly_charges],
                "TotalCharges": [total_charges],
            }
            raw_df = pd.DataFrame(raw_dict)

            # Thực thi tiền xử lý theo luồng đã chọn
            model = models[selected_model_id]
            is_flow_a = selected_model_id.endswith("_A")

            if is_flow_a:
                X_input = preprocessor_A.transform(raw_df)
            else:
                X_input = tao_dac_trung_B(raw_df)

            prediction = model.predict(X_input)[0]
            churn_proba = None
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_input)[0]
                pos_idx = list(model.classes_).index("Yes")
                churn_proba = probs[pos_idx]

            st.markdown("---")
            st.subheader("🎯 Kết Quả Phân Tích & Dự Báo")

            res_col1, res_col2 = st.columns([1, 1])

            with res_col1:
                if prediction == "Yes":
                    st.markdown(
                        f"""
                        <div class="risk-high">
                            <h3>⚠️ CẢNH BÁO: KHÁCH HÀNG CÓ NGUY CƠ RỜI BỎ (CHURN)</h3>
                            <p>Mô hình dự báo khách hàng này có xác suất cao sẽ hủy dịch vụ trong thời gian tới.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="risk-low">
                            <h3>✅ AN TOÀN: KHÁCH HÀNG CÓ XU HƯỚNG Ở LẠI (STAY)</h3>
                            <p>Mô hình nhận định khách hàng đang gắn bó ổn định với nhà mạng.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with res_col2:
                if churn_proba is not None:
                    st.write(f"**Xác suất rời bỏ (Churn Probability):** `{churn_proba*100:.1f}%`")
                    st.progress(float(churn_proba))
                    if churn_proba > 0.5:
                        st.caption("🔴 Mức độ rủi ro: **CAO**")
                    elif churn_proba > 0.3:
                        st.caption("🟡 Mức độ rủi ro: **TRUNG BÌNH**")
                    else:
                        st.caption("🟢 Mức độ rủi ro: **THẤP**")

            # Khuyến nghị kinh doanh
            st.markdown("#### 💡 Khuyến nghị hành động cho bộ phận CSKH:")
            if contract == "Month-to-month":
                st.info("📌 **Hợp đồng từng tháng:** Đây là yếu tố hàng đầu gây Churn. Hãy chủ động đề xuất chính sách ưu đãi giảm giá cước 10-15% nếu khách hàng chuyển sang hợp đồng 1 năm.")
            if security == "No" or support == "No":
                st.info("📌 **Thiếu dịch vụ bảo vệ:** Khách hàng không dùng Online Security hoặc Tech Support có tỷ lệ Churn rất cao. Nên tặng dùng thử gói bảo vệ 3 tháng.")
            if payment == "Electronic check":
                st.info("📌 **Thanh toán qua Electronic Check:** Phương thức này có tỷ lệ lỗi và churn cao nhất. Hãy khuyến khích chuyển sang Auto-Pay (thẻ tín dụng/ngân hàng) kèm quà tặng cước.")

    with tab_error:
        st.subheader("📉 Phân Tích Lỗi (Error Analysis trên Tập Test chung)")
        st.markdown(
            """
            Phân tích lỗi trên 1.409 khách hàng của tập Test độc lập giúp nhóm hiểu rõ lý do mô hình nhầm lẫn:
            - **False Negatives (Bỏ sót Churn):** Khách rời mạng nhưng mô hình đoán là ở lại $\\rightarrow$ thường do khách hàng có thâm niên cao hoặc hợp đồng dài hạn nhưng phát sinh bất mãn đột xuất.
            - **False Positives (Nhầm là Churn):** Khách ở lại nhưng mô hình đoán rời mạng $\\rightarrow$ thường do dùng hợp đồng Month-to-month và cước cao nhưng chưa có nhu cầu đổi mạng.
            """
        )

        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.image(str(FIGURES_DIR / "error_analysis_decision_tree.png"), caption="Phân tích lỗi: Decision Tree (Luồng A)", use_container_width=True)
            st.image(str(FIGURES_DIR / "dt_confusion_matrix.png"), caption="Ma trận nhầm lẫn: Decision Tree (A vs B)", use_container_width=True)

        with sub_col2:
            st.image(str(FIGURES_DIR / "error_analysis_knn.png"), caption="Phân tích lỗi: K-NN (Luồng A)", use_container_width=True)
            st.image(str(FIGURES_DIR / "knn_confusion_matrix.png"), caption="Ma trận nhầm lẫn: K-NN (A vs B)", use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Bảng 30 Ca Lỗi Tiêu Biểu Để Tra Cứu")
        sample_csv = RESULTS_DIR / "error_cases_sample.csv"
        if sample_csv.exists():
            df_sample = pd.read_csv(sample_csv)
            st.dataframe(df_sample, use_container_width=True)

    with tab_about:
        st.subheader("ℹ️ Giới thiệu Đề tài Bài tập lớn")
        st.markdown(
            """
            - **Đề tài 9:** Dự đoán khách hàng rời bỏ dịch vụ viễn thông (Telco Customer Churn).
            - **Học phần:** Nhập môn Học Máy.
            - **Quy ước kỹ thuật nghiêm ngặt:**
              - `random_state = 42`, `test_size = 0.20`, `stratify = y`.
              - Đánh giá chéo 4 cấu hình mô hình trên **cùng một tập Test duy nhất**.
            - **Phân công nhiệm vụ nhóm:**
              1. **Hùng (Đội trưởng):** Quản lý chung, tổng hợp báo cáo LaTeX, notebook tổng hợp.
              2. **Mạnh:** EDA, chia tập Train/Test chuẩn, tiền xử lý Luồng A.
              3. **Đức:** Feature Engineering Luồng B, huấn luyện Decision Tree A/B.
              4. **Hải:** Huấn luyện K-NN A/B, Phân tích lỗi (Error Analysis), Xây dựng Demo Streamlit.
            """
        )


if __name__ == "__main__":
    main()
