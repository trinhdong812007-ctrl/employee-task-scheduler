import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from applist import validate_employee_payload, validate_task_payload


def test_employee_validation_requires_core_fields():
    errors = validate_employee_payload({"ma_nv": "", "ho_ten": ""})
    assert any("Mã nhân viên" in e for e in errors)
    assert any("Họ tên" in e for e in errors)


def test_task_validation_requires_core_fields():
    errors = validate_task_payload({"ma_cv": "", "ten_cv": ""})
    assert any("Mã công việc" in e for e in errors)
    assert any("Tên công việc" in e for e in errors)


def test_employee_validation_accepts_complete_payload():
    data = {
        "ma_nv": "NV100",
        "ho_ten": "Nguyễn Văn A",
        "email": "a@example.com",
        "bo_phan": "IT Support",
        "vi_tri": "Nhân viên IT",
        "trinh_do": "Khá",
    }
    assert validate_employee_payload(data) == []


def test_task_validation_accepts_complete_payload():
    data = {
        "ma_cv": "CV100",
        "ten_cv": "Test task",
        "ghi_chu": "",
        "do_uu_tien": "Cao",
        "ngay_gio": "2026-07-23",
        "bo_phan": "Kinh doanh",
        "so_luong_nv": 2,
        "thoi_luong": 4.5,
    }
    assert validate_task_payload(data) == []
