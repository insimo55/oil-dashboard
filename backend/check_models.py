# check_models.py
import google.generativeai as genai

# Вставь свой ключ прямо сюда для быстрой проверки
GOOGLE_API_KEY = "AIzaSyDG-7wgFvAl5I3QMJkiOTEi4aCRsXn1_m4"
genai.configure(api_key=GOOGLE_API_KEY)

print("Доступные модели, поддерживающие 'generateContent':")
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(f"- {m.name}")