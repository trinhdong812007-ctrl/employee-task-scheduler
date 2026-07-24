Lập lịch công việc cho nhân viên

Hệ thống phân tích công việc nhân viên theo tuần — đồ án môn Lập trình Python.

Công nghệ ứng dụng
Python 3.10 trở lên
Bình
SQLite + SQLAlchemy (Flask-SQLAlchemy)
HTML5, CSS3, Bootstrap 5, Biểu tượng Bootstrap
Mẫu Jinja2
Cấu trúc dự án
employee_task_scheduler/
├── applist.py              # File chạy chính: models, routes, business logic
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
├── templates/
│   ├── base.html           # Layout chung (sidebar + topbar, tích hợp Dark Theme CSS)
│   ├── dashboard.html      # Trang Dashboard
│   ├── employees.html      # Quản lý nhân viên (CRUD + tìm kiếm)
│   ├── tasks.html          # Quản lý công việc (CRUD + tìm kiếm)
│   ├── task_assign.html    # Phân công công việc (chọn NV, xem phân công gần đây, xóa phân công)
│   ├── lich_trinh.html     # Lịch làm việc theo tuần (dạng bảng grid)
│   ├── reports.html        # Báo cáo / thống kê
│   └── import_data.html    # Nhập dữ liệu từ Excel / CSV
└── static/
    ├── css/style.css
    ├── js/app.js
    └── img/logo.svg
Cài đặt &
đập
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python applist.py

Open browser at: http://127.0.0.1:5000

SQLite cơ sở dữ liệu ( scheduler.db) sẽ tự động được tạo và tải mẫu dữ liệu khi chạy ứng dụng lần đầu.

Chức năng chính & Cập nhật mới
Mô-đun	Mô tả
Bảng điều khiển	Thống kê tổng quan (tập NV, tổng CV, tổng lịch, số NV làm việc hôm nay), bảng phân công nhanh, xem trước lịch tuần.
quản lý nhân viên	Thêm / Chỉnh sửa / Xóa / Tìm kiếm — mã NV, họ tên, email, SĐT, bộ phận, chức năng.
Quản lý công	Thêm / Chỉnh sửa / Xóa / Tìm kiếm — mã CV, tên, mô tả, mức độ ưu tiên, thời lượng.
Phân công công	Chọn công việc, nhân viên tự động sẵn sàng. Hỗ trợ xóa phân tích trực tiếp (nút thùng rác) trong danh sách phân tích gần đây.
lịch làm việc tuần	Xem dạng mạng (Thứ 2 → Thứ 7, theo ca) hoặc dạng danh sách. Chỉ hiển thị các công việc đã được phân tích (các công việc chưa được giao hoặc bị hủy bỏ sẽ tự động ẩn). Hỗ trợ hiển thị nhiều công việc cùng một ngày/ngày.
vật liệu	Cho phép tải lên danh sách nhân viên / công việc dữ liệu từ tệp Excel/CSV.
Báo cáo	Thống kê khối lượng công việc theo từng nhân viên và theo bộ phận.
Giao diện & logic cải tiến (cập nhật mới)
Lịch trình ưu tiên: Kết nối dữ liệu dưới dạng INNER JOIN giữa bảng Nhiệm vụ và Lịch trình, giúp tự động đồng bộ hiển thị — khi xóa hết nhân viên khỏi công việc, công việc đó sẽ tự động ẩn khỏi lịch trình.
Xử lý hiển thị đa công việc: Một ô (Ngày / Ca) có thể hiển thị danh sách xếp chồng nhiều công việc cùng lúc, phân biệt theo màu ưu tiên (Khẩn cấp, Cao, Trung bình, Thấp).
Cải tiến UI Dark Mode: Đồng bộ bộ chuẩn màu Dark Theme với độ tương phản cao, xử lý triệt để để sao chép màu nền/chữ tối ở các ô Đầu vào, Bảng, Nhãn, Hộp chọn giúp giao diện dễ nhìn và rõ ràng hơn.
Xóa phân công linh hoạt: Bổ sung nút thao tác xóa phân công khó khăn ngay tại trang phân công nhân viên.
Quy tắc nghiệp vụ quan trọng
Hệ thống hoạt động từ Thứ Hai đến Thứ Bảy (nghỉ Chủ Nhật).
Mỗi ngày có 2 ca: Sáng (07 :30 –11 :30 ) và Chiều (13 :00 –17 :00 ) .
Một nhân viên không được phân tích quá 1 công việc trong cùng 1 ca — được xóa ở cơ sở dữ liệu tầng (Ràng buộc duy nhất) và kiểm tra ở tầng ứng dụng trước khi lưu.
Ghi chú sử dụng AI support

Dự án có sử dụng AI (Gemini / Claude) hỗ trợ ban đầu mã nguồn sinh mã, CSS Dark Mode tối ưu hóa và nâng cấp logic lọc lịch trình theo dữ liệu thực tế. Nhóm/sinh viên sử dụng lại mã nguồn này cần:

Đọc và hiểu toàn bộ logic trước khi nộp bài.
Tự kiểm tra các chức năng, đặc biệt là kiểm tra ca trùng lặp và xử lý xóa phân tích.
Xác định rõ các phần báo cáo có hỗ trợ AI theo định nghĩa chính xác.
Hướng phát triển (mở rộng)
Đăng nhập & phân quyền (admin / bộ phận chính).
Xuất lịch làm việc sang Excel / PDF.
Kéo thả (Kéo & Thả) lịch làm việc.
Gửi thông báo qua email khi có công cụ phân tích mới.
Triển khai Render / Railroad.