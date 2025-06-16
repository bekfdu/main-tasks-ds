# Telekom Mijozlar Ketishi Tahlili va Telegram Bot Hisoboti

## Umumiy Ko‘rinish
Ushbu hisobot telekom kompaniyasining mijozlar ketishini bashorat qilish loyihasini taqdim etadi. Tasodifiy O‘rmon modeli o‘qitildi va Telegram bot orqali mijoz ma‘lumotlarini kiritib, ketish ehtimolligini bashorat qilish imkoni yaratildi.

## Telegram Bot Haqida
- **Funksionallik**:  
  - `/predict` orqali 18 ta xususiyat (tenure, MonthlyCharges, Contract, va h.k.) so‘raladi.  
  - Tasodifiy O‘rmon modeli (`model.joblib`) va StandardScaler (`scaler.joblib`) yordamida bashorat qilinadi.  
  - `/start`, `/help`, `/cancel` buyruqlari qulaylik yaratadi.

- **Interfeys**:  
  - Oldingi MarkdownV2 formatidagi xatolar tufayli HTML formatiga o‘tildi, bu maxsus belgilarni ekranlashtirish muammolarini bartaraf qildi.  
  - `StreamingMovies` bosqichidagi xatolik tuzatildi, qo‘shimcha logging qo‘shildi.  
  - Barcha xabarlar foydalanuvchiga qulay va aniq.

- **Texnik Detallar**:  
  - Python’da `python-telegram-bot` (v20.0+) ishlatildi.  
  - Bashorat jarayoni mustahkamlandi, model ustunlari mosligi ta’minlandi.  
  - Xavfsiz: xato boshqaruv, kengaytirilgan logging va validatsiya.

## `model.joblib` va `scaler.joblib` Fayllari
- **Yaratish**:  
  - `create_model_and_scaler.py` skripti `Data.csv` asosida model va scaler’ni hosil qiladi.  
  - Fayllar `D:\Data Science\Project` papkasida saqlanadi.

- **Ishlatish**:  
  - Fayllar `telegram_bot.py` bilan bir papkada bo‘lishi kerak.  
  - Bot ularni avtomatik yuklaydi.

## Asosiy Natijalar
- **Model**: Tasodifiy O‘rmon (Accuracy: ~0.82, F1: ~0.60, ROC-AUC: ~0.86).  
- **Muhim Xususiyatlar**: tenure, MonthlyCharges, Contract_Month-to-month, InternetService_Fiber optic.

## Tavsiyalar
- Yangi mijozlarga chegirmalar taklif qilish.  
- Optik tolali xizmat sifatini yaxshilash.  
- Oy-ma-oy shartnomalarni uzoq muddatlilarga aylantirish.

## Topshiriladigan Fayllar
- `telegram_bot.py`: Telegram bot kodi (HTML formatiga o‘tildi, StreamingMovies xatosi tuzatildi).  
- `create_model_and_scaler.py`: Model va scaler yaratish kodi.  
- `report.md`: Ushbu hisobot.  
- Bot skrinshotlari GitHub reposida.

## Foydalanish Ko‘rsatmalari
1. `pip install python-telegram-bot pandas scikit-learn joblib` orqali kutubxonalarni o‘rnating.  
2. `YOUR_BOT_TOKEN` ni haqiqiy token bilan almashtiring.  
3. `model.joblib` va `scaler.joblib` fayllarini `D:\Data Science\Project` papkasida ta’minlang (agar yo‘q bo‘lsa, `create_model_and_scaler.py` ni ishlatib yarating).  
4. `python telegram_bot.py` orqali botni ishga tushiring.  
5. Telegram’da `/predict` buyrug‘ini sinab ko‘ring, `StreamingMovies` bosqichidan o‘tib, bashoratni oling.

## Xatolarni Bartaraf Qilish
- Agar bot ishlamasa, terminaldagi xato logini tekshiring va taqdim qiling.  
- `Data.csv`, `model.joblib`, va `scaler.joblib` fayllari mavjudligini tekshiring.  
- Bot tokeni va kutubxonalar versiyalarini qayta ko‘rib chiqing
