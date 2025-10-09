# Hướng Dẫn Phát Triển PyVault cho Jules

Chào Jules, đây là tài liệu hướng dẫn để bạn có thể hiểu và phát triển dự án PyVault.

## 1. Tổng Quan Dự Án

- **Tên dự án:** PyVault
- **Mục tiêu:** Một trình quản lý mật khẩu cá nhân an toàn, mã hóa dữ liệu và lưu trữ cục bộ trên máy tính người dùng.
- **Công nghệ chính:**
  - **Ngôn ngữ:** Python 3.10+
  - **Giao diện người dùng (GUI):** PySide6
  - **Mã hóa:** Thư viện `cryptography` (AES-256-GCM, PBKDF2)
  - **Đóng gói:** PyInstaller

## 2. Thiết Lập Môi Trường Phát Triển

Dự án này sử dụng Python. Bạn không cần PHP, Composer hay Node.js.

1.  **Yêu cầu:**
    - Python 3.10 hoặc mới hơn.
    - `pip` và `venv`.

2.  **Các bước cài đặt:**
    ```bash
    # 1. Clone repository (nếu bạn chưa có)
    # git clone https://github.com/mttk2004/pyvault.git
    # cd pyvault

    # 2. Tạo môi trường ảo
    python -m venv venv

    # 3. Kích hoạt môi trường ảo
    # Trên Windows:
    # venv\Scripts\activate
    # Trên macOS/Linux:
    # source venv/bin/activate

    # 4. Cài đặt các thư viện cần thiết
    pip install -r requirements.txt
    ```

## 3. Chạy Ứng Dụng

Sau khi đã cài đặt môi trường, bạn có thể chạy ứng dụng bằng lệnh:

```bash
python main.py
```

## 4. Cấu Trúc Dự Án

- `main.py`: Điểm khởi đầu của ứng dụng.
- `requirements.txt`: Danh sách các thư viện Python cần thiết.
- `pyvault.spec`: File cấu hình cho PyInstaller để đóng gói ứng dụng.
- `src/`: Thư mục chứa mã nguồn chính.
  - `crypto_logic.py`: Xử lý toàn bộ logic mã hóa và giải mã.
  - `vault_manager.py`: Quản lý việc đọc/ghi file vault đã mã hóa.
  - `category_manager.py`: Quản lý danh mục cho các mục nhập.
  - `ui/`: Chứa các file liên quan đến giao diện người dùng (cửa sổ, dialogs, widgets).
  - `utils/`: Chứa các tiện ích, ví dụ như tạo mật khẩu.
  - `assets/`: Chứa các tài nguyên tĩnh như icon.
- `tests/`: Chứa các unit test cho dự án.

---

## 5. Gợi Ý (Prompts) Cho Các Nhiệm Vụ Phát Triển Tiếp Theo

Dưới đây là những gợi ý chi tiết bạn có thể sử dụng để yêu cầu tôi (hoặc một AI khác) thực hiện các nhiệm vụ tiếp theo.

### Gợi Ý 1: Đóng Gói Ứng Dụng cho Windows

**Bối cảnh:** Dự án đã có thể đóng gói cho Linux bằng PyInstaller (`pyvault.spec`) và có script cài đặt (`install.sh`). Tuy nhiên, chưa có phiên bản cho Windows.

**Yêu cầu:**

> **Prompt:** "Hãy phân tích dự án PyVault và thực hiện các bước cần thiết để đóng gói ứng dụng thành một file thực thi (`.exe`) duy nhất cho Windows 64-bit.
>
> 1.  **Phân tích và điều chỉnh `pyvault.spec`:**
>     - Đảm bảo file spec tương thích với Windows (ví dụ: sử dụng `console=False`, xử lý đường dẫn đúng cách).
>     - Cấu hình để ứng dụng được đóng gói thành một file duy nhất (`--onefile`).
>     - Chuyển đổi icon `src/assets/icon.svg` thành định dạng `.ico` và nhúng vào file `.exe`.
>
> 2.  **Tạo script xây dựng cho Windows:**
>     - Tạo một file batch script `build_windows.bat` để tự động hóa quá trình kích hoạt môi trường ảo (nếu có) và chạy PyInstaller với file spec đã được cấu hình.
>
> 3.  **Kiểm tra và hoàn thiện:**
>     - Đảm bảo file `.exe` được tạo ra trong thư mục `dist` có thể chạy độc lập trên một máy Windows khác mà không cần cài đặt Python hay bất kỳ thư viện nào.
>     - Cập nhật file `README.md` để thêm liên kết tải xuống cho phiên bản Windows sau khi nó được phát hành."

### Gợi Ý 2: Hiện Đại Hóa Giao Diện Người Dùng (UI/UX)

**Bối cảnh:** Giao diện hiện tại của PyVault hoạt động tốt nhưng trông còn khá đơn giản và "nghiệp dư". Cần cải thiện để mang lại trải nghiệm người dùng chuyên nghiệp và hiện đại hơn.

**Yêu cầu:**

> **Prompt:** "Hãy cải thiện toàn diện UI/UX cho ứng dụng PyVault để nó trông hiện đại, chuyên nghiệp và thân thiện hơn. Tập trung vào các khía cạnh sau:
>
> 1.  **Cải thiện Cửa sổ Đăng nhập (`login_window_enhanced.py`):**
>     - Thiết kế lại layout cho cân đối và hấp dẫn hơn.
>     - Thêm hiệu ứng (animation) tinh tế khi người dùng tương tác (ví dụ: khi focus vào ô nhập liệu, khi nhấn nút).
>     - Cải thiện thông báo lỗi/thành công, làm cho chúng trực quan hơn thay vì chỉ là text đơn thuần.
>
> 2.  **Nâng cấp Cửa sổ Chính (`main_window.py`):**
>     - **Bảng hiển thị mật khẩu:** Thay thế `QTableWidget` bằng `QTableView` với `QAbstractTableModel` để tối ưu hiệu suất và khả năng tùy biến.
>     - **Thanh công cụ (Toolbar):** Thiết kế lại thanh công cụ với các icon mới, rõ ràng và đồng bộ hơn (sử dụng icon từ một bộ icon hiện đại như Feather Icons hoặc Fluent UI System Icons).
>     - **Tích hợp quản lý danh mục:** Thay vì chỉ hiển thị danh mục trong dialog, hãy tích hợp một panel bên trái cửa sổ chính để người dùng có thể lọc các mục nhập theo danh mục một cách trực quan (giống như các ứng dụng email client).
>     - **Thêm "Empty State":** Khi không có mục nhập nào, hiển thị một thông điệp thân thiện hướng dẫn người dùng cách thêm mục nhập đầu tiên, thay vì chỉ một bảng trống.
>
> 3.  **Cải thiện các Dialog (`entry_dialog.py`, `category_dialog.py`):**
>     - Thiết kế lại các form nhập liệu cho gọn gàng, các nhãn (label) và ô nhập (input) được căn chỉnh hợp lý.
>     - Thêm chức năng ẩn/hiện mật khẩu trong `entry_dialog.py` để người dùng có thể kiểm tra lại mật khẩu đã nhập.
>
> 4.  **Đồng bộ và Tinh chỉnh:**
>     - Rà soát toàn bộ ứng dụng để đảm bảo sự đồng nhất về font chữ, màu sắc, khoảng cách và kích thước các thành phần theo `design_system.py`.
>     - Áp dụng các hiệu ứng đổ bóng (shadow) và bo góc (border-radius) một cách hợp lý để tạo cảm giác mềm mại và hiện đại."
