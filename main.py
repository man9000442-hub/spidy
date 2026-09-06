"""h
سكريبت يحول أي صورة إلى رسمة متحركة بلغة turtle
النسخة دي معدّلة عشان تشتغل مع صور خلفيتها سودا والشكل فاتح/ملوّن
(زي صورة سبايدرمان ماسك حبل الشبكة النازل لجثة)

مطلوب تثبيت المكتبات أولاً:
    pip install opencv-python numpy
(مكتبة turtle موجودة جاهزة مع بايثون)
"""

import cv2
import numpy as np
import turtle
import time

# ==== الإعدادات ====
IMAGE = "spiderman.jpg"   # ضع هنا اسم/مسار صورتك (لازم تكون في نفس مجلد السكريبت)
TARGET_HEIGHT = 600       # ارتفاع الرسمة على الشاشة (بكسل)
THRESHOLD_VALUE = 30      # قيمة العتبة لفصل الشكل عن الخلفية السودا (زوّدها لو فيه ضوضاء، قلّلها لو الشكل ناقص أجزاء)
MIN_CONTOUR_POINTS = 15   # أقل عدد نقاط للـ contour عشان يترسم (يشيل الكتابة/العلامة المائية الصغيرة)
DRAW_SPEED = 1            # سرعة رسم السلحفاة: 0 = أسرع سرعة، من 1 لـ 10 = أبطأ (1 هي أبطأ سرعة مدمجة)
ANIMATE = True            # True = تشوف الرسم بيترسم خطوة بخطوة، False = يظهر دفعة واحدة بسرعة
EXTRA_SLOWDOWN = 0        # عامل إبطاء إضافي (اضرب فيه عشان تبطئ أكتر من أقصى بطء متاح في turtle) - 1 = بدون إبطاء زيادة، 8 = أبطأ بـ 8 أضعاف
POINT_DELAY_MS = 10        # تأخير إضافي (ميلي ثانية) بعد كل نقطة، لو عايز تحكم أدق في السرعة
FILL_COLOR = "white"      # لون التلوين (الشكل فاتح على خلفية سودا، فالأنسب أبيض)
BG_COLOR = "black"        # لون خلفية شاشة الرسم

# ==== قراءة الصورة ====
img = cv2.imread(IMAGE)

if img is None:
    print("الصورة غير موجودة! تأكد من اسم/مسار الملف.")
    exit()

# ==== تصغير الصورة مع الحفاظ على النسبة ====
ratio = TARGET_HEIGHT / img.shape[0]
width = int(img.shape[1] * ratio)
height = TARGET_HEIGHT
img = cv2.resize(img, (width, height))

# ==== استخراج الشكل عن الخلفية السودا ====
# بناخد أعلى قيمة بين قنوات B/G/R لكل بكسل، عشان نمسك أي لون (مش بس الأبيض)
# وده أفضل من التحويل الرمادي العادي في حالة وجود ألوان زاهية على خلفية سودا
gray = np.max(img, axis=2)
_, thresh = cv2.threshold(gray, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)

# ==== استخراج الحواف (contours) ====
contours, _ = cv2.findContours(
    thresh,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_NONE
)

# شيل أي contours صغيرة جدًا (ضوضاء / كتابة / علامة مائية)
contours = [c for c in contours if len(c) >= MIN_CONTOUR_POINTS]

# ==== إعداد شاشة الرسم ====
screen = turtle.Screen()
screen.setup(width=width + 100, height=height + 100)
screen.bgcolor(BG_COLOR)
screen.title("Image to Turtle Drawing")

if ANIMATE:
    # كل ما EXTRA_SLOWDOWN أكبر، كل ما التأخير بين كل تحديث للشاشة أكبر = رسم أبطأ
    screen.tracer(1, 10 * EXTRA_SLOWDOWN)
else:
    screen.tracer(0, 0)   # يرسم كل حاجة في الخلفية وبعدين يعرضها مرة واحدة بسرعة

t = turtle.Turtle()
t.hideturtle()
t.speed(DRAW_SPEED)
t.pencolor(FILL_COLOR)
t.fillcolor(FILL_COLOR)
t.width(1)


def to_turtle_coords(x, y):
    """تحويل إحداثيات الصورة (0,0 في أعلى الشمال) لإحداثيات turtle (0,0 في النص)"""
    tx = x - width / 2
    ty = height / 2 - y
    return tx, ty


# ==== رسم كل contour مع تلوينه ====
for contour in contours:
    t.penup()
    start_x, start_y = contour[0][0]
    tx, ty = to_turtle_coords(start_x, start_y)
    t.goto(tx, ty)
    t.pendown()
    t.begin_fill()

    for point in contour[1:]:
        x, y = point[0]
        tx, ty = to_turtle_coords(x, y)
        t.goto(tx, ty)
        if POINT_DELAY_MS > 0:
            time.sleep(POINT_DELAY_MS / 1000)

    t.end_fill()

if not ANIMATE:
    screen.update()

print("تم رسم الصورة بنجاح!")
turtle.done()
