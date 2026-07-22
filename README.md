# Employee Task Scheduler

Hệ thống phân công công việc nhân viên theo tuần — đồ án môn Lập trình Python.

## Công nghệ sử dụng
- Python 3.10+
- Flask
- SQLite + SQLAlchemy (Flask-SQLAlchemy)
- HTML5, Bootstrap 5, Bootstrap Icons

## Cấu trúc dự án
```
employee_task_scheduler/
├── applist.py              # File chạy chính: models, routes, business logic
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
├── templates/
│   ├── base.html           # Layout chung (sidebar + topbar)
│   ├── dashboard.html      # Trang Dashboard
│   ├── employees.html      # Quản lý nhân viên (CRUD + tìm kiếm)
│   ├── tasks.html          # Quản lý công việc (CRUD + tìm kiếm)
│   ├── schedule_assign.html# Phân công công việc
│   ├── weekly_schedule.html# Lịch làm việc theo tuần
│   └── reports.html        # Báo cáo / thống kê
└── static/
    ├── css/style.css
    └── js/app.js
```

## Cài đặt & chạy
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python applist.py
```
Mở trình duyệt tại: **http://127.0.0.1:5000**

Cơ sở dữ liệu SQLite (`scheduler.db`) sẽ tự động được tạo và nạp dữ liệu mẫu
(5 nhân viên, 10 công việc, một vài lịch phân công mẫu) khi chạy lần đầu.

## Chức năng chính
| Module | Mô tả |
|---|---|
| Dashboard | Thống kê tổng quan (tổng NV, tổng CV, tổng lịch, số NV làm việc hôm nay), panel "Phân công nhanh", "Công việc hôm nay", xem trước lịch tuần |
| Quản lý nhân viên | Thêm / Sửa / Xóa / Tìm kiếm — mã NV, họ tên, email, SĐT, bộ phận, chức vụ |
| Quản lý công việc | Thêm / Sửa / Xóa / Tìm kiếm — mã CV, tên, mô tả, độ ưu tiên, thời lượng |
| Phân công công việc | Chọn nhân viên, công việc, ngày, ca — **tự động kiểm tra trùng ca/trùng lịch** (cả phía server và kiểm tra realtime qua API) |
| Lịch làm việc tuần | Xem dạng lưới (Thứ 2 → Thứ 7, theo ca) hoặc dạng danh sách, điều hướng tuần trước/sau |
| Báo cáo | Thống kê khối lượng công việc theo từng nhân viên và theo bộ phận |

## Quy tắc nghiệp vụ quan trọng
- Hệ thống hoạt động từ **Thứ Hai đến Thứ Bảy** (nghỉ Chủ Nhật).
- Mỗi ngày có 2 ca: **Sáng (07:30–11:30)** và **Chiều (13:00–17:00)**.
- Một nhân viên **không được phân công quá 1 công việc trong cùng 1 ca** — được ràng buộc
  ở tầng cơ sở dữ liệu (Unique Constraint) và kiểm tra ở tầng ứng dụng trước khi lưu.

## Ghi chú sử dụng AI hỗ trợ
Dự án có sử dụng AI (Claude) hỗ trợ sinh khung mã nguồn ban đầu (models, routes CRUD,
giao diện Bootstrap). Nhóm/sinh viên sử dụng lại mã nguồn này cần:
- Đọc và hiểu toàn bộ logic trước khi nộp bài.
- Tự kiểm thử các chức năng, đặc biệt là kiểm tra trùng ca.
- Ghi rõ trong báo cáo phần nào có AI hỗ trợ theo đúng yêu cầu mục 8 của đề bài.

## Hướng phát triển (mở rộng)
- Đăng nhập & phân quyền (admin / trưởng bộ phận).
- Xuất lịch làm việc sang Excel / PDF.
- Kéo thả (Drag & Drop) lịch làm việc.
- Gửi thông báo qua email khi có phân công mới.
- Triển khai lên Render / Railway.
