# Thư mục kết quả mô hình

Hùng cần nhận **4 kết quả** sau:

1. `decision_tree_A` - Đức - Decision Tree trên Luồng A
2. `decision_tree_B` - Đức - Decision Tree trên Luồng B
3. `knn_A` - Hải - K-NN trên Luồng A
4. `knn_B` - Hải - K-NN trên Luồng B

Mỗi kết quả tạo một file `.json` dựa theo `result_template.json`, ví dụ:

- `duc_decision_tree_A.json`
- `duc_decision_tree_B.json`
- `hai_knn_A.json`
- `hai_knn_B.json`

Không điền số giả. Chỉ điền số sau khi chạy mô hình thật trên đúng tập Test chung.

Khi đủ 4 file, chạy từ thư mục gốc dự án:

```bash
python -m src.aggregate_results
```

Chương trình sẽ tạo/cập nhật `report/model_comparison.csv`.
