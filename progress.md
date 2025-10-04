# Nhật Ký Phát Triển - Trình Quản Lý Mật Khẩu

Đây là tài liệu theo dõi tiến độ triển khai dự án dựa trên roadmap đã đề ra trong file `desc.md`.

## Giai đoạn 1: Nền tảng

- [x] **Bước 1: Thiết lập môi trường**
    - [x] Cài đặt Python 3.
    - [x] Tạo môi trường ảo (virtual environment).
    - [x] Cài đặt thư viện `PySide6`.
    - [x] Cài đặt thư viện `cryptography`.

## Giai đoạn 2: Xây dựng Lõi

- [x] **Bước 2: Xây dựng lõi mã hóa (`crypto_logic.py`)**
    - [x] Viết hàm `derive_key(password, salt)` sử dụng `PBKDF2HMAC`.
    - [x] Viết hàm `encrypt(data, key)` sử dụng `AESGCM` để trả về `(nonce, ciphertext)`.
    - [x] Viết hàm `decrypt(nonce, ciphertext, key)` để giải mã và xác thực dữ liệu.
    - [x] Viết unit test cho các hàm mã hóa để đảm bảo hoạt động chính xác.

- [x] **Bước 3: Xây dựng logic quản lý file (`vault_manager.py`)**
    - [x] Viết hàm `save_vault(file_path, salt, nonce, ciphertext)` để lưu dữ liệu vào file.
    - [x] Viết hàm `load_vault(file_path)` để đọc dữ liệu từ file.
    - [x] Xử lý các trường hợp lỗi (ví dụ: file không tồn tại).

## Giai đoạn 3: Giao diện Người dùng (UI)

- [x] **Bước 4: Thiết kế và Xây dựng Giao diện**
    - [x] Thiết kế cửa sổ "Tạo Mật khẩu chủ" (cho lần đầu sử dụng).
    - [x] Thiết kế cửa sổ "Mở khóa" (yêu cầu Mật khẩu chủ).
    - [x] Thiết kế cửa sổ chính hiển thị danh sách mật khẩu (dùng `QTableWidget` hoặc `QListView`).
    - [x] Thiết kế cửa sổ "Thêm/Sửa" thông tin đăng nhập.
    - [x] Chuyển các file thiết kế `.ui` (từ Qt Designer) thành code Python.

- [x] **Bước 5: Tích hợp Logic vào Giao diện**
    - [x] Kết nối sự kiện "Mở khóa" với logic `load_vault`, `derive_key`, và `decrypt`.
    - [x] Kết nối sự kiện "Lưu" (thêm/sửa) với logic mã hóa lại toàn bộ dữ liệu và `save_vault`.
    - [x] Hiển thị dữ liệu đã giải mã lên giao diện chính.
    - [x] Xử lý luồng tạo két sắt mới và lưu `salt`.

## Giai đoạn 4: Hoàn thiện và Mở rộng

- [x] **Bước 6: Hoàn thiện các tính năng cốt lõi**
    - [x] Hoàn thiện chức năng Thêm/Sửa/Xóa các mục đăng nhập.
    - [x] Thêm tính năng "Sao chép vào clipboard" một cách an toàn.
    - [x] Thêm chức năng tìm kiếm trong danh sách mật khẩu.

- [x] **Bước 7: Các tính năng mở rộng (Tùy chọn)**
    - [ ] Thêm chức năng "Tạo mật khẩu ngẫu nhiên".
    - [ ] Thêm chỉ báo độ mạnh của Mật khẩu chủ.
    - [x] Tự động khóa ứng dụng sau một khoảng thời gian không hoạt động.

## Giai đoạn 5: Đóng gói và Phát hành

- [x] Cài đặt `PyInstaller`.
- [x] Tạo tệp `pyvault.spec` để cấu hình quá trình đóng gói.
- [x] Xây dựng ứng dụng cho Linux bằng PyInstaller.
- [x] Cập nhật tài liệu `README.md` với hướng dẫn sử dụng phiên bản đã đóng gói.
- [x] Hoàn thành phiên bản 1.0.0 của PyVault.

## Tổng kết Phiên bản 1.0.0

Phiên bản đầu tiên của PyVault đã được hoàn thành với đầy đủ các tính năng cốt lõi:

✅ **Bảo mật hàng đầu**: Mã hóa AES-256-GCM với PBKDF2 key derivation
✅ **Quản lý mật khẩu**: Thêm, sửa, xóa và tìm kiếm thông tin đăng nhập
✅ **Sao chép an toàn**: Tự động xóa clipboard sau 30 giây
✅ **Tự động khóa**: Khóa vault sau 5 phút không hoạt động
✅ **Giao diện hiện đại**: UI thân thiện được xây dựng với PySide6
✅ **Đóng gói sẵn sàng**: Tệp thực thi độc lập cho Linux

**Các tính năng sẽ phát triển trong tương lai:**
- Tối ưu hóa tạo mật khẩu ngẫu nhiên
- Chỉ báo độ mạnh mật khẩu nâng cao
- Đóng gói cho Windows và macOS
- Đồng bộ hóa đám mây (tùy chọn)
- Import/Export dữ liệu
