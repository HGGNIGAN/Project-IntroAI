# Hướng dẫn Workflow

## 1. Quy Tắc Commit

### 1.1 Thông Điệp Commit

- Viết commit message rõ ràng, ngắn gọn và mô tả chính xác thay đổi
- Dòng đầu tiên không quá 50 ký tự
- Nếu cần thêm chi tiết, cách dòng thứ hai và viết lý do thay đổi
- Sử dụng tiếng Anh, nhất quán trong cả dự án

Ví dụ tốt:

```
Fix login validation bug in user authentication

- Update password validation logic
- Add comprehensive error messages
- Improve performance by 15%
```

### 1.2 Kích Thước Commit

- Mỗi commit nên là một đơn vị logic hoàn chỉnh
- Tránh commit quá lớn (nhiều tính năng khác nhau)
- Tránh commit quá nhỏ (thay đổi không ý nghĩa)

## 2. Quy Tắc Nhánh (Branch)

### 2.1 Đặt Tên Nhánh

- Sử dụng tên nhánh mô tả rõ ràng
- Định dạng: `feature/tên-tính-năng` hoặc `bugfix/tên-lỗi`
- Sử dụng chữ thường và gạch ngang

Ví dụ:

- `feature/user-authentication`
- `bugfix/login-validation`
- `docs/update-readme`

### 2.2 Tạo Nhánh

- Luôn tạo nhánh mới từ `main` hoặc `develop` (tùy theo quy trình)
- Cập nhật nhánh với commit mới nhất trước khi tạo pull request

## 3. Quy Tắc Code

### 3.1 Tiêu Chuẩn Code

- Mặc định indentation size sẽ là 8 spaces, mọi người nên điều chỉnh để có codebase đồng nhất ở khoản này
- Tuân thủ PEP 8 (đối với Python)
- Sử dụng consistent naming conventions
- Viết code sạch, dễ đọc và dễ bảo trì
- Tránh code trùng lặp (DRY - Don't Repeat Yourself)

### 3.2 Documentation

- Thêm docstrings cho các hàm và lớp
- Cập nhật README nếu có thay đổi công năng
- Viết comments cho logic phức tạp

### 3.3 Kiểu Code

- Sử dụng linting tool (flake8, pylint cho Python)
- Định dạng code tự động (black, autopep8)
- Đảm bảo code pass kiểm tra linting

## 4. Quy Tắc Testing

### 4.1 Trước Khi Push

- Chạy toàn bộ test suite local
- Đảm bảo code không có lỗi biên dịch/syntax
- Kiểm tra manual các tính năng mới
- Không push nếu tests fail

### 4.2 Viết Test

- Thêm unit tests cho tính năng mới
- Cập nhật tests khi thay đổi logic hiện tại
- Đạt ít nhất 70% code coverage

## 5. Quy Tắc Pull Request (PR)

### 5.1 Mô Tả PR

- Viết tiêu đề rõ ràng, mô tả nội dung PR
- Chi tiết các thay đổi chính trong mô tả
- Liên kết đến issue/task liên quan nếu có
- Liệt kê các thay đổi lớn

Mẫu PR:

```
## Mô Tả
[Mô tả ngắn về thay đổi]

## Loại Thay Đổi
- [ ] Bug fix
- [ ] Tính năng mới
- [ ] Breaking change
- [ ] Documentation update

## Kiểm Tra
- [ ] Code pass linting
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No conflicts with main
```

### 5.2 Code Review

- Chờ ít nhất 1 approval trước merge
- Phản hồi review comments một cách xây dựng
- Yêu cầu review từ team members có kinh nghiệm

## 6. Quy Tắc Trước Push

- Luôn pull latest từ main/develop trước push
- Rebase hoặc merge conflicts nếu cần
- Không push code chưa được review/approve
- Kiểm tra lần cuối trước khi push

## 7. Quy Tắc Sau Merge

- Xóa nhánh feature sau merge vào main
- Monitor CI/CD pipeline
- Thông báo team về thay đổi lớn
- Cập nhật documentation nếu cần

## 8. Quy Tắc Bảo Mật

- Không commit secrets (API keys, passwords)
- Sử dụng .gitignore để bỏ qua các tập tin nhạy cảm
- Review code cẩn thận trước commit
- Không commit thông tin cá nhân

## 9. Quy Tắc Đặt Tên Tập Tin

- Sử dụng tên tập tin mô tả rõ ràng
- Sử dụng snake_case cho Python (my_file.py)
- Sử dụng camelCase hoặc kebab-case cho tập tin config
- Tránh spaces trong tên tập tin

## 10. Quy Tắc Thay Đổi Database

- Viết migration script nếu thay đổi schema
- Backup dữ liệu trước thay đổi
- Test migration trên development trước
- Không xóa dữ liệu quan trọng

## 11. Tương Tác Với Remote Repository

### 11.1 Fetch và Pull

- Fetch thường xuyên để cập nhật dữ liệu remote
- Pull trước khi bắt đầu công việc mới
- Giải quyết conflicts khi có

### 11.2 Push

- Push nhánh feature của bạn trước khi tạo PR
- Không force push nếu không cần thiết
- Không push trực tiếp từ nhánh `main`
- Nếu force push, thông báo team

## 12. Quy Tắc Log và Debugging

- Không commit console.log, print statements không cần thiết
- Sử dụng logging framework thích hợp
- Xóa debug code trước commit

## Tóm Tắt Quy Trình Chuẩn

1. Tạo nhánh: `git checkout -b feature/tên-tính-năng`
2. Thực hiện thay đổi và test
3. Commit với message rõ ràng
4. Push nhánh lên repository
5. Tạo Pull Request
6. Chờ review và merge
7. Xóa nhánh cục bộ và remote

---

Tuân thủ những quy tắc này sẽ giúp duy trì chất lượng code cao và tạo môi trường làm việc tốt cho toàn bộ team.
