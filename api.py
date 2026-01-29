import google.generativeai as genai

genai.configure(api_key="AIzaSyBbkOL15IxhETgmK3y6ttVJy8lDWThK0vA")

print("รายชื่อโมเดลที่ใช้ได้:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")