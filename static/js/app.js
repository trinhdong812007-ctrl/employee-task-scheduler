// Đồng hồ + ngày hiện tại trên topbar
function updateClock() {
  const now = new Date();
  const clockEl = document.getElementById("clockNow");
  const dateEl = document.getElementById("dateNow");
  if (clockEl) {
    clockEl.textContent = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
  if (dateEl) {
    const days = ["Chủ nhật","Thứ hai","Thứ ba","Thứ tư","Thứ năm","Thứ sáu","Thứ bảy"];
    const d = String(now.getDate()).padStart(2,'0');
    const m = String(now.getMonth()+1).padStart(2,'0');
    dateEl.textContent = `${days[now.getDay()]}, ${d}/${m}/${now.getFullYear()}`;
  }
}
setInterval(updateClock, 1000);
updateClock();

// Toggle sidebar (mobile)
const hamburgerBtn = document.getElementById("hamburgerBtn");
if (hamburgerBtn) {
  hamburgerBtn.addEventListener("click", () => {
    document.getElementById("sidebar").classList.toggle("open");
  });
}

// Kiểm tra trùng ca theo thời gian thực trên trang Phân công
function initConflictCheck() {
  const empSel = document.getElementById("employee_id");
  const dateInput = document.getElementById("ngay_lam_viec");
  const caRadios = document.querySelectorAll('input[name="ca"]');
  const warnBox = document.getElementById("conflictWarning");
  const submitBtn = document.getElementById("submitAssignBtn");

  if (!empSel || !dateInput || !warnBox) return;

  async function checkConflict() {
    const employee_id = empSel.value;
    const ngay = dateInput.value;
    const caChecked = document.querySelector('input[name="ca"]:checked');
    const ca = caChecked ? caChecked.value : null;

    if (!employee_id || !ngay || !ca) {
      warnBox.classList.add("d-none");
      return;
    }
    try {
      const res = await fetch(`/api/check_conflict?employee_id=${employee_id}&ngay_lam_viec=${ngay}&ca=${encodeURIComponent(ca)}`);
      const data = await res.json();
      if (data.conflict) {
        warnBox.classList.remove("d-none");
        warnBox.textContent = `⚠️ Nhân viên đã có lịch "${data.task_name}" trong ca này. Vui lòng chọn ca hoặc ngày khác.`;
        if (submitBtn) submitBtn.disabled = true;
      } else {
        warnBox.classList.add("d-none");
        if (submitBtn) submitBtn.disabled = false;
      }
    } catch (e) {
      warnBox.classList.add("d-none");
    }
  }

  empSel.addEventListener("change", checkConflict);
  dateInput.addEventListener("change", checkConflict);
  caRadios.forEach(r => r.addEventListener("change", checkConflict));
}
document.addEventListener("DOMContentLoaded", initConflictCheck);
