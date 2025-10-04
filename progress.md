# Nhật Ký Phát Triển - Trình Quản Lý Mật Khẩu

Đây là tài liệu theo dõi tiến độ triển khai dự án dựa trên roadmap đã đề ra trong file `desc.md`.

## Giai đoạn 1: Nền tảng

- [ ] **Bước 1: Thiết lập môi trường**
    - [ ] Cài đặt Python 3.
    - [ ] Tạo môi trường ảo (virtual environment).
    - [ ] Cài đặt thư viện `PySide6`.
    - [ ] Cài đặt thư viện `cryptography`.

## Giai đoạn 2: Xây dựng Lõi

- [ ] **Bước 2: Xây dựng lõi mã hóa (`crypto_logic.py`)**
    - [ ] Viết hàm `derive_key(password, salt)` sử dụng `PBKDF2HMAC`.
    - [ ] Viết hàm `encrypt(data, key)` sử dụng `AESGCM` để trả về `(nonce, ciphertext)`.
    - [ ] Viết hàm `decrypt(nonce, ciphertext, key)` để giải mã và xác thực dữ liệu.
    - [ ] Viết unit test cho các hàm mã hóa để đảm bảo hoạt động chính xác.

- [ ] **Bước 3: Xây dựng logic quản lý file (`vault_manager.py`)**
    - [ ] Viết hàm `save_vault(file_path, salt, nonce, ciphertext)` để lưu dữ liệu vào file.
    - [ ] Viết hàm `load_vault(file_path)` để đọc dữ liệu từ file.
    - [ ] Xử lý các trường hợp lỗi (ví dụ: file không tồn tại).

## Giai đoạn 3: Giao diện Người dùng (UI)

- [ ] **Bước 4: Thiết kế và Xây dựng Giao diện**
    - [ ] Thiết kế cửa sổ "Tạo Mật khẩu chủ" (cho lần đầu sử dụng).
    - [ ] Thiết kế cửa sổ "Mở khóa" (yêu cầu Mật khẩu chủ).
    - [ ] Thiết kế cửa sổ chính hiển thị danh sách mật khẩu (dùng `QTableWidget` hoặc `QListView`).
    - [ ] Thiết kế cửa sổ "Thêm/Sửa" thông tin đăng nhập.
    - [ ] Chuyển các file thiết kế `.ui` (từ Qt Designer) thành code Python.

- [ ] **Bước 5: Tích hợp Logic vào Giao diện**
    - [ ] Kết nối sự kiện "Mở khóa" với logic `load_vault`, `derive_key`, và `decrypt`.
    - [ ] Kết nối sự kiện "Lưu" (thêm/sửa) với logic mã hóa lại toàn bộ dữ liệu và `save_vault`.
    - [ ] Hiển thị dữ liệu đã giải mã lên giao diện chính.
    - [ ] Xử lý luồng tạo két sắt mới và lưu `salt`.

## Giai đoạn 4: Hoàn thiện và Mở rộng

- [ ] **Bước 6: Hoàn thiện các tính năng cốt lõi**
    - [ ] Hoàn thiện chức năng Thêm/Sửa/Xóa các mục đăng nhập.
    - [ ] Thêm tính năng "Sao chép vào clipboard" một cách an toàn.
    - [ ] Thêm chức năng tìm kiếm trong danh sách mật khẩu.

- [ ] **Bước 7: Các tính năng mở rộng (Tùy chọn)**
    - [ ] Thêm chức năng "Tạo mật khẩu ngẫu nhiên".
    - [ ] Thêm chỉ báo độ mạnh của Mật khẩu chủ.
    - [ ] Tự động khóa ứng dụng sau một khoảng thời gian không hoạt động.

## Giai đoạn 5: Đóng gói và Phát hành

- [ ] Cài đặt `PyInstaller`.
- [ ] Viết script để đóng gói ứng dụng cho Windows.
- [ ] Viết script để đóng gói ứng dụng cho macOS.
- [ ] Viết script để đóng gói ứng dụng cho Linux.
- [ ] Kiểm thử ứng dụng trên các nền tảng.
