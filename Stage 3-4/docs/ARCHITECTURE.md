# System Architecture — Library Management System (Group 02)

## Kiến trúc áp dụng: **Layered Architecture** (Chapter 3)

Hệ thống được tổ chức thành 3 tầng chính (Presentation / Business /
Persistence), mỗi tầng chỉ được gọi xuống tầng ngay bên dưới nó (không
nhảy tầng), theo đúng mô hình Layered model đã học:

```
┌───────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                             │
│  - app/main.py       : console app (menu nhập từ bàn phím)      │
│  - app/gui_main.py   : entry point cho GUI                      │
│  - app/gui/*.py      : Tkinter GUI                              │
│      login_view.py   : màn hình đăng nhập                       │
│      member_view.py  : màn hình chức năng member                │
│      admin_view.py   : màn hình chức năng admin                 │
│      dialogs.py, app.py : cửa sổ con, khung ứng dụng chính      │
│                                                                   │
│  -> Chỉ gọi method trên object Member/Administrator, KHÔNG       │
│     chứa business rule nào (không tính tiền phạt, không so       │
│     sánh ngày quá hạn ở tầng này).                               │
├───────────────────────────────────────────────────────────────┤
│  BUSINESS LAYER  (app/models.py)                                 │
│                                                                   │
│      User  (base class: username, password, login())            │
│        │                                                          │
│        ├── Member (extends User)                                 │
│        │     - view_personal_info(), search_books()              │
│        │     - view_borrowed_books(), view_borrow_history()      │
│        │     - view_fines()                                      │
│        │                                                          │
│        └── Administrator (extends User)                          │
│              - add/update/delete/view Member                     │
│              - add/update/delete/view Book                       │
│              - record_borrow(), record_return()                  │
│              - view_overdue_records(), pay_fine()                │
│                                                                   │
│      Book            BorrowRecord            Fine                │
│      - check_availability()   - check_overdue()   - calculate_amount()│
│      - update_quantity()      - record_return()   - pay()        │
│                                                                   │
│  -> Toàn bộ nghiệp vụ (login, tìm sách, mượn/trả, tính quá hạn,   │
│     tính & lưu tiền phạt) nằm hết ở tầng này. Không biết dữ liệu  │
│     đang hiển thị ở console hay GUI.                             │
├───────────────────────────────────────────────────────────────┤
│  PERSISTENCE LAYER  (app/db.py)                                  │
│  - load_data() / save_data() : đọc/ghi data/sample_data.json     │
│  -> Business Layer gọi xuống đây để lấy/lưu dữ liệu; không biết   │
│     nghiệp vụ gì đang xảy ra ở trên.                              │
└───────────────────────────────────────────────────────────────┘
```

## Vì sao chọn Layered model
- **Tách biệt rõ trách nhiệm**: Presentation (console + GUI) không biết gì
  về cách dữ liệu được lưu; Business layer không quan tâm dữ liệu hiển thị
  ra console hay Tkinter; Persistence layer không quan tâm nghiệp vụ gì
  đang chạy ở trên nó.
- **Hai giao diện dùng chung một Business layer**: `app/main.py` (console)
  và `app/gui/*.py` (Tkinter) đều gọi thẳng các method trên cùng object
  `Member`/`Administrator` từ `models.py` — không có business logic nào bị
  viết lặp lại giữa 2 giao diện.
- **Dễ thay thế từng tầng độc lập**: có thể đổi `db.py` sang SQL Server/
  SQLite mà không phải sửa `models.py` hay bất kỳ file GUI/console nào,
  vì tầng trên chỉ làm việc với đối tượng `Member`/`Book`/`BorrowRecord`/
  `Fine`, không biết dữ liệu đến từ JSON hay database thật.

## Ánh xạ sang Class Diagram
- `User` là lớp cha (base class), `Member` và `Administrator` kế thừa từ
  `User` — đúng quan hệ **inheritance** trong sơ đồ lớp Stage 1/2.
- `Book`, `BorrowRecord`, `Fine` là các lớp độc lập, mỗi lớp có thuộc tính
  + hành vi riêng của chính nó, ví dụ:
  - `Book.check_availability()` / `update_quantity()`
  - `BorrowRecord.check_overdue()` / `record_return()`
  - `Fine.calculate_amount()` / `pay()`
- Quan hệ 1 `BorrowRecord` — 0..1 `Fine` được giữ đúng như class diagram:
  chỉ tạo `Fine` khi trả sách trễ, và không tạo trùng nếu đã có `Fine`
  cho bản ghi mượn đó (`Fine.find_for_record`).

## Ghi chú cho bản vẽ draw.io
Vẽ 3 khối xếp chồng (Presentation → Business → Persistence) như sơ đồ ở
trên, riêng khối Business vẽ thêm quan hệ kế thừa `User → Member,
Administrator` bằng mũi tên rỗng (empty arrowhead, ký hiệu inheritance
trong UML). Ghi tên file/class trong mỗi khối — sau đó chụp ảnh dán vào
mục "draw.io" trong file `Task Assignment & Tool Usage Evidence.docx`.
