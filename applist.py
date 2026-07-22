# -*- coding: utf-8 -*-
"""
applist.py
Employee Task Scheduler - Hệ thống phân công công việc nhân viên
Đồ án môn: Lập trình Python (Flask + SQLite + SQLAlchemy)

Cách chạy:
    pip install -r requirements.txt
    python applist.py
Mặc định chạy tại: http://127.0.0.1:5000
"""

import os
from datetime import datetime, timedelta, date

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

# --------------------------------------------------------------------------
# CẤU HÌNH ỨNG DỤNG
# --------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "employee-task-scheduler-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "scheduler.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------------------------------------------------------------
# HẰNG SỐ DÙNG CHUNG
# --------------------------------------------------------------------------
CA_LAM_VIEC = {
    "Sáng": "07:30 - 11:30",
    "Chiều": "13:00 - 17:00",
}

THU_TRONG_TUAN = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]  # T2 -> T7 (nghỉ CN)

DO_UU_TIEN_LIST = ["Thấp", "Trung bình", "Cao", "Khẩn cấp"]


# --------------------------------------------------------------------------
# MÔ HÌNH DỮ LIỆU (MODELS)
# --------------------------------------------------------------------------
class Employee(db.Model):
    """Bảng Nhân viên"""
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    ma_nv = db.Column(db.String(20), unique=True, nullable=False)
    ho_ten = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    sdt = db.Column(db.String(20))
    bo_phan = db.Column(db.String(80))
    chuc_vu = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship(
        "Schedule", backref="employee", cascade="all, delete-orphan", lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ma_nv": self.ma_nv,
            "ho_ten": self.ho_ten,
            "email": self.email,
            "sdt": self.sdt,
            "bo_phan": self.bo_phan,
            "chuc_vu": self.chuc_vu,
        }


class Task(db.Model):
    """Bảng Công việc"""
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    ma_cv = db.Column(db.String(20), unique=True, nullable=False)
    ten_cv = db.Column(db.String(150), nullable=False)
    mo_ta = db.Column(db.Text)
    do_uu_tien = db.Column(db.String(20), default="Trung bình")
    thoi_luong = db.Column(db.Float, default=1.0)  # đơn vị: giờ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship(
        "Schedule", backref="task", cascade="all, delete-orphan", lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ma_cv": self.ma_cv,
            "ten_cv": self.ten_cv,
            "mo_ta": self.mo_ta,
            "do_uu_tien": self.do_uu_tien,
            "thoi_luong": self.thoi_luong,
        }


class Schedule(db.Model):
    """Bảng Phân công (lịch làm việc)"""
    __tablename__ = "schedule"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    ngay_lam_viec = db.Column(db.Date, nullable=False)
    ca = db.Column(db.String(10), nullable=False)  # 'Sáng' hoặc 'Chiều'
    ghi_chu = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("employee_id", "ngay_lam_viec", "ca", name="uq_emp_day_ca"),
    )


class Page(db.Model):
    """Bảng lưu trữ đường dẫn động (Dynamic Routes)"""
    __tablename__ = "page"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)  # Ví dụ: "huong-dan"
    tieu_de = db.Column(db.String(200), nullable=False)
    noi_dung = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --------------------------------------------------------------------------
# HÀM TIỆN ÍCH
# --------------------------------------------------------------------------
def parse_date(value, default=None):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return default or date.today()


def get_week_start(d: date) -> date:
    """Trả về ngày Thứ Hai của tuần chứa ngày d"""
    return d - timedelta(days=d.weekday())


def check_trung_ca(employee_id, ngay_lam_viec, ca, exclude_id=None):
    """Kiểm tra nhân viên đã có lịch trong ca này của ngày này chưa"""
    query = Schedule.query.filter_by(
        employee_id=employee_id, ngay_lam_viec=ngay_lam_viec, ca=ca
    )
    if exclude_id:
        query = query.filter(Schedule.id != exclude_id)
    return query.first()


# --------------------------------------------------------------------------
# DASHBOARD
# --------------------------------------------------------------------------
@app.route("/")
def dashboard():
    today = date.today()

    tong_nhan_vien = Employee.query.count()
    tong_cong_viec = Task.query.count()
    tong_lich_phan_cong = Schedule.query.count()

    lich_hom_nay = (
        Schedule.query.filter(Schedule.ngay_lam_viec == today)
        .order_by(Schedule.ca)
        .all()
    )
    nhan_vien_hom_nay = len({s.employee_id for s in lich_hom_nay})

    # tuần hiện tại cho preview lịch trên dashboard
    week_start = get_week_start(today)
    week_dates = [week_start + timedelta(days=i) for i in range(6)]
    employees = Employee.query.order_by(Employee.ho_ten).all()
    tasks = Task.query.order_by(Task.ten_cv).all()

    weekly_grid = build_weekly_grid(week_dates, employees)

    cong_viec_hom_nay = (
        db.session.query(Schedule, Employee, Task)
        .join(Employee, Schedule.employee_id == Employee.id)
        .join(Task, Schedule.task_id == Task.id)
        .filter(Schedule.ngay_lam_viec == today)
        .order_by(Schedule.ca)
        .limit(6)
        .all()
    )

    return render_template(
        "dashboard.html",
        tong_nhan_vien=tong_nhan_vien,
        tong_cong_viec=tong_cong_viec,
        tong_lich_phan_cong=tong_lich_phan_cong,
        nhan_vien_hom_nay=nhan_vien_hom_nay,
        week_start=week_start,
        week_dates=week_dates,
        thu_list=THU_TRONG_TUAN,
        employees=employees,
        tasks=tasks,
        weekly_grid=weekly_grid,
        cong_viec_hom_nay=cong_viec_hom_nay,
        today=today,
        now=datetime.now(),
    )


def build_weekly_grid(week_dates, employees):
    """Tạo dữ liệu dạng {employee_id: {date: {'Sáng': Schedule|None, 'Chiều': Schedule|None}}}"""
    grid = {}
    schedules = (
        Schedule.query.filter(
            Schedule.ngay_lam_viec.in_(week_dates)
        ).all()
    )
    lookup = {}
    for s in schedules:
        lookup.setdefault(s.employee_id, {}).setdefault(s.ngay_lam_viec, {})[s.ca] = s

    for emp in employees:
        grid[emp.id] = {}
        for d in week_dates:
            entry = lookup.get(emp.id, {}).get(d, {})
            grid[emp.id][d] = {
                "Sáng": entry.get("Sáng"),
                "Chiều": entry.get("Chiều"),
            }
    return grid


# --------------------------------------------------------------------------
# QUẢN LÝ NHÂN VIÊN
# --------------------------------------------------------------------------
@app.route("/employees")
def employees_page():
    q = request.args.get("q", "").strip()
    query = Employee.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Employee.ma_nv.ilike(like),
                Employee.ho_ten.ilike(like),
                Employee.email.ilike(like),
                Employee.bo_phan.ilike(like),
                Employee.chuc_vu.ilike(like),
            )
        )
    employees = query.order_by(Employee.id.desc()).all()
    return render_template("employees.html", employees=employees, q=q)


@app.route("/employees/add", methods=["POST"])
def employee_add():
    ma_nv = request.form.get("ma_nv", "").strip()
    ho_ten = request.form.get("ho_ten", "").strip()
    email = request.form.get("email", "").strip()
    sdt = request.form.get("sdt", "").strip()
    bo_phan = request.form.get("bo_phan", "").strip()
    chuc_vu = request.form.get("chuc_vu", "").strip()

    if not ma_nv or not ho_ten:
        flash("Mã nhân viên và Họ tên là bắt buộc.", "danger")
        return redirect(url_for("employees_page"))

    if Employee.query.filter_by(ma_nv=ma_nv).first():
        flash(f"Mã nhân viên '{ma_nv}' đã tồn tại.", "danger")
        return redirect(url_for("employees_page"))

    emp = Employee(
        ma_nv=ma_nv, ho_ten=ho_ten, email=email, sdt=sdt,
        bo_phan=bo_phan, chuc_vu=chuc_vu
    )
    db.session.add(emp)
    db.session.commit()
    flash(f"Đã thêm nhân viên '{ho_ten}' thành công.", "success")
    return redirect(url_for("employees_page"))


@app.route("/employees/edit/<int:emp_id>", methods=["POST"])
def employee_edit(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    ma_nv = request.form.get("ma_nv", "").strip()

    trung = Employee.query.filter(
        Employee.ma_nv == ma_nv, Employee.id != emp_id
    ).first()
    if trung:
        flash(f"Mã nhân viên '{ma_nv}' đã được sử dụng bởi nhân viên khác.", "danger")
        return redirect(url_for("employees_page"))

    emp.ma_nv = ma_nv
    emp.ho_ten = request.form.get("ho_ten", "").strip()
    emp.email = request.form.get("email", "").strip()
    emp.sdt = request.form.get("sdt", "").strip()
    emp.bo_phan = request.form.get("bo_phan", "").strip()
    emp.chuc_vu = request.form.get("chuc_vu", "").strip()
    db.session.commit()
    flash("Đã cập nhật thông tin nhân viên.", "success")
    return redirect(url_for("employees_page"))


@app.route("/employees/delete/<int:emp_id>", methods=["POST"])
def employee_delete(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash(f"Đã xóa nhân viên '{emp.ho_ten}'.", "success")
    return redirect(url_for("employees_page"))


# --------------------------------------------------------------------------
# QUẢN LÝ CÔNG VIỆC
# --------------------------------------------------------------------------
@app.route("/tasks")
def tasks_page():
    q = request.args.get("q", "").strip()
    query = Task.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Task.ma_cv.ilike(like), Task.ten_cv.ilike(like), Task.mo_ta.ilike(like))
        )
    tasks = query.order_by(Task.id.desc()).all()
    return render_template("tasks.html", tasks=tasks, q=q, do_uu_tien_list=DO_UU_TIEN_LIST)


@app.route("/tasks/add", methods=["POST"])
def task_add():
    ma_cv = request.form.get("ma_cv", "").strip()
    ten_cv = request.form.get("ten_cv", "").strip()
    mo_ta = request.form.get("mo_ta", "").strip()
    do_uu_tien = request.form.get("do_uu_tien", "Trung bình")
    thoi_luong = request.form.get("thoi_luong", "1")

    if not ma_cv or not ten_cv:
        flash("Mã công việc và Tên công việc là bắt buộc.", "danger")
        return redirect(url_for("tasks_page"))

    if Task.query.filter_by(ma_cv=ma_cv).first():
        flash(f"Mã công việc '{ma_cv}' đã tồn tại.", "danger")
        return redirect(url_for("tasks_page"))

    try:
        thoi_luong_f = float(thoi_luong)
    except ValueError:
        thoi_luong_f = 1.0

    task = Task(
        ma_cv=ma_cv, ten_cv=ten_cv, mo_ta=mo_ta,
        do_uu_tien=do_uu_tien, thoi_luong=thoi_luong_f
    )
    db.session.add(task)
    db.session.commit()
    flash(f"Đã thêm công việc '{ten_cv}' thành công.", "success")
    return redirect(url_for("tasks_page"))


@app.route("/tasks/edit/<int:task_id>", methods=["POST"])
def task_edit(task_id):
    task = Task.query.get_or_404(task_id)
    ma_cv = request.form.get("ma_cv", "").strip()

    trung = Task.query.filter(Task.ma_cv == ma_cv, Task.id != task_id).first()
    if trung:
        flash(f"Mã công việc '{ma_cv}' đã được sử dụng.", "danger")
        return redirect(url_for("tasks_page"))

    task.ma_cv = ma_cv
    task.ten_cv = request.form.get("ten_cv", "").strip()
    task.mo_ta = request.form.get("mo_ta", "").strip()
    task.do_uu_tien = request.form.get("do_uu_tien", "Trung bình")
    try:
        task.thoi_luong = float(request.form.get("thoi_luong", "1"))
    except ValueError:
        task.thoi_luong = 1.0
    db.session.commit()
    flash("Đã cập nhật công việc.", "success")
    return redirect(url_for("tasks_page"))


@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def task_delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash(f"Đã xóa công việc '{task.ten_cv}'.", "success")
    return redirect(url_for("tasks_page"))


# --------------------------------------------------------------------------
# PHÂN CÔNG CÔNG VIỆC
# --------------------------------------------------------------------------
@app.route("/schedule/assign")
def assign_page():
    employees = Employee.query.order_by(Employee.ho_ten).all()
    tasks = Task.query.order_by(Task.ten_cv).all()

    today = date.today()
    recent = (
        db.session.query(Schedule, Employee, Task)
        .join(Employee, Schedule.employee_id == Employee.id)
        .join(Task, Schedule.task_id == Task.id)
        .order_by(Schedule.id.desc())
        .limit(15)
        .all()
    )
    return render_template(
        "schedule_assign.html",
        employees=employees,
        tasks=tasks,
        recent=recent,
        today=today.strftime("%Y-%m-%d"),
    )


@app.route("/schedule/assign", methods=["POST"])
def assign_submit():
    employee_id = request.form.get("employee_id")
    task_id = request.form.get("task_id")
    ngay_str = request.form.get("ngay_lam_viec")
    ca = request.form.get("ca")
    ghi_chu = request.form.get("ghi_chu", "").strip()

    if not employee_id or not task_id or not ngay_str or not ca:
        flash("Vui lòng chọn đầy đủ Nhân viên, Công việc, Ngày và Ca làm việc.", "danger")
        return redirect(url_for("assign_page"))

    ngay = parse_date(ngay_str)

    # KIỂM TRA TRÙNG CA / TRÙNG LỊCH (yêu cầu bắt buộc 4.3)
    trung = check_trung_ca(int(employee_id), ngay, ca)
    if trung:
        emp = Employee.query.get(employee_id)
        flash(
            f"LỖI: Nhân viên '{emp.ho_ten if emp else employee_id}' đã có lịch làm việc "
            f"trong ca '{ca}' ngày {ngay.strftime('%d/%m/%Y')}. "
            f"Không thể phân công trùng ca!",
            "danger",
        )
        return redirect(url_for("assign_page"))

    schedule = Schedule(
        employee_id=int(employee_id),
        task_id=int(task_id),
        ngay_lam_viec=ngay,
        ca=ca,
        ghi_chu=ghi_chu,
    )
    db.session.add(schedule)
    db.session.commit()
    flash("Phân công công việc thành công!", "success")
    return redirect(url_for("assign_page"))


@app.route("/schedule/delete/<int:sch_id>", methods=["POST"])
def schedule_delete(sch_id):
    sch = Schedule.query.get_or_404(sch_id)
    db.session.delete(sch)
    db.session.commit()
    flash("Đã xóa lịch phân công.", "success")
    return redirect(request.referrer or url_for("assign_page"))


# API kiểm tra trùng ca theo thời gian thực (dùng cho JS phía client)
@app.route("/api/check_conflict")
def api_check_conflict():
    employee_id = request.args.get("employee_id", type=int)
    ngay_str = request.args.get("ngay_lam_viec")
    ca = request.args.get("ca")
    if not employee_id or not ngay_str or not ca:
        return jsonify({"conflict": False})
    ngay = parse_date(ngay_str)
    trung = check_trung_ca(employee_id, ngay, ca)
    if trung:
        return jsonify({
            "conflict": True,
            "task_name": trung.task.ten_cv,
        })
    return jsonify({"conflict": False})


# --------------------------------------------------------------------------
# LỊCH LÀM VIỆC THEO TUẦN
# --------------------------------------------------------------------------
@app.route("/schedule/week")
def week_page():
    start_param = request.args.get("start")
    if start_param:
        anchor = parse_date(start_param)
    else:
        anchor = date.today()
    week_start = get_week_start(anchor)
    week_dates = [week_start + timedelta(days=i) for i in range(6)]

    employees = Employee.query.order_by(Employee.ho_ten).all()
    weekly_grid = build_weekly_grid(week_dates, employees)

    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)

    view = request.args.get("view", "grid")  # grid | list

    list_items = []
    if view == "list":
        list_items = (
            db.session.query(Schedule, Employee, Task)
            .join(Employee, Schedule.employee_id == Employee.id)
            .join(Task, Schedule.task_id == Task.id)
            .filter(Schedule.ngay_lam_viec.in_(week_dates))
            .order_by(Schedule.ngay_lam_viec, Schedule.ca)
            .all()
        )

    return render_template(
        "weekly_schedule.html",
        week_start=week_start,
        week_dates=week_dates,
        thu_list=THU_TRONG_TUAN,
        employees=employees,
        weekly_grid=weekly_grid,
        prev_week=prev_week.strftime("%Y-%m-%d"),
        next_week=next_week.strftime("%Y-%m-%d"),
        today_str=date.today().strftime("%Y-%m-%d"),
        view=view,
        list_items=list_items,
    )


# --------------------------------------------------------------------------
# BÁO CÁO / THỐNG KÊ
# --------------------------------------------------------------------------
@app.route("/reports")
def reports_page():
    # Thống kê khối lượng công việc theo từng nhân viên
    employees = Employee.query.order_by(Employee.ho_ten).all()
    stats = []
    for emp in employees:
        count = Schedule.query.filter_by(employee_id=emp.id).count()
        total_hours = (
            db.session.query(db.func.sum(Task.thoi_luong))
            .join(Schedule, Schedule.task_id == Task.id)
            .filter(Schedule.employee_id == emp.id)
            .scalar()
            or 0
        )
        stats.append({
            "employee": emp,
            "so_luong_ca": count,
            "tong_gio": round(total_hours, 1),
        })
    stats.sort(key=lambda x: x["so_luong_ca"], reverse=True)

    tong_lich = Schedule.query.count()
    tong_nv_co_lich = db.session.query(Schedule.employee_id).distinct().count()

    # Thống kê theo bộ phận
    bo_phan_stats = {}
    for emp in employees:
        bp = emp.bo_phan or "Chưa phân loại"
        bo_phan_stats[bp] = bo_phan_stats.get(bp, 0) + Schedule.query.filter_by(employee_id=emp.id).count()

    return render_template(
        "reports.html",
        stats=stats,
        tong_lich=tong_lich,
        tong_nv_co_lich=tong_nv_co_lich,
        bo_phan_stats=bo_phan_stats,
    )


# --------------------------------------------------------------------------
# DYNAMIC ROUTING (ĐƯỜNG DẪN ĐỘNG)
# --------------------------------------------------------------------------
@app.route("/p/<path:slug>")
def dynamic_page(slug):
    """Trang hiển thị nội dung động từ Database theo đường dẫn (slug)"""
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        return "Trang không tồn tại (404)", 404
    return render_template("dynamic_page.html", page=page)


@app.route("/pages/add", methods=["POST"])
def page_add():
    """Tạo đường dẫn động mới và lưu vào cơ sở dữ liệu"""
    slug = request.form.get("slug", "").strip()
    tieu_de = request.form.get("tieu_de", "").strip()
    noi_dung = request.form.get("noi_dung", "").strip()

    if not slug or not tieu_de:
        flash("Slug và Tiêu đề là bắt buộc.", "danger")
        return redirect(url_for("dashboard"))

    if Page.query.filter_by(slug=slug).first():
        flash(f"Đường dẫn '/p/{slug}' đã tồn tại!", "danger")
        return redirect(url_for("dashboard"))

    new_page = Page(slug=slug, tieu_de=tieu_de, noi_dung=noi_dung)
    db.session.add(new_page)
    db.session.commit()

    flash(f"Đã tạo đường dẫn mới: /p/{slug}", "success")
    return redirect(url_for("dynamic_page", slug=slug))


# --------------------------------------------------------------------------
# KHỞI TẠO DATABASE + DỮ LIỆU MẪU
# --------------------------------------------------------------------------
def seed_data():
    if Employee.query.count() > 0:
        return

    demo_employees = [
        Employee(ma_nv="NV001", ho_ten="Nguyễn Văn A", email="nguyenvana@company.com", sdt="0901000001", bo_phan="Kỹ thuật", chuc_vu="Nhân viên kỹ thuật"),
        Employee(ma_nv="NV002", ho_ten="Trần Thị B", email="tranthib@company.com", sdt="0901000002", bo_phan="Kinh doanh", chuc_vu="Nhân viên kinh doanh"),
        Employee(ma_nv="NV003", ho_ten="Lê Văn C", email="levanc@company.com", sdt="0901000003", bo_phan="Kế toán", chuc_vu="Kế toán viên"),
        Employee(ma_nv="NV004", ho_ten="Phạm Thị D", email="phamthid@company.com", sdt="0901000004", bo_phan="Hành chính", chuc_vu="Nhân viên hành chính"),
        Employee(ma_nv="NV005", ho_ten="Hoàng Văn E", email="hoangvane@company.com", sdt="0901000005", bo_phan="IT Support", chuc_vu="Nhân viên IT"),
    ]
    db.session.add_all(demo_employees)

    demo_tasks = [
        Task(ma_cv="CV001", ten_cv="Kiểm tra thiết bị", mo_ta="Kiểm tra tình trạng thiết bị định kỳ", do_uu_tien="Cao", thoi_luong=4),
        Task(ma_cv="CV002", ten_cv="Sửa chữa", mo_ta="Sửa chữa thiết bị hỏng", do_uu_tien="Cao", thoi_luong=4),
        Task(ma_cv="CV003", ten_cv="Bảo trì máy móc", mo_ta="Bảo trì định kỳ máy móc", do_uu_tien="Trung bình", thoi_luong=4),
        Task(ma_cv="CV004", ten_cv="Tư vấn KH", mo_ta="Tư vấn khách hàng", do_uu_tien="Trung bình", thoi_luong=4),
        Task(ma_cv="CV005", ten_cv="Chăm sóc KH", mo_ta="Chăm sóc khách hàng sau bán", do_uu_tien="Trung bình", thoi_luong=4),
        Task(ma_cv="CV006", ten_cv="Nhập liệu", mo_ta="Nhập liệu dữ liệu kế toán", do_uu_tien="Thấp", thoi_luong=4),
        Task(ma_cv="CV007", ten_cv="Đối chiếu", mo_ta="Đối chiếu số liệu sổ sách", do_uu_tien="Trung bình", thoi_luong=4),
        Task(ma_cv="CV008", ten_cv="Văn thư", mo_ta="Công tác văn thư lưu trữ", do_uu_tien="Thấp", thoi_luong=4),
        Task(ma_cv="CV009", ten_cv="Hỗ trợ IT", mo_ta="Hỗ trợ kỹ thuật IT cho nhân viên", do_uu_tien="Cao", thoi_luong=4),
        Task(ma_cv="CV010", ten_cv="Backup dữ liệu", mo_ta="Sao lưu dữ liệu hệ thống", do_uu_tien="Khẩn cấp", thoi_luong=2),
    ]
    db.session.add_all(demo_tasks)
    db.session.commit()

    today = date.today()
    monday = get_week_start(today)
    pairs = [
        (0, 0, 0, "Sáng"), (0, 0, 2, "Chiều"),
        (1, 1, 3, "Sáng"), (1, 1, 4, "Chiều"),
        (2, 2, 5, "Sáng"), (2, 2, 6, "Chiều"),
    ]
    for emp_idx, day_idx, task_idx, ca in pairs:
        sch = Schedule(
            employee_id=demo_employees[emp_idx].id,
            task_id=demo_tasks[task_idx].id,
            ngay_lam_viec=monday + timedelta(days=day_idx),
            ca=ca,
        )
        db.session.add(sch)
    db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)