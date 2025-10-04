# PyVault - Trình Quản Lý Mật Khẩu Cá Nhân An Toàn

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Qt](https://img.shields.io/badge/Qt-PySide6-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

Một ứng dụng desktop đơn giản, an toàn và đa nền tảng để quản lý mật khẩu cá nhân, được xây dựng bằng Python và PySide6.

## Giới thiệu

Trong thời đại số, việc quản lý hàng chục mật khẩu là một thách thức. **PyVault** giải quyết vấn đề này bằng cách cho phép bạn lưu trữ tất cả thông tin đăng nhập vào một "két sắt" kỹ thuật số duy nhất, được mã hóa và bảo vệ bởi một Mật khẩu chủ.

Dữ liệu của bạn không bao giờ rời khỏi máy tính và không được lưu trữ trên bất kỳ máy chủ đám mây nào.

## Tính năng chính

- **Bảo mật hàng đầu:** Toàn bộ dữ liệu được mã hóa bằng thuật toán AES-256-GCM.
- **Bảo vệ Mật khẩu chủ:** Sử dụng PBKDF2 với salt và hàng trăm ngàn vòng lặp để chống lại tấn công từ điển.
- **Quản lý Toàn diện:** Thêm, sửa, xóa và tìm kiếm thông tin đăng nhập.
- **An toàn:** Sao chép mật khẩu vào clipboard và tự động xóa sau một khoảng thời gian ngắn.
- **Đa nền tảng:** Hoạt động trên Windows, macOS và Linux.

## Kiến trúc bảo mật

- **Không lưu Mật khẩu chủ:** Mật khẩu chủ của bạn chỉ được dùng để tạo ra khóa mã hóa trong bộ nhớ và không bao giờ được lưu trữ.
- **Mã hóa xác thực (Authenticated Encryption):** Chế độ AES-GCM đảm bảo dữ liệu vừa được giữ bí mật, vừa không thể bị thay đổi mà không bị phát hiện.
- **Lưu trữ cục bộ:** Toàn bộ két sắt được lưu trong một file duy nhất (`vault.dat`) trên máy của bạn.

## Công nghệ sử dụng

- **Ngôn ngữ:** Python 3
- **Giao diện người dùng (GUI):** PySide6
- **Thư viện mã hóa:** `cryptography`

## Tải xuống và Sử dụng

### Phiên bản đã đóng gói

**📦 Hiện tại có sẵn:**
- **Linux (x64)**: [Tải xuống v1.0.0](https://github.com/mttk2004/pyvault/releases/download/v1.0.0/pyvault-v1.0.0-linux-x64.tar.gz)

**🚧 Đang phát triển:**
- **Windows (x64)**: Sẽ có trong phiên bản tương lai
- **macOS (Intel/ARM)**: Sẽ có trong phiên bản tương lai

> **Lưu ý**: Hiện tại chỉ có bản Linux. Để cài đặt, tải file tar.gz và giải nén, sau đó chạy file `pyvault` trong thư mục.

### Chạy từ mã nguồn (Cho nhà phát triển)

1.  **Clone repository:**
    ```bash
    git clone https://github.com/mttk2004/pyvault.git
    cd pyvault
    ```

2.  **Tạo môi trường ảo và cài đặt thư viện:**
    ```bash
    # Tạo môi trường ảo
    python -m venv venv

    # Kích hoạt môi trường ảo
    # Trên Windows:
    # venv\Scripts\activate
    # Trên macOS/Linux:
    source venv/bin/activate

    # Cài đặt các thư viện cần thiết
    pip install -r requirements.txt
    ```

3.  **Chạy ứng dụng:**
    ```bash
    python main.py
    ```

### Xây dựng từ mã nguồn

```bash
# Cài đặt PyInstaller
pip install pyinstaller

# Xây dựng ứng dụng
python -m PyInstaller --clean pyvault.spec

# Ứng dụng sẽ được tạo trong thư mục dist/
```

## Cài đặt và Gỡ bỏ

### Cài đặt hệ thống
```bash
# Giải nén và chạy script cài đặt
tar -xzf pyvault-v1.0.0-linux-x64.tar.gz
cd pyvault/
./install.sh
```

### Sử dụng sau khi cài đặt
```bash
# Chạy từ bất kỳ đâu
pyvault

# Hoặc tìm "PyVault" trong Application Menu
```

### Gỡ cài đặt
```bash
# Gỗ cài đặt tương tác (an toàn)
./uninstall.sh

# Gỡ cài đặt tự động (giữ lại dữ liệu vault)
./uninstall.sh --force

# Xem trợ giúp
./uninstall.sh --help
```

**Lưu ý:** Dữ liệu vault được lưu tại `~/.config/pyvault/vault.dat` và sẽ được bảo vệ trừ khi bạn chọn xóa.

## Giấy phép

Dự án này được cấp phép theo Giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.
