import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
import logging
import re

# Logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Holatlar (ConversationHandler uchun)
(
    TENURE,
    MONTHLY_CHARGES,
    CONTRACT,
    INTERNET_SERVICE,
    PAYMENT_METHOD,
    GENDER,
    SENIOR_CITIZEN,
    PARTNER,
    DEPENDENTS,
    PHONE_SERVICE,
    MULTIPLE_LINES,
    ONLINE_SECURITY,
    ONLINE_BACKUP,
    DEVICE_PROTECTION,
    TECH_SUPPORT,
    STREAMING_TV,
    STREAMING_MOVIES,
    PAPERLESS_BILLING,
) = range(18)

# Model va scaler ni yuklash
try:
    model = joblib.load("model.joblib")
    scaler = joblib.load("scaler.joblib")
    logger.info("Model va scaler muvaffaqiyatli yuklandi")
except FileNotFoundError:
    logger.error("Model yoki scaler fayli topilmadi! D:\\Data Science\\Project papkasida model.joblib va scaler.joblib fayllari bo‘lishi kerak.")
    raise

# Ma'lumotlarni saqlash uchun vaqtinchalik ombor
user_data = {}

# Boshlang'ich /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>👋 Assalomu alaykum!</b> Men telekom mijozlar ketishini bashorat qiluvchi botman.\n"
        "Mijoz ma'lumotlarini kiritish uchun /predict buyrug‘ini ishlatishingiz mumkin.\n"
        "Yordam uchun /help.",
        parse_mode="HTML"
    )

# Yordam /help buyrug'i
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>ℹ️ Yordam</b>\n\n"
        "Men mijozning ketish ehtimolligini bashorat qilaman. Quyidagi buyruqlardan foydalaning:\n"
        "- /predict: Mijoz ma'lumotlarini kiritish va bashorat olish.\n"
        "- /cancel: Jarayonni bekor qilish.\n\n"
        "Ma'lumot kiritishda har bir qadamda ko‘rsatmalar beriladi. Savollar bo‘lsa, yozing!",
        parse_mode="HTML"
    )

# /predict buyrug'i: jarayonni boshlash
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data[update.effective_user.id] = {}
    await update.message.reply_text(
        "<b>📊 Mijoz ketishini bashorat qilish jarayonini boshlaymiz!</b>\n\n"
        "<b>1️⃣ Tenure</b>: Mijoz kompaniyada necha oy bo‘lgan? (0 dan 72 gacha raqam kiriting)",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    logger.info(f"Predict jarayoni boshlandi (Foydalanuvchi: {update.effective_user.id})")
    return TENURE

# Ma'lumotlarni validatsiya qilish uchun yordamchi funksiyalar
def validate_number(value: str, min_val: float, max_val: float) -> bool:
    try:
        num = float(value)
        return min_val <= num <= max_val
    except ValueError:
        return False

# Tenure kiritish
async def tenure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not validate_number(text, 0, 72):
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, 0 dan 72 gacha bo‘lgan raqam kiriting. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return TENURE

    user_data[user_id]["tenure"] = float(text)
    logger.info(f"Tenure kiritildi: {text} (Foydalanuvchi: {user_id})")
    await update.message.reply_text(
        "<b>2️⃣ Oylik To'lovlar</b>: Mijozning oylik to‘lov summasi necha dollar? (10 dan 150 gacha raqam kiriting)",
        parse_mode="HTML"
    )
    return MONTHLY_CHARGES

# MonthlyCharges kiritish
async def monthly_charges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not validate_number(text, 10, 150):
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, 10 dan 150 gacha bo‘lgan raqam kiriting. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return MONTHLY_CHARGES

    user_data[user_id]["MonthlyCharges"] = float(text)
    logger.info(f"MonthlyCharges kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Oy-ma-oy", "Bir yillik", "Ikki yillik"]]
    await update.message.reply_text(
        "<b>3️⃣ Shartnoma Turi</b>: Mijozning shartnoma turi qaysi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CONTRACT

# Contract kiritish
async def contract(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Oy-ma-oy", "Bir yillik", "Ikki yillik"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Oy-ma-oy, Bir yillik, Ikki yillik. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return CONTRACT

    user_data[user_id]["Contract"] = text
    logger.info(f"Contract kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Optik tolali", "DSL", "Yo'q"]]
    await update.message.reply_text(
        "<b>4️⃣ Internet Xizmati</b>: Mijoz qanday internet xizmatidan foydalanadi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return INTERNET_SERVICE

# InternetService kiritish
async def internet_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Optik tolali", "DSL", "Yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Optik tolali, DSL, Yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return INTERNET_SERVICE

    user_data[user_id]["InternetService"] = text
    logger.info(f"InternetService kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [
        ["Elektron chek", "Pochta cheki"],
        ["Bank o'tkazmasi (avtomatik)", "Kredit karta (avtomatik)"]
    ]
    await update.message.reply_text(
        "<b>5️⃣ To'lov Usuli</b>: Mijoz qanday to‘lov usulidan foydalanadi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return PAYMENT_METHOD

# PaymentMethod kiritish
async def payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = [
        "Elektron chek",
        "Pochta cheki",
        "Bank o'tkazmasi (avtomatik)",
        "Kredit karta (avtomatik)"
    ]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Elektron chek, Pochta cheki, Bank o'tkazmasi (avtomatik), Kredit karta (avtomatik). Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return PAYMENT_METHOD

    user_data[user_id]["PaymentMethod"] = text
    logger.info(f"PaymentMethod kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Erkak", "Ayol"]]
    await update.message.reply_text(
        "<b>6️⃣ Jins</b>: Mijozning jinsi qaysi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return GENDER

# Gender kiritish
async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Erkak", "Ayol"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Erkak, Ayol. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return GENDER

    user_data[user_id]["gender"] = text
    logger.info(f"Gender kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q"]]
    await update.message.reply_text(
        "<b>7️⃣ Katta yoshli</b>: Mijoz katta yoshli (65 va undan yuqori)mi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SENIOR_CITIZEN

# SeniorCitizen kiritish
async def senior_citizen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return SENIOR_CITIZEN

    user_data[user_id]["SeniorCitizen"] = 1 if text == "Ha" else 0
    logger.info(f"SeniorCitizen kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q"]]
    await update.message.reply_text(
        "<b>8️⃣ Turmush o'rtog'i</b>: Mijozning turmush o‘rtog‘i bormi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return PARTNER

# Partner kiritish
async def partner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return PARTNER

    user_data[user_id]["Partner"] = text
    logger.info(f"Partner kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q"]]
    await update.message.reply_text(
        "<b>9️⃣ Qaramog'dagilar</b>: Mijozning qaramog‘ida bolalari yoki boshqa shaxslar bormi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DEPENDENTS

# Dependents kiritish
async def dependents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return DEPENDENTS

    user_data[user_id]["Dependents"] = text
    logger.info(f"Dependents kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q"]]
    await update.message.reply_text(
        "<b>🔟 Telefon Xizmati</b>: Mijoz telefon xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return PHONE_SERVICE

# PhoneService kiritish
async def phone_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return PHONE_SERVICE

    user_data[user_id]["PhoneService"] = text
    logger.info(f"PhoneService kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q", "Telefon xizmati yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣1️⃣ Bir nechta liniya</b>: Mijoz bir nechta telefon liniyasidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MULTIPLE_LINES

# MultipleLines kiritish
async def multiple_lines(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q", "Telefon xizmati yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q, Telefon xizmati yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return MULTIPLE_LINES

    user_data[user_id]["MultipleLines"] = text
    logger.info(f"MultipleLines kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q", "Internet xizmati yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣2️⃣ Onlayn Xavfsizlik</b>: Mijoz onlayn xavfsizlik xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ONLINE_SECURITY

# OnlineSecurity kiritish
async def online_security(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q", "Internet xizmati yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q, Internet xizmati yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return ONLINE_SECURITY

    user_data[user_id]["OnlineSecurity"] = text
    logger.info(f"OnlineSecurity kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q", "Internet xizmati yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣3️⃣ Onlayn Zaxira</b>: Mijoz onlayn zaxira xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ONLINE_BACKUP

# OnlineBackup kiritish
async def online_backup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q", "Internet xizmati yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q, Internet xizmati yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return ONLINE_BACKUP

    user_data[user_id]["OnlineBackup"] = text
    logger.info(f"OnlineBackup kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q", "Internet xizmati yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣4️⃣ Qurilma Himoyasi</b>: Mijoz qurilma himoyasi xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DEVICE_PROTECTION

# DeviceProtection kiritish
async def device_protection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q", "Internet xizmati yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q, Internet xizmati yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return DEVICE_PROTECTION

    user_data[user_id]["DeviceProtection"] = text
    logger.info(f"DeviceProtection kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q", "Internet xizmati yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣5️⃣ Texnik Yordam</b>: Mijoz texnik yordam xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return TECH_SUPPORT

# TechSupport kiritish
async def tech_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q", "Internet xizmati yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q, Internet xizmati yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return TECH_SUPPORT

    user_data[user_id]["TechSupport"] = text
    logger.info(f"TechSupport kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q", "Internet xizmati yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣6️⃣ Streaming TV</b>: Mijoz striming TV xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return STREAMING_TV

# StreamingTV kiritish
async def streaming_tv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q", "Internet xizmati yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q, Internet xizmati yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return STREAMING_TV

    user_data[user_id]["StreamingTV"] = text
    logger.info(f"StreamingTV kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q", "Internet xizmati yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣7️⃣ Streaming Filmlar</b>: Mijoz striming filmlar xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    logger.info(f"StreamingMovies so‘rovi yuborildi (Foydalanuvchi: {user_id})")
    return STREAMING_MOVIES

# StreamingMovies kiritish
async def streaming_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q", "Internet xizmati yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q, Internet xizmati yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return STREAMING_MOVIES

    user_data[user_id]["StreamingMovies"] = text
    logger.info(f"StreamingMovies kiritildi: {text} (Foydalanuvchi: {user_id})")
    reply_keyboard = [["Ha", "Yo'q"]]
    await update.message.reply_text(
        "<b>1️⃣8️⃣ Qog'ozsiz Hisob</b>: Mijoz qog‘ozsiz hisob-kitob xizmatidan foydalanadimi?\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    logger.info(f"PaperlessBilling so‘rovi yuborildi (Foydalanuvchi: {user_id})")
    return PAPERLESS_BILLING

# PaperlessBilling kiritish va bashorat
async def paperless_billing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    valid_options = ["Ha", "Yo'q"]

    if text not in valid_options:
        await update.message.reply_text(
            "<b>❌ Xato!</b> Iltimos, quyidagi variantlardan birini tanlang: Ha, Yo'q. Qayta urinib ko‘ring:",
            parse_mode="HTML"
        )
        return PAPERLESS_BILLING

    user_data[user_id]["PaperlessBilling"] = text
    logger.info(f"PaperlessBilling kiritildi: {text} (Foydalanuvchi: {user_id})")

    # Ma'lumotlarni tayyorlash
    try:
        # TotalCharges ni hisoblash (taxminiy)
        data = user_data[user_id].copy()
        data["TotalCharges"] = data["tenure"] * data["MonthlyCharges"]
        logger.info(f"TotalCharges hisoblandi: {data['TotalCharges']} (Foydalanuvchi: {user_id})")

        # Ma'lumotlarni DataFrame'ga aylantirish
        df = pd.DataFrame([data])

        # Kategorik o'zgaruvchilarni kodlash
        categorical_cols = [
            "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
            "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
            "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
            "PaperlessBilling", "PaymentMethod"
        ]

        # Label Encoding
        for col in ["gender", "Partner", "Dependents", "PhoneService", "PaperlessBilling"]:
            df[col] = df[col].map({"Erkak": 1, "Ayol": 0, "Ha": 1, "Yo'q": 0})

        # MultipleLines kodlash
        df["MultipleLines"] = df["MultipleLines"].map({
            "Ha": "Yes",
            "Yo'q": "No",
            "Telefon xizmati yo'q": "No phone service"
        })

        # Internet xizmatlari kodlash
        for col in ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]:
            df[col] = df[col].map({
                "Ha": "Yes",
                "Yo'q": "No",
                "Internet xizmati yo'q": "No internet service"
            })

        # Contract kodlash
        df["Contract"] = df["Contract"].map({
            "Oy-ma-oy": "Month-to-month",
            "Bir yillik": "One year",
            "Ikki yillik": "Two year"
        })

        # InternetService kodlash
        df["InternetService"] = df["InternetService"].map({
            "Optik tolali": "Fiber optic",
            "DSL": "DSL",
            "Yo'q": "No"
        })

        # PaymentMethod kodlash
        df["PaymentMethod"] = df["PaymentMethod"].map({
            "Elektron chek": "Electronic check",
            "Pochta cheki": "Mailed check",
            "Bank o'tkazmasi (avtomatik)": "Bank transfer (automatic)",
            "Kredit karta (avtomatik)": "Credit card (automatic)"
        })

        # One-Hot Encoding
        categorical_cols_for_encoding = [
            "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
            "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
            "Contract", "PaymentMethod"
        ]
        df_encoded = pd.get_dummies(df, columns=categorical_cols_for_encoding, drop_first=True)
        logger.info(f"Ma'lumotlar kodlandi (Foydalanuvchi: {user_id})")

        # Model uchun kerakli ustunlarni ta'minlash
        expected_columns = model.feature_names_in_
        for col in expected_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[expected_columns]
        logger.info(f"Ustunlar moslashtirildi: {list(df_encoded.columns)} (Foydalanuvchi: {user_id})")

        # Raqamli ustunlarni masshtablash
        numerical_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
        df_encoded[numerical_cols] = scaler.transform(df_encoded[numerical_cols])
        logger.info(f"Raqamli ustunlar masshtablandi (Foydalanuvchi: {user_id})")

        # Bashorat qilish
        prob = model.predict_proba(df_encoded)[:, 1][0]
        prediction = "Ketadi" if prob > 0.5 else "Ketmaydi"
        logger.info(f"Bashorat tayyor: {prediction}, Ehtimollik: {prob * 100:.2f}% (Foydalanuvchi: {user_id})")

        # Natijani ko'rsatish
        await update.message.reply_text(
            "<b>🎊 Bashorat Natijasi</b>\n\n"
            f"<b>📌 Holati</b>: {prediction}\n"
            f"<b>📈 Ehtimollik</b>: {prob * 100:.2f}%\n\n"
            "Yana bashorat qilish uchun /predict buyrug‘ini ishlat!",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        logger.error(f"Bashoratda xato yuz berdi: {str(e)} (Foydalanuvchi: {user_id})")
        await update.message.reply_text(
            "<b>❌ Xato!</b> Bashorat qilishda xato yuz berdi! Iltimos, qayta urinib ko‘ring yoki /help orqali yordam oling.",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )

    # Ma'lumotlarni tozalash
    user_data.pop(user_id, None)
    return ConversationHandler.END

# Jarayonni bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data.pop(user_id, None)
    await update.message.reply_text(
        "<b>🚫 Jarayon bekor qilindi.</b> Yangi bashorat uchun /predict buyrug‘ini ishlat!",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Xato boshqaruv
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Xato yuz berdi: {context.error}")
    try:
        await update.message.reply_text(
            "<b>❌ Botda xato yuz berdi!</b> Iltimos, qayta urinib ko‘ring yoki /help orqali yordam oling.",
            parse_mode="HTML"
        )
    except:
        pass

def main() -> None:
    # Botni ishga tushirish
    try:
        application = Application.builder().token("7690742329:AAEyd_1snMwBhalcPsMpqIqDybN0v5JZ0H8").build()
        logger.info("Bot muvaffaqiyatli ishga tushirildi")
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xato: {str(e)}")
        raise

    # ConversationHandler sozlamalari
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("predict", predict)],
        states={
            TENURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, tenure)],
            MONTHLY_CHARGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, monthly_charges)],
            CONTRACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract)],
            INTERNET_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, internet_service)],
            PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_method)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            SENIOR_CITIZEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, senior_citizen)],
            PARTNER: [MessageHandler(filters.TEXT & ~filters.COMMAND, partner)],
            DEPENDENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, dependents)],
            PHONE_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_service)],
            MULTIPLE_LINES: [MessageHandler(filters.TEXT & ~filters.COMMAND, multiple_lines)],
            ONLINE_SECURITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, online_security)],
            ONLINE_BACKUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, online_backup)],
            DEVICE_PROTECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, device_protection)],
            TECH_SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, tech_support)],
            STREAMING_TV: [MessageHandler(filters.TEXT & ~filters.COMMAND, streaming_tv)],
            STREAMING_MOVIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, streaming_movies)],
            PAPERLESS_BILLING: [MessageHandler(filters.TEXT & ~filters.COMMAND, paperless_billing)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Buyruqlar va xatolarni boshqarish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # Botni ishga tushirish
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()