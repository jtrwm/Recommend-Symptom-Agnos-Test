# Agnos Health - Symptom Recommender System 

โปรเจกต์นี้เป็นส่วนหนึ่งของแบบทดสอบคัดเลือกตำแหน่ง Data science สำหรับ Agnos Health 

## Key Features
1. Smart Symptom Extraction ใช้ข้อมูล search_term และ summary
   - มีระบบ Tokenization จัดการแยกอาการที่พิมพ์ติดกัน เช่น น้ำมูกไหล, ไอมีเสมหะ, ให้เป็นอาการเดี่ยว ๆ อย่างน้ำมูกไหล และไอมีเสมหะ
2. Age Group Categorization
   - ระบบมีการจัดกลุ่มอายุผู้ป่วยออกเป็น 4 ช่วงวัยหลัก เพื่อให้สอดคล้องกับพฤติกรรมและโรคที่มักเกิดตามวัย ได้แก่ 
        - 0-6 ปี (วัยเด็ก)
        - 7-18 ปี (วัยเรียน/วัยรุ่น) 
        - 19-60 ปี (วัยผู้ใหญ่/วัยทำงาน)
        - 60+ ปี (ผู้สูงอายุ)
3. recommend the next possible symptom similar 3 ระดับ เพื่อไม่ให้ผู้ป่วยตื่นตระหนกจนเกินไป ระบบจะแสดงผลความเสี่ยงตามกลุ่มต่าง ๆ ดังนี้
   - โอกาสสูงมาก วิเคราะห์จากผู้ป่วยที่ช่วงอายุและเพศมีความเหมือนกันทั้งหมด
   - โอกาสปานกลาง วิเคราะห์ไปยังช่วงอายุข้างเคียง
   - โอกาสน้อย วิเคราะห์เปรียบเทียบจากฐานข้อมูลทั้งหมด
4. Strict Gender Isolation
   - ป้องกันความผิดพลาดทางการแพทย์ (Medical Error) โดยยึดหลักไม่นำข้อมูลอาการของเพศตรงข้ามมาคำนวณร่วมด้วยในโอกาสสูงมาก และโอกาสปานกลาง
5. Interactive UI / UX:
   - ใช้ไลบรารี Select2 แปลงช่องกรอกข้อความธรรมดา ให้เป็น Searchable Dropdown
   - รองรับการพิมพ์ค้นหาทั้งภาษาไทยและภาษาอังกฤษแบบเว้นวรรค เช่น Animal bite

## Tech Stack
- Backend: Python (FastAPI) - เลือกใช้ FastAPI เพราะประมวลผลเร็ว รองรับ Pydantic ข้อมูลมีโครงสร้างชัดเจน
- Data Engine: Pandas, JSON, difflib - สำหรับจัดการและทำความสะอาด Data Pipeline
- Frontend: HTML, CSS, JavaScript 

## วิธีการติดตั้งและรันระบบ
1. เตรียม Environment และติดตั้งไลบรารี เปิด Terminal และติดตั้งไลบรารีที่จำเป็นทั้งหมดผ่านไฟล์ requirements.txt:
   ```bash
   pip install -r requirements.txt
2. รันคำสั่ง python app.py
3. เปิดเว็บเบราว์เซอร์และเข้าไปที่ http://127.0.0.1:8000/

## API Interface 
ระบบหลังบ้านถูกพัฒนาขึ้นด้วย FastAPI ซึ่งมาพร้อมกับระบบสร้างเอกสาร API อัตโนมัติ เมื่อรันเซิร์ฟเวอร์แล้วสามารถเข้าไปดูโครงสร้างเอกสารและทดสอบยิงระบบ ได้ทันทีที่ http://127.0.0.1:8000/docs

### Endpoint หลักสำหรับการประเมินอาการ
* URL: `/recommend`
* Method: `POST`
* Content-Type: `application/json`

ตัวอย่างข้อมูลที่ต้องส่งเข้ามา
{
  "gender": "Male",
  "age": 25,
  "symptoms": ["Blurry vision", "Dizzy"]
}

ตัวอย่างข้อมูลที่ระบบส่งกลับ
{
  "error": false,
  "detected_symptoms": ["Blurry vision", "Dizzy"],
  "tier_1": ["Headache", "Nausea"],
  "tier_2": ["Fatigue"],
  "tier_3": [],
  "message": "วิเคราะห์สำเร็จ"
}