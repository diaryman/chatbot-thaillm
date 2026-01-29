def save_to_sheet(username, q, r_left, r_right):
    print("🔄 กำลังพยายามบันทึกข้อมูลลง Sheet...") # Debug print 1
    try:
        sheet = get_sheet_client()
        if sheet is None:
            print("❌ Error: เชื่อมต่อ Google Sheet ไม่ได้ (เช็คชื่อไฟล์/credentials)")
            return

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            username, 
            q,
            r_left['model'], 
            r_left['answer'], 
            f"{r_left['cost']:.4f}",
            r_right['model'], 
            r_right['answer'], 
            f"{r_right['cost']:.4f}"
        ]
        sheet.append_row(row)
        print("✅ บันทึกข้อมูลสำเร็จ!") # Debug print 2
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึก: {e}") # มันจะฟ้อง Error ตรงนี้
        # st.error(f"Save Error: {e}") # ถ้าอยากให้ขึ้นบนหน้าเว็บ ให้เอา comment ออก