# 🏛️ Court AI ThaiLLM — คู่มือติดตั้ง

ระบบ AI ตอบคำถามกฎหมายปกครองและคดีปกครอง พัฒนาด้วย Python + Streamlit เชื่อมต่อ ThaiLLM API และ AWS Bedrock

---

## 📋 ความต้องการของระบบ

| รายการ | เวอร์ชัน |
|--------|---------|
| Docker | 20.10+ |
| Docker Compose | v2+ |
| พื้นที่ดิสก์ | อย่างน้อย 500MB (รวม data ไฟล์กฎหมาย) |

---

## 🔑 ไฟล์ที่ต้องเตรียมก่อน (ไม่อยู่ใน Git)

### 1. `.streamlit/secrets.toml`

```toml
# AWS Bedrock
AWS_ACCESS_KEY  = "your-aws-access-key"
AWS_SECRET_KEY  = "your-aws-secret-key"
KB_ID           = "your-knowledge-base-id"
REGION          = "us-east-1"

# ThaiLLM API
THAILLM_API_KEY = "your-thaillm-api-key"
```

### 2. `data/` folder

โฟลเดอร์ข้อมูลที่ต้องได้รับจากทีมพัฒนา ประกอบด้วย:
- `court_ai.db` — ฐานข้อมูล SQLite หลัก (บทสนทนา + ประวัติ)
- ไฟล์กฎหมาย (.txt, .docx, .doc) — ข้อมูลกฎหมายปกครอง
- ไฟล์ intent (.xlsx) — ข้อมูล intent classification

> ⚠️ ไฟล์เหล่านี้ไม่อยู่ใน Git เนื่องจากขนาดใหญ่และมีข้อมูลภายใน ติดต่อทีมพัฒนาเพื่อขอไฟล์

---

## 🚀 ขั้นตอนติดตั้ง (Docker)

### 1. Clone โปรเจกต์
```bash
git clone https://github.com/diaryman/chatbot-thaillm.git
cd chatbot-thaillm
```

### 2. สร้าง secrets
```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
# ใส่ค่าตามรูปแบบด้านบน
```

### 3. วาง data folder
```bash
# รับไฟล์ data จากทีมพัฒนา แล้วแตกไว้ที่นี่
mkdir -p data
# cp -r /path/to/data/* ./data/
```

### 4. รัน Docker
```bash
docker compose up -d --build
```

### 5. เข้าใช้งาน
เปิด browser ที่ **http://localhost:8502**

---

## 🗂️ โครงสร้างโปรเจกต์

```
chatbot-thaillm/
├── main.py                    # โค้ดหลัก
├── src/
│   ├── admin.py               # หน้า admin dashboard
│   ├── config.py              # ค่า config ทั้งหมด
│   ├── database.py            # จัดการ SQLite
│   ├── export.py              # export รายงาน
│   ├── services.py            # logic เชื่อมต่อ API
│   ├── ui.py                  # UI components
│   └── utils.py               # utility functions
├── .streamlit/
│   └── secrets.toml           # 🔑 ต้องสร้างเอง
├── data/                      # 🔑 ต้องรับจากทีม (ไม่อยู่ใน Git)
│   ├── court_ai.db            # SQLite database
│   └── *.txt, *.docx          # ไฟล์กฎหมาย
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🔧 คำสั่งที่ใช้บ่อย

```bash
# ดู logs
docker compose logs -f

# หยุดระบบ
docker compose down

# อัปเดตโค้ด
git pull && docker compose up -d --build

# Backup database
cp data/court_ai.db data/court_ai.db.backup
```

---

## 🐛 แก้ปัญหาที่พบบ่อย

| ปัญหา | วิธีแก้ |
|-------|--------|
| Port 8502 ถูกใช้อยู่ | แก้ใน docker-compose.yml: `"8510:8501"` |
| Database ไม่เจอ | ตรวจสอบว่า `data/court_ai.db` มีอยู่ |
| ThaiLLM API error | ตรวจสอบ THAILLM_API_KEY ใน secrets.toml |
