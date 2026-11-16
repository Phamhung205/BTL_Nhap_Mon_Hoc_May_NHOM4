"""Cấu hình dùng chung cho toàn bộ dự án.

Không tự ý thay đổi RANDOM_STATE giữa các thành viên, vì mọi mô hình
phải được đánh giá trên cùng cách chia dữ liệu.
"""

RANDOM_STATE = 42
TEST_SIZE = 0.20
TARGET_COLUMN = "Churn"
POSITIVE_LABEL = "Yes"

# Phương án Baseline làm mốc đối sánh: Decision Tree mặc định trên Luồng A (chưa tinh chỉnh, class_weight=None)
BASELINE_MODEL_ID = "baseline_decision_tree_A_default"
BASELINE_DESCRIPTION = "Decision Tree mặc định trên Luồng A (depth=None, unweighted)"

# Bốn kết quả Hùng cần thu thập để so sánh chéo.
EXPECTED_RESULT_IDS = (
    "decision_tree_A",
    "decision_tree_B",
    "knn_A",
    "knn_B",
)
