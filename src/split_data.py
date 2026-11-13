"""Hàm chia dữ liệu thống nhất cho dự án.

Theo phân công, Mạnh là người thực hiện bước chia dữ liệu chính thức.
File này giữ quy ước chung để các thành viên không dùng sai random_state
hoặc quên stratify=y.
"""

from sklearn.model_selection import train_test_split

from .config import RANDOM_STATE, TEST_SIZE


def chia_du_lieu(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE):
    """Chia dữ liệu train/test và giữ nguyên tỷ lệ lớp bằng stratify=y."""
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
