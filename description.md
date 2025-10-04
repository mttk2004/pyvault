# Đồ án: Trình Quản Lý Mật Khẩu Cá Nhân An Toàn

## 1. Giới thiệu

Trong thời đại số, mỗi người dùng sở hữu hàng chục tài khoản trực tuyến. Việc sử dụng mật khẩu yếu hoặc tái sử dụng một mật khẩu cho nhiều dịch vụ là một rủi ro bảo mật cực kỳ lớn. Nếu một dịch vụ bị rò rỉ dữ liệu, tất cả các tài khoản khác của người dùng cũng sẽ bị đe dọa.

**Mục tiêu của đồ án:** Xây dựng một ứng dụng desktop đơn giản, an toàn bằng Python để giải quyết vấn đề trên. Ứng dụng cho phép người dùng lưu trữ thông tin đăng nhập (tên tài khoản, mật khẩu, URL) vào một "két sắt" (vault) kỹ thuật số được mã hóa trên máy tính cá nhân. Toàn bộ két sắt này được bảo vệ bởi một **Mật khẩu chủ (Master Password)** duy nhất.

## 2. Các tính năng cốt lõi

*   **Tạo và Quản lý Két sắt:**
    *   Tạo một két sắt mới được bảo vệ bởi Mật khẩu chủ.
    *   Mở một két sắt đã có bằng Mật khẩu chủ.
*   **Quản lý Thông tin đăng nhập:**
    *   Thêm, sửa, xóa các mục đăng nhập (tên dịch vụ, username, password, URL).
    *   Hiển thị danh sách các mục đã lưu.
    *   Sao chép (copy) mật khẩu vào clipboard một cách an toàn.
*   **Bảo mật:**
    *   Toàn bộ dữ liệu được mã hóa bằng thuật toán mạnh (AES).
    *   Sử dụng kỹ thuật kéo dãn khóa (key stretching) để bảo vệ Mật khẩu chủ khỏi tấn công từ điển.

## 3. Kiến trúc Bảo mật (Phần quan trọng nhất)

Đây là trái tim của ứng dụng, thể hiện các kiến thức đã học. Mô hình bảo mật sẽ không bao giờ lưu trữ Mật khẩu chủ dưới dạng văn bản gốc.

### 3.1. Mật khẩu chủ và Hàm tạo khóa (Key Derivation Function - KDF)

Khi người dùng tạo Mật khẩu chủ, chúng ta không dùng trực tiếp mật khẩu này làm khóa mã hóa. Thay vào đó, ta dùng một **Hàm tạo khóa** như **PBKDF2** (Password-Based Key Derivation Function 2).

*   **Quy trình:** `Khóa mã hóa = PBKDF2(Mật khẩu chủ, Salt, Số vòng lặp)`
*   **Salt (Chuỗi ngẫu nhiên):** Là một chuỗi byte ngẫu nhiên, được tạo ra một lần duy nhất cho mỗi két sắt. Salt sẽ được lưu công khai cùng với file dữ liệu đã mã hóa. Việc sử dụng Salt đảm bảo rằng ngay cả khi hai người dùng có cùng Mật khẩu chủ, khóa mã hóa của họ vẫn sẽ khác nhau.
*   **Số vòng lặp (Iterations):** Là số lần hàm băm được thực hiện lặp đi lặp lại (ví dụ: 100,000 hoặc cao hơn). Việc này làm cho quá trình tạo khóa trở nên chậm một cách có chủ đích, khiến cho kẻ tấn công không thể dùng phương pháp "thử và sai" (brute-force) một cách nhanh chóng.

### 3.2. Mã hóa Dữ liệu (AES-GCM)

Sau khi có được `Khóa mã hóa` từ bước trên, ta sẽ dùng nó để mã hóa toàn bộ dữ liệu của người dùng.

*   **Thuật toán:** Sử dụng **AES (Advanced Encryption Standard)**, một trong những chuẩn mã hóa đối xứng mạnh và phổ biến nhất.
*   **Chế độ hoạt động:** Sử dụng chế độ **GCM (Galois/Counter Mode)**. Chế độ này rất hiện đại vì nó cung cấp cả hai tính năng:
    1.  **Tính bí mật (Confidentiality):** Đảm bảo dữ liệu không thể bị đọc.
    2.  **Tính xác thực (Authenticity):** Đảm bảo dữ liệu không bị sửa đổi trên đường đi hoặc khi đang lưu trữ. Nếu file mã hóa bị thay đổi dù chỉ một bit, quá trình giải mã sẽ thất bại.
*   **Nonce (Initialization Vector - IV):** Là một giá trị ngẫu nhiên phải được tạo mới cho *mỗi lần mã hóa*. Nonce cũng sẽ được lưu công khai cùng file dữ liệu.

### 3.3. Cấu trúc lưu trữ

Toàn bộ két sắt sẽ được lưu trong một file duy nhất (ví dụ: `vault.dat`). File này sẽ chứa:
*   **Salt:** Dùng cho PBKDF2.
*   **Nonce:** Dùng cho AES-GCM.
*   **Ciphertext (Bản mã):** Dữ liệu người dùng (dưới dạng JSON hoặc XML) sau khi đã được mã hóa.

**Ví dụ cấu trúc file (logic):** `{ "salt": "...", "nonce": "...", "ciphertext": "..." }`

## 4. Luồng hoạt động của ứng dụng

1.  **Lần đầu sử dụng:**
    *   Ứng dụng yêu cầu người dùng nhập Mật khẩu chủ mới.
    *   Tạo một `salt` ngẫu nhiên.
    *   Dùng PBKDF2 để tạo `Khóa mã hóa` từ Mật khẩu chủ và `salt`.
    *   Lưu lại `salt` và một hash của `Khóa mã hóa` để kiểm tra mật khẩu đúng ở lần sau.
2.  **Mở khóa Két sắt:**
    *   Người dùng nhập Mật khẩu chủ.
    *   Ứng dụng đọc `salt` từ file.
    *   Tái tạo lại `Khóa mã hóa` bằng PBKDF2 với mật khẩu vừa nhập và `salt`.
    *   Dùng `Khóa mã hóa` này để giải mã `ciphertext` trong file.
    *   Nếu giải mã thành công (nhờ tính năng xác thực của GCM), dữ liệu sẽ được hiển thị. Nếu không, báo lỗi sai mật khẩu.
3.  **Lưu dữ liệu (Thêm/Sửa mật khẩu):**
    *   Người dùng thêm một mục mới.
    *   Toàn bộ dữ liệu (bao gồm cả mục mới) được chuyển thành dạng chuỗi (ví dụ JSON).
    *   Tạo một `nonce` mới, ngẫu nhiên.
    *   Dùng `Khóa mã hóa` hiện tại và `nonce` mới để mã hóa lại toàn bộ dữ liệu.
    *   Ghi đè file `vault.dat` với `salt` (không đổi), `nonce` (mới), và `ciphertext` (mới).

## 5. Công nghệ và Thư viện đề xuất

*   **Ngôn ngữ:** **Python 3**
*   **Thư viện Giao diện (GUI):**
    *   **PySide6:** Lựa chọn hiện đại, mạnh mẽ, chuyên nghiệp với giấy phép LGPL linh hoạt.
*   **Thư viện Mã hóa:**
    *   **cryptography:** Thư viện tiêu chuẩn, mạnh mẽ và an toàn nhất cho Python.
        ```bash
        pip install cryptography PySide6
        ```

## 6. Các bước triển khai (Roadmap)

1.  **Bước 1: Thiết lập môi trường**
    *   Cài đặt Python, PySide6, và thư viện `cryptography`.
2.  **Bước 2: Thiết kế Giao diện người dùng (UI)**
    *   Vẽ phác thảo các cửa sổ: màn hình khóa (yêu cầu Mật khẩu chủ), màn hình chính (hiển thị danh sách mật khẩu), cửa sổ thêm/sửa mật khẩu.
3.  **Bước 3: Xây dựng lõi mã hóa (`crypto_logic.py`)**
    *   Viết các hàm:
        *   `derive_key(password, salt)`: Dùng `PBKDF2HMAC` từ thư viện `cryptography`.
        *   `encrypt(data, key)`: Dùng `AESGCM` để mã hóa, trả về `(nonce, ciphertext)`.
        *   `decrypt(nonce, ciphertext, key)`: Giải mã và xác thực. Trả về dữ liệu gốc hoặc `None` nếu thất bại.
4.  **Bước 4: Xây dựng logic quản lý file (`vault_manager.py`)**
    *   Viết các hàm:
        *   `save_vault(file_path, salt, nonce, ciphertext)`
        *   `load_vault(file_path)`: Đọc và trả về `(salt, nonce, ciphertext)`.
5.  **Bước 5: Tích hợp Logic vào Giao diện**
    *   Kết nối các nút bấm (button) với các hàm đã viết. Ví dụ: nút "Mở khóa" sẽ gọi hàm `load_vault`, `derive_key`, và `decrypt`.
6.  **Bước 6: Hoàn thiện và Mở rộng**
    *   Thêm tính năng "Tạo mật khẩu ngẫu nhiên".
    *   Thêm tính năng "Sao chép vào clipboard" (có thể tự động xóa sau 30 giây).
    *   Thêm chức năng tìm kiếm.

## 7. Tính năng mở rộng (Nếu có thời gian)

*   **Tạo mật khẩu ngẫu nhiên:** Thêm một chức năng giúp người dùng tạo mật khẩu mạnh (bao gồm chữ hoa, chữ thường, số, ký tự đặc biệt).
*   **Tự động khóa:** Tự động khóa két sắt sau một khoảng thời gian không hoạt động.
*   **Chỉ báo độ mạnh mật khẩu:** Đánh giá độ mạnh của Mật khẩu chủ khi người dùng tạo.
