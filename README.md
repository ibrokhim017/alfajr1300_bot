# Al Fajr Telegram tushum bot

Telegram guruhiga keladigan SMS xabarlaridan tushumni saqlaydi va hisobot beradi.

## Buyruqlar

- `/today` — bugungi tushum
- `/week` — so‘nggi 7 kun
- `/month` — so‘nggi 30 kun
- `/stats` — umumiy statistika
- `/help` — yordam

Bot faqat `GROUP_ID` bilan belgilangan guruhdagi kirim xabarlarini saqlaydi. Bir xil xabar ikki marta yuborilsa, u faqat bir marta hisoblanadi.

## Render sozlamasi

1. Render’da **New → Blueprint** ni tanlang va shu repository’ni ulang.
2. Ikkita secret qo‘shing:
   - `BOT_TOKEN`: BotFather bergan yangi token
   - `GROUP_ID`: SMS keladigan guruh IDsi, masalan `-1001234567890`
3. Deploy qiling.

Loyiha Docker orqali Python 3.13 bilan ishlaydi; shu sababli Render’ning Python 3.14 event-loop muammosi bo‘lmaydi.

> Muhim: Render’ning bepul worker rejimida SQLite fayli doimiy saqlanmasligi mumkin. Muhim moliyaviy ma’lumotlar uchun persistent disk yoki PostgreSQL ishlating.

## Telegram sozlamasi

Botni SMS keladigan guruhga qo‘shing va BotFather’dan **Group Privacy** ni o‘chirib qo‘ying. Shunda bot guruhdagi SMS Forwarder xabarlarini ko‘ra oladi.
