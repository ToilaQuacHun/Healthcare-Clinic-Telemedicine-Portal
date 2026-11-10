
# 🏥 MediConnect – Healthcare Clinic & Telemedicine Management System

**Đồ án môn học:** Cơ sở dữ liệu (INT1313)  
**Nhóm thực hiện:** G2  
**Trường:** Học viện Công nghệ Bưu chính Viễn thông – Cơ sở TP.HCM

## 📌 1. Giới thiệu dự án

**MediConnect** là hệ thống quản lý phòng khám và hỗ trợ khám bệnh từ xa, được xây dựng nhằm quản lý thông tin bệnh nhân, bác sĩ, lịch khám, hồ sơ bệnh án và đơn thuốc.

Dự án được phát triển bằng **MySQL và Python Flask**, với giao diện web hỗ trợ ba vai trò:

- **ADMIN:** Quản lý hệ thống, bác sĩ, bệnh nhân, lịch khám và đơn thuốc.
- **DOCTOR:** Xem lịch khám, tạo lịch hẹn và kê đơn thuốc.
- **PATIENT:** Đặt lịch khám, theo dõi lịch hẹn và xem đơn thuốc cá nhân.

## 🛠️ 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Database | MySQL 8.x |
| Database Design | MySQL Workbench |
| Backend | Python, Flask |
| Frontend | HTML, CSS, Bootstrap |
| Database Connector | MySQL Connector/Python |
| Version Control | Git, GitHub |
| IDE | Visual Studio Code |

## 📁 3. Cấu trúc thư mục

```text
MediConnect-G2/
│
├── database/
│   ├── tables.sql
│   ├── Triggers.sql
│   ├── Views.sql
│   ├── complex_queries.sql
│   └── Phrase3_full_demo.sql
│
├── docs/
│   ├── G2_BaoCao.pdf
│   ├── diagram.png
│   
│
├── scripts/
├── templates/
├── static/
│
├── app.py
├── db.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

**Lưu ý:** Đây là cấu trúc thư mục dự kiến sau khi nhóm sắp xếp repository. File `Phrase3_full_demo.sql` cần được xuất từ MySQL Workbench nếu chưa có.

## 🚀 4. Hướng dẫn cài đặt và chạy chương trình

### Bước 1: Clone repository

```bash
git clone <URL_REPOSITORY>
cd MediConnect-G2
```

Thay `<URL_REPOSITORY>` bằng đường dẫn GitHub thực tế của nhóm.

### Bước 2: Cài đặt MySQL

1. Cài đặt MySQL Server và MySQL Workbench.
2. Tạo database có tên `Phrase3`.
3. Import file SQL trong thư mục `database/`.

Nếu nhóm đã cung cấp `Phrase3_full_demo.sql` đầy đủ cấu trúc, dữ liệu, Views và Triggers, có thể import file này thay vì chạy riêng từng script.

Không import lại dữ liệu nhiều lần để tránh trùng khóa chính.

### Bước 3: Cài đặt môi trường Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Trên Windows, lệnh kích hoạt môi trường là:

```powershell
.venv\Scripts\activate
```

### Bước 4: Cấu hình kết nối database

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Cập nhật thông tin MySQL trong `.env`:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456

DB_NAME=Phrase3
FLASK_SECRET_KEY=CHANGE_TO_RANDOM_SECRET
```

**Không đưa file `.env` hoặc mật khẩu thật lên GitHub.**

### Bước 5: Khởi động website

```bash
python app.py
```

Truy cập:

**http://127.0.0.1:5000**

Đăng nhập bằng tài khoản đã được thiết lập trong database.

## 👥 5. Thành viên nhóm G2

| STT | Họ và tên | Email |
|---|---|---|
| 1 | Lê Nguyễn Quốc Hùng | n24dece070@student.ptithcm.edu.vn |
| 2 | Trần Hoàng Hải Đăng | n24dece059@student.ptithcm.edu.vn |
| 3 | Trần Quốc Huy | n24dece074@student.ptithcm.edu.vn |

## 📋 6. Bảng phân công công việc

| Thành viên | Công việc thực hiện |
|---|---|
| **Lê Nguyễn Quốc Hùng** | Thực hiện báo cáo Phase 1–4; kiểm tra, chỉnh sửa, tổng hợp và hoàn thiện báo cáo Phase 2–4; thiết kế và triển khai SQL gồm Tables, Primary Keys, Foreign Keys, Indexes, Triggers, Views và Complex Queries; kiểm thử ràng buộc dữ liệu; tổng hợp dữ liệu của nhóm; phát triển và tích hợp website Flask với MySQL trong Phase 4; xây dựng các chức năng đăng nhập, phân quyền, quản lý bác sĩ, bệnh nhân, lịch khám, đơn thuốc; kiểm tra, sửa lỗi hệ thống; quản lý và hoàn thiện mã nguồn trên GitHub. |
| **Trần Hoàng Hải Đăng** | Thực hiện nội dung báo cáo Phase 2–3; tìm kiếm, thu thập và chuẩn bị dữ liệu mẫu; xây dựng dữ liệu SQL phục vụ kiểm thử hệ thống; phối hợp cung cấp dữ liệu cho các bảng liên quan đến lịch hẹn, phiên khám, bệnh án và đơn thuốc. |
| **Trần Quốc Huy** | Thực hiện nội dung báo cáo Phase 2–3; tìm kiếm, thu thập và chuẩn bị dữ liệu mẫu; xây dựng dữ liệu SQL phục vụ kiểm thử hệ thống; phối hợp cung cấp dữ liệu cho các bảng liên quan đến tài khoản, bệnh nhân, bác sĩ và lịch làm việc. |

## 📄 7. Báo cáo và tài liệu

Các nội dung chi tiết được trình bày trong báo cáo của nhóm:

- Phân tích yêu cầu và Business Rules.
- Thiết kế EER Diagram và Logical Schema.
- Chuẩn hóa cơ sở dữ liệu.
- Data Dictionary.
- SQL Queries, Triggers, Views và Indexes.
- Kiểm thử, bảo mật và phân quyền.
- Tích hợp giao diện Flask với MySQL.

**Tài liệu:** [Báo cáo MediConnect G2](https://docs.google.com/document/d/1KDScY3_KR7Hbz158LKo01zvqP5-lz1r8/edit?usp=sharing&ouid=102331205998537801349&rtpof=true&sd=true)

**Sơ đồ EER:** [EER Diagram](docs/diagram.png)

## 📝 8. Ghi chú

- Project được phát triển phục vụ mục đích học tập và nghiên cứu.
- Dữ liệu sử dụng trong bản demo là dữ liệu mô phỏng.
- Các chức năng cần được kiểm thử trên môi trường MySQL trước khi sử dụng.
- Không đưa thông tin đăng nhập, mật khẩu hoặc dữ liệu bệnh nhân thật lên repository công khai.

---

**© Group G2 – INT1313 – Posts and Telecommunications Institute of Technology, HCMC.**
