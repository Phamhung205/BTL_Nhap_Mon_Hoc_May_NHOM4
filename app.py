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
from sklearn.tree import DecisionTreeClassifier

from src.feature_engineering_b import tao_dac_trung_B

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_DATA_DIR = ROOT / "data" / "raw"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "report" / "figures"
COMPARISON_CSV = ROOT / "report" / "model_comparison.csv"
RAW_CUSTOMER_CSV = RAW_DATA_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

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
    models = {}
    for model_name in ["decision_tree_A", "decision_tree_B", "knn_A", "knn_B"]:
        model_path = MODELS_DIR / f"{model_name}.pkl"
        if model_path.exists():
            models[model_name] = joblib.load(model_path)

    preprocessor_A = joblib.load(MODELS_DIR / "preprocessor_A.pkl") if (MODELS_DIR / "preprocessor_A.pkl").exists() else None
    return models, preprocessor_A


def get_model_display_name(model_key: str) -> str:
    model_labels = {
        "baseline_decision_tree_A": "Baseline (Decision Tree Mặc định) - Luồng A",
        "decision_tree_A": "Decision Tree - Luồng A",
        "decision_tree_B": "Decision Tree - Luồng B",
        "knn_A": "K-NN - Luồng A",
        "knn_B": "K-NN - Luồng B",
    }
    return model_labels.get(model_key, model_key)


def build_baseline_model(preprocessor_A):
    train_X = pd.read_csv(PROCESSED_DIR / "X_train_A.csv")
    train_y = pd.read_csv(PROCESSED_DIR / "y_train.csv")["Churn"]
    model = DecisionTreeClassifier(random_state=42)
    model.fit(preprocessor_A.transform(train_X), train_y)
    return model


def resolve_model(models, preprocessor_A, selected_model_id):
    if selected_model_id in models:
        return models[selected_model_id]

    if selected_model_id == "baseline_decision_tree_A":
        if preprocessor_A is not None:
            baseline_model = build_baseline_model(preprocessor_A)
            models[selected_model_id] = baseline_model
            return baseline_model

    raise KeyError(f"Không tìm thấy mô hình {selected_model_id} trong thư mục models/.")


def classify_risk(probability: float) -> str:
    if probability >= 0.70:
        return "Cao"
    if probability >= 0.40:
        return "Trung bình"
    return "Thấp"


def get_model_comparison_metrics(selected_model_id: str):
    if not COMPARISON_CSV.exists():
        return {}

    csv_map = {
        "baseline_decision_tree_A": "baseline_dt_default",
        "decision_tree_A": "decision_tree_A",
        "decision_tree_B": "decision_tree_B",
        "knn_A": "knn_A",
        "knn_B": "knn_B",
    }
    model_id = csv_map.get(selected_model_id)
    if not model_id:
        return {}

    df = pd.read_csv(COMPARISON_CSV)
    row = df[df["model_id"] == model_id]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


def build_model_advice(model_metrics: dict, churn_probability: float, prediction: str):
    advice = []
    recall = float(model_metrics.get("recall", 0.0) or 0.0)
    f1 = float(model_metrics.get("f1_score", 0.0) or 0.0)
    accuracy = float(model_metrics.get("accuracy", 0.0) or 0.0)

    if recall >= 0.70:
        advice.append("📌 Recall cao: mô hình phát hiện tốt khách hàng rời mạng. Hãy ưu tiên gọi lại, khuyến mãi gói ưu đãi hoặc gia hạn hợp đồng cho nhóm có nguy cơ cao.")
    elif recall >= 0.55:
        advice.append("📌 Recall ở mức trung bình: nên kết hợp thêm kiểm tra hành vi thanh toán, mức tiêu thụ và dịch vụ sử dụng để giảm bỏ sót khách hàng rời mạng.")
    else:
        advice.append("📌 Recall thấp: cần bổ sung cảnh báo sớm bằng dữ liệu hành vi, thời gian sử dụng và dịch vụ đang thiếu để tăng độ nhạy của mô hình.")

    if f1 >= 0.60:
        advice.append("📈 F1-score tốt: mô hình cân bằng giữa phát hiện chính xác và tránh nhầm lẫn. Tiếp tục theo dõi nhưng vẫn nên có chiến lược chăm sóc chủ động.")
    else:
        advice.append("📉 F1-score còn thấp: cần cải thiện độ chính xác bằng cách tăng dữ liệu, điều chỉnh ngưỡng cảnh báo hoặc kiểm tra thêm biến có tác động lớn đến churn.")

    if churn_probability >= 0.50 or prediction == "Yes":
        advice.append("⚠️ Khách hàng có nguy cơ rời mạng > 50%: nên triển khai ưu đãi 10–15%, tư vấn gói mới, hoặc đề xuất hợp đồng dài hạn trong 24–72 giờ tới.")
    elif churn_probability >= 0.30:
        advice.append("🟡 Khách hàng ở mức rủi ro trung bình: gửi tin nhắn chăm sóc, thúc đẩy sử dụng các gói bảo vệ và dịch vụ đa tiện ích để giữ chân khách hàng.")
    else:
        advice.append("🟢 Khách hàng ở mức rủi ro thấp: tiếp tục duy trì chất lượng dịch vụ và tạo các chương trình bảo lưu khách hàng dài hạn.")

    if accuracy >= 0.78:
        advice.append("✅ Accuracy cao: mô hình phân loại tổng quát ổn định. Có thể dùng làm công cụ hỗ trợ ưu tiên chăm sóc khách hàng trong thực tế.")

    return advice


def render_sidebar():
    st.sidebar.title("⚙️ Cấu hình Mô hình")
    model_choice = st.sidebar.selectbox(
        "Chọn mô hình thực thi:",
        options=[
            ("baseline_decision_tree_A", "Baseline (Decision Tree Mặc định) - Luồng A"),
            ("decision_tree_A", "Decision Tree - Luồng A"),
            ("decision_tree_B", "Decision Tree - Luồng B"),
            ("knn_A", "K-NN - Luồng A"),
            ("knn_B", "K-NN - Luồng B"),
        ],
        format_func=lambda item: item[1],
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
        real_customer_df = pd.read_csv(RAW_CUSTOMER_CSV) if RAW_CUSTOMER_CSV.exists() else pd.DataFrame()

        source_option = st.radio(
            "Nguồn dữ liệu dự đoán:",
            ["Dữ liệu khách hàng thực tế từ tập dữ liệu", "Nhập tay"],
            horizontal=True,
        )

        if source_option == "Dữ liệu khách hàng thực tế từ tập dữ liệu" and not real_customer_df.empty:
            customer_index = st.selectbox(
                "Chọn khách hàng thực tế để dự đoán:",
                options=real_customer_df.index,
                format_func=lambda idx: f"{real_customer_df.loc[idx, 'customerID']} | {real_customer_df.loc[idx, 'Contract']} | Churn={real_customer_df.loc[idx, 'Churn']}",
            )
            selected_customer = real_customer_df.loc[customer_index].copy()
            st.caption(f"Đang dùng dữ liệu thực tế của khách hàng: **{selected_customer['customerID']}**")

            defaults = {
                "gender": selected_customer.get("gender", "Female"),
                "SeniorCitizen": int(selected_customer.get("SeniorCitizen", 0)),
                "Partner": selected_customer.get("Partner", "No"),
                "Dependents": selected_customer.get("Dependents", "No"),
                "tenure": int(selected_customer.get("tenure", 0)),
                "PhoneService": selected_customer.get("PhoneService", "Yes"),
                "MultipleLines": selected_customer.get("MultipleLines", "No"),
                "InternetService": selected_customer.get("InternetService", "Fiber optic"),
                "OnlineSecurity": selected_customer.get("OnlineSecurity", "No"),
                "OnlineBackup": selected_customer.get("OnlineBackup", "No"),
                "DeviceProtection": selected_customer.get("DeviceProtection", "No"),
                "TechSupport": selected_customer.get("TechSupport", "No"),
                "StreamingTV": selected_customer.get("StreamingTV", "No"),
                "StreamingMovies": selected_customer.get("StreamingMovies", "No"),
                "Contract": selected_customer.get("Contract", "Month-to-month"),
                "PaperlessBilling": selected_customer.get("PaperlessBilling", "No"),
                "PaymentMethod": selected_customer.get("PaymentMethod", "Electronic check"),
                "MonthlyCharges": float(selected_customer.get("MonthlyCharges", 79.85)),
                "TotalCharges": float(selected_customer.get("TotalCharges", 0.0) if pd.notna(selected_customer.get("TotalCharges", 0.0)) else 0.0),
            }
        else:
            # Thiết lập giá trị mặc định theo preset nếu người dùng chọn nhập tay
            col_preset1, col_preset2 = st.columns([2, 1])
            with col_preset1:
                preset = st.radio(
                    "Tải hồ sơ mẫu nhanh:",
                    ["Nhập tùy chỉnh", "Mẫu 1: Khách hàng nguy cơ rời bỏ cao (Churn)", "Mẫu 2: Khách hàng trung thành (Ở lại)"],
                    horizontal=True,
                )

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
                senior = st.selectbox("Người cao tuổi (Senior Citizen):", [0, 1], format_func=lambda x: "Có" if x == 1 else "Không", index=int(defaults["SeniorCitizen"]))
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
                tenure = st.slider("Thời gian gắn bó (Tháng):", min_value=0, max_value=72, value=int(defaults["tenure"]))
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
                monthly_charges = st.number_input("Cước hàng tháng ($):", min_value=15.0, max_value=150.0, value=float(defaults["MonthlyCharges"]), step=0.5)
                auto_total = float(tenure * monthly_charges)
                total_charges = st.number_input("Tổng cước lũy kế ($):", min_value=0.0, max_value=10000.0, value=float(defaults.get("TotalCharges", auto_total)), step=10.0)

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

            model = resolve_model(models, preprocessor_A, selected_model_id)
            if selected_model_id.endswith("_A"):
                X_input = preprocessor_A.transform(raw_df)
            else:
                X_input = tao_dac_trung_B(raw_df)

            prediction = model.predict(X_input)[0]
            probas = model.predict_proba(X_input)[0]
            class_names = list(model.classes_)
            churn_idx = class_names.index("Yes") if "Yes" in class_names else 1
            no_idx = class_names.index("No") if "No" in class_names else 0
            churn_proba = float(probas[churn_idx])
            stay_proba = float(probas[no_idx])
            risk_label = classify_risk(churn_proba)

            st.markdown("---")
            st.subheader("🎯 Kết Quả Phân Tích & Dự Báo")

            res_col1, res_col2 = st.columns([1, 1])
            with res_col1:
                if prediction == "Yes":
                    st.markdown(
                        """
                        <div class="risk-high">
                            <h3>⚠️ CẢNH BÁO: KHÁCH HÀNG CÓ NGUY CƠ RỜI BỎ (CHURN)</h3>
                            <p>Mô hình dự báo khách hàng này có xác suất cao sẽ hủy dịch vụ trong thời gian tới.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div class="risk-low">
                            <h3>✅ AN TOÀN: KHÁCH HÀNG CÓ XU HƯỚNG Ở LẠI (STAY)</h3>
                            <p>Mô hình nhận định khách hàng đang gắn bó ổn định với nhà mạng.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with res_col2:
                st.write(f"**Thuật toán đang chạy:** `{get_model_display_name(selected_model_id)}`")
                st.write(f"**Xác suất rời bỏ (Churn Probability):** `{churn_proba * 100:.1f}%`")
                st.write(f"**Xác suất ở lại (Stay Probability):** `{stay_proba * 100:.1f}%`")
                st.progress(churn_proba)
                st.caption(f"🔴 Mức độ rủi ro: **{risk_label.upper()}**")

            model_metrics = get_model_comparison_metrics(selected_model_id)
            model_accuracy = float(model_metrics.get("accuracy", 0.0) or 0.0)
            model_recall = float(model_metrics.get("recall", 0.0) or 0.0)
            model_f1 = float(model_metrics.get("f1_score", 0.0) or 0.0)

            result_df = pd.DataFrame([
                {
                    "Tên Thuật Toán & Luồng đang chạy": get_model_display_name(selected_model_id),
                    "Nhãn Dự Đoán (Rời mạng / Ở lại)": "Rời mạng" if prediction == "Yes" else "Ở lại",
                    "Accuracy": round(model_accuracy, 4),
                    "Recall": round(model_recall, 4),
                    "F1-score": round(model_f1, 4),
                    "Xác suất rời mạng (%)": round(churn_proba * 100, 2),
                    "Xác suất ở lại (%)": round(stay_proba * 100, 2),
                    "Mức độ rủi ro (Thấp / Trung bình / Cao)": risk_label,
                }
            ])

            st.markdown("#### 📊 Bảng Kết Quả Chạy Thuật Toán")
            result_col, note_col = st.columns([1.7, 1.3])

            with result_col:
                st.dataframe(result_df, use_container_width=True, hide_index=True)

            with note_col:
                st.markdown("#### 📝 Ghi chú mô hình")
                st.info(
                    f"- Accuracy: **{model_accuracy:.4f}**\n"
                    f"- Recall: **{model_recall:.4f}**\n"
                    f"- F1-score: **{model_f1:.4f}**\n\n"
                    "Mô hình này đang được đánh giá trên tập Test chung của đề tài; nếu mục tiêu ưu tiên là phát hiện khách hàng rời mạng, Recall và F1-score là chỉ số quan trọng hơn Accuracy."
                )

                model_notes = build_model_advice(model_metrics, churn_proba, prediction)
                for note in model_notes:
                    st.info(note)

            st.markdown("#### 🛠️ Khuyến nghị hành động chi tiết")
            if churn_proba >= 0.5:
                st.info(
                    "📌 **Khách hàng có nguy cơ rời mạng cao (>50%)**. Nên chủ động đề xuất gói ưu đãi, khuyến mãi 10–15% trong 3 tháng, hoặc gia hạn hợp đồng dài hạn để giảm nguy cơ mất khách. "
                    "Bộ phận CSKH nên ưu tiên gọi lại, kiểm tra các vấn đề về cước, dịch vụ Internet và kỹ thuật hỗ trợ để giải quyết nhanh trước khi khách hàng chuyển nhà mạng."
                )
            elif churn_proba >= 0.3:
                st.info(
                    "📌 **Khách hàng ở mức rủi ro trung bình**. Nên gửi tin nhắn chăm sóc riêng, nhắc khách hàng về các tiện ích đang sử dụng và đề xuất nâng cấp gói phù hợp với mức tiêu thụ hiện tại."
                )
            else:
                st.info(
                    "📌 **Khách hàng ở mức rủi ro thấp**. Tiếp tục duy trì chất lượng dịch vụ, theo dõi mức độ hài lòng và tạo các ưu đãi bảo lưu khách hàng để giảm khả năng thoát ra sau này."
                )

            if contract == "Month-to-month":
                st.info("📌 **Hợp đồng từng tháng:** Đây là yếu tố hàng đầu gây Churn. Hãy đề xuất ưu đãi nếu khách hàng chuyển sang hợp đồng 1 năm/2 năm.")
            if security == "No" or support == "No":
                st.info("📌 **Thiếu dịch vụ bảo vệ/hỗ trợ:** Nên gợi ý gói Online Security hoặc Tech Support dùng thử miễn phí trong 3 tháng.")
            if payment == "Electronic check":
                st.info("📌 **Thanh toán qua Electronic check:** Khuyến khích chuyển sang Auto-Pay qua thẻ/nhà băng để giảm rủi ro hao hụt và cải thiện trải nghiệm.")

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
