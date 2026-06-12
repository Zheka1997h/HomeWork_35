import asyncio
import logging
import os

import requests
import io
import urllib.parse
import math
import imageio
import numpy as np
from dotenv import load_dotenv
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    BufferedInputFile
from aiogram.filters import CommandStart, Command

# Эта команда загружает ключи из файла .env
load_dotenv()

# API-ключи
API_Bot =  '8746829931:AAHxWK0WQLMvvGqDPRTPRirp5BxJrNTk3ig'
WEATHER_API_KEY = '0c930ee79715b0b638b413e07cbc1d1b'

bot = Bot(API_Bot)
dp = Dispatcher()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌤 Погода"), KeyboardButton(text="🎵 Музыка")],
        [KeyboardButton(text="💰 Финансы"), KeyboardButton(text="💵 Курс Доллара")],
        [KeyboardButton(text="🖼 Оживление фото"), KeyboardButton(text="🎨 Редактирование фото")],
        [KeyboardButton(text="🎮 Игры"), KeyboardButton(text="ℹ Помощь")],
        [KeyboardButton(text="👋 О боте")]
    ],
    resize_keyboard=True
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

PHRASES_MAP = {
    ('привет', 'здравствуй', 'добрый день', 'доброе утро', 'добрый вечер', 'хелло'):
        'Здравствуйте! Чем могу помочь?',
    ('как дела', 'как ты', 'как настроение', 'что нового'):
        'Отлично, спасибо! А у вас как дела?',
    ('что делаешь', 'чем занят', 'чем занимаешься'):
        'Общаюсь с вами и учусь новому! Чем могу помочь?',
    ('пока', 'до свидания', 'увидимся', 'прощай'):
        'До свидания! Буду рад пообщаться снова! 👋',
    ('спасибо', 'благодарю', 'спасибо большое'):
        'Пожалуйста! Всегда рад помочь! 😊',
    ('кто ты', 'что ты за бот', 'расскажи о себе'):
        'Я — бот с ИИ-зрением! Могу оживлять людей, редактировать фото и играть в игры! 🎬🎮',
}

CITY_DECLENSION_EXCEPTIONS = {
    'темрюк': 'Темрюке', 'сочи': 'Сочи', 'анапа': 'Анапе', 'геленджик': 'Геленджике',
    'новороссийск': 'Новороссийске', 'краснодар': 'Краснодаре', 'москва': 'Москве',
    'санкт-петербург': 'Санкт-Петербурге', 'петербург': 'Петербурге', 'казань': 'Казани',
}


def decline_city_prepositional(city_name: str) -> str:
    city_lower = city_name.lower().strip()
    if city_lower in CITY_DECLENSION_EXCEPTIONS:
        return CITY_DECLENSION_EXCEPTIONS[city_lower]
    if city_lower[-1] in 'бвгджзйклмнпрстфхцчшщ':
        if city_lower.endswith('ий'):
            return city_name[:-2] + 'ии'
        return city_name + 'е'
    if city_lower.endswith('а') or city_lower.endswith('я'):
        return city_name[:-1] + 'е'
    if city_lower.endswith('ь'):
        return city_name + 'е'
    return city_name


FONT_PATH = "arial.ttf"


def bytesio_to_buffered(bio: io.BytesIO, filename: str = "image.png") -> BufferedInputFile:
    bio.seek(0)
    return BufferedInputFile(bio.read(), filename=filename)


# ============================================
# 🧠 AI-СЕГМЕНТАЦИЯ ЧЕЛОВЕКА
# ============================================

class BodyAnimator:
    def __init__(self):
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                min_detection_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            self.available = True
        except Exception as e:
            logging.error(f"MediaPipe не доступен: {e}")
            self.available = False
            self.pose = None

        self.LANDMARKS = {
            'nose': 0,
            'left_eye': 2, 'right_eye': 5,
            'left_ear': 7, 'right_ear': 8,
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28,
        }

    def detect_pose(self, img: Image.Image):
        if not self.available or self.pose is None:
            return None
        try:
            img_rgb = np.array(img)
            results = self.pose.process(img_rgb)
            if not results.pose_landmarks:
                return None
            h, w = img_rgb.shape[:2]
            landmarks = {}
            for name, idx in self.LANDMARKS.items():
                lm = results.pose_landmarks.landmark[idx]
                if lm.visibility < 0.5:
                    continue
                landmarks[name] = (int(lm.x * w), int(lm.y * h))
            return landmarks if landmarks else None
        except Exception as e:
            logging.error(f"Ошибка детекции позы: {e}")
            return None

    def create_body_masks(self, img: Image.Image, landmarks: dict):
        w, h = img.size
        masks = {}
        if 'nose' in landmarks:
            nose = landmarks['nose']
            if 'left_ear' in landmarks:
                ear = landmarks['left_ear']
                head_radius = max(40, int(math.dist(nose, ear) * 1.5))
            elif 'left_shoulder' in landmarks:
                shoulder = landmarks['left_shoulder']
                head_radius = max(40, int(math.dist(nose, shoulder) * 0.6))
            else:
                head_radius = 60
            mask = Image.new('L', (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (nose[0] - head_radius, nose[1] - head_radius,
                 nose[0] + head_radius, nose[1] + head_radius),
                fill=255
            )
            masks['head'] = mask
        if all(k in landmarks for k in ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']):
            ls = landmarks['left_shoulder']
            rs = landmarks['right_shoulder']
            lh = landmarks['left_hip']
            rh = landmarks['right_hip']
            mask = Image.new('L', (w, h), 0)
            draw = ImageDraw.Draw(mask)
            polygon = [ls, rs, rh, lh]
            draw.polygon(polygon, fill=255)
            masks['torso'] = mask
        if all(k in landmarks for k in ['left_shoulder', 'left_elbow', 'left_wrist']):
            ls = landmarks['left_shoulder']
            le = landmarks['left_elbow']
            lw = landmarks['left_wrist']
            mask = self._create_limb_mask(w, h, [ls, le, lw], thickness=30)
            masks['left_arm'] = mask
        if all(k in landmarks for k in ['right_shoulder', 'right_elbow', 'right_wrist']):
            rs = landmarks['right_shoulder']
            re = landmarks['right_elbow']
            rw = landmarks['right_wrist']
            mask = self._create_limb_mask(w, h, [rs, re, rw], thickness=30)
            masks['right_arm'] = mask
        if all(k in landmarks for k in ['left_hip', 'left_knee', 'left_ankle']):
            lh = landmarks['left_hip']
            lk = landmarks['left_knee']
            la = landmarks['left_ankle']
            mask = self._create_limb_mask(w, h, [lh, lk, la], thickness=40)
            masks['left_leg'] = mask
        if all(k in landmarks for k in ['right_hip', 'right_knee', 'right_ankle']):
            rh = landmarks['right_hip']
            rk = landmarks['right_knee']
            ra = landmarks['right_ankle']
            mask = self._create_limb_mask(w, h, [rh, rk, ra], thickness=40)
            masks['right_leg'] = mask
        return masks

    def _create_limb_mask(self, w, h, points, thickness=30):
        mask = Image.new('L', (w, h), 0)
        draw = ImageDraw.Draw(mask)
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=255, width=thickness)
            draw.ellipse(
                (points[i][0] - thickness // 2, points[i][1] - thickness // 2,
                 points[i][0] + thickness // 2, points[i][1] + thickness // 2),
                fill=255
            )
        last = points[-1]
        draw.ellipse(
            (last[0] - thickness // 2, last[1] - thickness // 2,
             last[0] + thickness // 2, last[1] + thickness // 2),
            fill=255
        )
        return mask

    def animate_body_part(self, img: Image.Image, mask: Image.Image,
                          pivot: tuple, angle_deg: float) -> Image.Image:
        rotated_mask = mask.rotate(angle_deg, center=pivot, resample=Image.BICUBIC)
        rotated_img = img.rotate(angle_deg, center=pivot, resample=Image.BICUBIC,
                                 fillcolor=(0, 0, 0))
        result = img.copy()
        result.paste(rotated_img, mask=rotated_mask)
        return result


body_animator = BodyAnimator()

# ============================================
# 📊 ХРАНИЛИЩЕ СОСТОЯНИЙ
# ============================================
user_states = {}  # Для отслеживания состояния пользователя


# ============================================
# 🎨 РЕДАКТИРОВАНИЕ ФОТО
# ============================================

@dp.message(F.text == "🎨 Редактирование фото")
async def photo_edit_request(message: Message):
    user_states[message.from_user.id] = 'edit_mode'
    await message.answer(
        "🎨 *Редактирование фото!*\n\n"
        "📸 Отправьте мне фотографию, и я применю эффекты:\n\n"
        "✨ **Основные эффекты:**\n"
        "• Ч/Б (черно-белое)\n"
        "• Сепия (старинное фото)\n"
        "• Размытие\n"
        "• Резкость\n"
        "• Контраст\n"
        "• Яркость\n"
        "• Инверсия цветов\n"
        "• Эффект эскиза\n\n"
        "⚠️ _Обработка занимает 2-5 секунд_",
        parse_mode="Markdown"
    )


@dp.message(F.text == "🖼 Оживление фото")
async def photo_animation_request(message: Message):
    user_states[message.from_user.id] = 'animate_mode'
    await message.answer(
        "🎬 *Оживление фото с помощью ИИ!*\n\n"
        "Отправьте мне фотографию с *человеком* или *животным*, и я:\n\n"
        "🧠 *Найду тело* с помощью нейросети (MediaPipe Pose)\n"
        "✂️ *Разделю на части*: голову, руки, ноги, торс\n"
        "🎞 *Анимирую каждую часть* независимо:\n"
        "  • 👤 Голова будет поворачиваться\n"
        "  • 💪 Руки будут двигаться в локтях\n"
        "  • 🦵 Ноги будут шагать\n"
        "  • 🫁 Торс будет «дышать»\n\n"
        "⚠️ _Обработка занимает 10-30 секунд_",
        parse_mode="Markdown"
    )


# ============================================
# 📸 ОБРАБОТКА ФОТО (УНИВЕРСАЛЬНАЯ)
# ============================================

@dp.message(F.photo)
async def handle_photo(message: Message):
    """Универсальный обработчик фото - определяет режим по состоянию"""
    user_id = message.from_user.id
    mode = user_states.get(user_id, 'none')

    try:
        await message.answer("⏳ Загружаю фото...")
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)

        img = Image.open(io.BytesIO(file_bytes.read()))
        if img.mode != 'RGB':
            img = img.convert('RGB')

        if mode == 'edit_mode':
            # РЕДАКТИРОВАНИЕ
            if not hasattr(handle_photo, 'edit_photos'):
                handle_photo.edit_photos = {}
            handle_photo.edit_photos[user_id] = img

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⚫ Ч/Б", callback_data="edit_grayscale"),
                        InlineKeyboardButton(text="🟤 Сепия", callback_data="edit_sepia"),
                    ],
                    [
                        InlineKeyboardButton(text="🌫 Размытие", callback_data="edit_blur"),
                        InlineKeyboardButton(text="🔪 Резкость", callback_data="edit_sharpen"),
                    ],
                    [
                        InlineKeyboardButton(text="🔆 Контраст", callback_data="edit_contrast"),
                        InlineKeyboardButton(text="💡 Яркость", callback_data="edit_brightness"),
                    ],
                    [
                        InlineKeyboardButton(text="🔄 Инверсия", callback_data="edit_invert"),
                        InlineKeyboardButton(text="✏️ Эскиз", callback_data="edit_sketch"),
                    ],
                    [
                        InlineKeyboardButton(text="🎨 Постеризация", callback_data="edit_posterize"),
                        InlineKeyboardButton(text="🌈 RGB сдвиг", callback_data="edit_rgb_shift"),
                    ],
                ]
            )
            await message.answer("✅ Фото загружено! Выберите эффект:", reply_markup=keyboard)

        elif mode == 'animate_mode':
            # ОЖИВЛЕНИЕ
            img.thumbnail((600, 600))
            landmarks = body_animator.detect_pose(img)

            if landmarks and body_animator.available:
                masks = body_animator.create_body_masks(img, landmarks)

                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="👤 Анимация головы", callback_data="anim_head")],
                        [InlineKeyboardButton(text="💪 Анимация рук", callback_data="anim_arms")],
                        [InlineKeyboardButton(text="🦵 Анимация ног", callback_data="anim_legs")],
                        [InlineKeyboardButton(text="🫁 Дыхание (торс)", callback_data="anim_breathe")],
                        [InlineKeyboardButton(text="🕺 ПОЛНЫЙ ТАНЕЦ (всё сразу!)", callback_data="anim_full")],
                    ]
                )

                await message.answer(
                    f"✅ *Человек найден!* Обнаружено {len(landmarks)} точек тела.\n\n"
                    f"Выберите анимацию:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )

                if not hasattr(handle_photo, 'animate_data'):
                    handle_photo.animate_data = {}
                handle_photo.animate_data[user_id] = {
                    'img': img,
                    'landmarks': landmarks,
                    'masks': masks,
                    'type': 'human'
                }
            else:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🫁 Дыхание", callback_data="simple_breath")],
                        [InlineKeyboardButton(text="🔍 Зум", callback_data="simple_zoom")],
                        [InlineKeyboardButton(text="📳 Встряска", callback_data="simple_shake")],
                        [InlineKeyboardButton(text="🎡 Покачивание", callback_data="simple_sway")],
                    ]
                )

                await message.answer(
                    "🐾 *Человек не найден на фото.*\n\n"
                    "Возможно, это животное или объект. Для них доступна простая анимация.\n\n"
                    "Выберите эффект:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )

                if not hasattr(handle_photo, 'animate_data'):
                    handle_photo.animate_data = {}
                handle_photo.animate_data[user_id] = {
                    'img': img,
                    'type': 'simple'
                }
        else:
            await message.answer(
                "❓ Неизвестный режим.\n\n"
                "Сначала выберите:\n"
                "• 🎨 Редактирование фото - для эффектов\n"
                "• 🖼 Оживление фото - для анимации"
            )

    except Exception as e:
        logging.error(f"Ошибка обработки фото: {e}")
        await message.answer(f"❌ Произошла ошибка: {e}")


# ============================================
# 🎨 ФУНКЦИИ РЕДАКТИРОВАНИЯ
# ============================================

def apply_grayscale(img: Image.Image) -> Image.Image:
    return ImageOps.grayscale(img).convert('RGB')


def apply_sepia(img: Image.Image) -> Image.Image:
    width, height = img.size
    pixels = img.load()
    sepia_img = Image.new('RGB', (width, height))
    sepia_pixels = sepia_img.load()
    for i in range(width):
        for j in range(height):
            r, g, b = pixels[i, j]
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            sepia_pixels[i, j] = (min(255, tr), min(255, tg), min(255, tb))
    return sepia_img


def apply_blur(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius=5))


def apply_sharpen(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.SHARPEN)


def apply_contrast(img: Image.Image) -> Image.Image:
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(2.0)


def apply_brightness(img: Image.Image) -> Image.Image:
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(1.5)


def apply_invert(img: Image.Image) -> Image.Image:
    return ImageOps.invert(img)


def apply_sketch(img: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(img)
    inverted = ImageOps.invert(gray)
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=5))
    sketch = Image.blend(gray, blurred, 0.5)
    return sketch.convert('RGB')


def apply_posterize(img: Image.Image) -> Image.Image:
    return ImageOps.posterize(img, bits=3)


def apply_rgb_shift(img: Image.Image) -> Image.Image:
    r, g, b = img.split()
    r = r.offset(5, 0)
    b = b.offset(-5, 0)
    return Image.merge('RGB', (r, g, b))


@dp.callback_query(F.data.startswith("edit_"))
async def apply_photo_effect(callback_query):
    try:
        user_id = callback_query.from_user.id
        if not hasattr(handle_photo, 'edit_photos') or user_id not in handle_photo.edit_photos:
            await callback_query.answer("Сначала отправьте фото в режиме редактирования!", show_alert=True)
            return

        await callback_query.answer("⏳ Применяю эффект...")
        img = handle_photo.edit_photos[user_id]
        effect = callback_query.data

        if effect == "edit_grayscale":
            result = apply_grayscale(img)
            caption = "⚫ Черно-белое фото"
        elif effect == "edit_sepia":
            result = apply_sepia(img)
            caption = "🟤 Эффект сепии"
        elif effect == "edit_blur":
            result = apply_blur(img)
            caption = "🌫 Размытие"
        elif effect == "edit_sharpen":
            result = apply_sharpen(img)
            caption = "🔪 Повышенная резкость"
        elif effect == "edit_contrast":
            result = apply_contrast(img)
            caption = "🔆 Усиленный контраст"
        elif effect == "edit_brightness":
            result = apply_brightness(img)
            caption = "💡 Повышенная яркость"
        elif effect == "edit_invert":
            result = apply_invert(img)
            caption = "🔄 Инверсия цветов"
        elif effect == "edit_sketch":
            result = apply_sketch(img)
            caption = "✏️ Эффект эскиза"
        elif effect == "edit_posterize":
            result = apply_posterize(img)
            caption = "🎨 Постеризация"
        elif effect == "edit_rgb_shift":
            result = apply_rgb_shift(img)
            caption = "🌈 RGB сдвиг"
        else:
            await callback_query.answer("Неизвестный эффект", show_alert=True)
            return

        bio = io.BytesIO()
        result.save(bio, format='PNG')
        bio.seek(0)
        photo_file = bytesio_to_buffered(bio, "edited.png")
        await callback_query.message.answer_photo(photo=photo_file, caption=caption)

    except Exception as e:
        logging.error(f"Ошибка применения эффекта: {e}")
        await callback_query.answer(f"Ошибка: {e}", show_alert=True)


# ============================================
# 🎬 АНИМАЦИИ
# ============================================

def _animate_head(img: Image.Image, masks: dict, landmarks: dict) -> io.BytesIO:
    if 'head' not in masks or 'nose' not in landmarks:
        return None
    head_mask = masks['head']
    pivot = landmarks['nose']
    frames = []
    num_frames = 24
    for i in range(num_frames):
        t = i / num_frames
        angle = 15 * math.sin(t * 2 * math.pi)
        frame = body_animator.animate_body_part(img, head_mask, pivot, angle)
        frames.append(np.array(frame))
    return _frames_to_gif(frames)


def _animate_arms(img: Image.Image, masks: dict, landmarks: dict) -> io.BytesIO:
    frames = []
    num_frames = 24
    left_pivot = landmarks.get('left_shoulder')
    right_pivot = landmarks.get('right_shoulder')
    for i in range(num_frames):
        t = i / num_frames
        angle = 20 * math.sin(t * 2 * math.pi)
        frame = img.copy()
        if 'left_arm' in masks and left_pivot:
            frame = body_animator.animate_body_part(frame, masks['left_arm'], left_pivot, angle)
        if 'right_arm' in masks and right_pivot:
            frame = body_animator.animate_body_part(frame, masks['right_arm'], right_pivot, -angle)
        frames.append(np.array(frame))
    return _frames_to_gif(frames)


def _animate_legs(img: Image.Image, masks: dict, landmarks: dict) -> io.BytesIO:
    frames = []
    num_frames = 24
    left_pivot = landmarks.get('left_hip')
    right_pivot = landmarks.get('right_hip')
    for i in range(num_frames):
        t = i / num_frames
        angle = 15 * math.sin(t * 2 * math.pi)
        frame = img.copy()
        if 'left_leg' in masks and left_pivot:
            frame = body_animator.animate_body_part(frame, masks['left_leg'], left_pivot, angle)
        if 'right_leg' in masks and right_pivot:
            frame = body_animator.animate_body_part(frame, masks['right_leg'], right_pivot, -angle)
        frames.append(np.array(frame))
    return _frames_to_gif(frames)


def _animate_breathe(img: Image.Image, masks: dict, landmarks: dict) -> io.BytesIO:
    frames = []
    num_frames = 24
    if 'left_shoulder' in landmarks and 'left_hip' in landmarks:
        ls = landmarks['left_shoulder']
        lh = landmarks['left_hip']
        pivot = ((ls[0] + lh[0]) // 2, (ls[1] + lh[1]) // 2)
    else:
        pivot = (img.size[0] // 2, img.size[1] // 2)
    for i in range(num_frames):
        t = i / num_frames
        scale = 1.0 + 0.05 * math.sin(t * 2 * math.pi)
        if 'torso' in masks:
            torso_mask = masks['torso']
            w, h = img.size
            new_w, new_h = int(w * scale), int(h * scale)
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            resized_mask = torso_mask.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            frame = img.copy()
            torso_crop = resized.crop((left, top, left + w, top + h))
            mask_crop = resized_mask.crop((left, top, left + w, top + h))
            frame.paste(torso_crop, mask=mask_crop)
            frames.append(np.array(frame))
        else:
            frames.append(np.array(img))
    return _frames_to_gif(frames)


def _animate_full(img: Image.Image, masks: dict, landmarks: dict) -> io.BytesIO:
    frames = []
    num_frames = 30
    left_shoulder = landmarks.get('left_shoulder')
    right_shoulder = landmarks.get('right_shoulder')
    left_hip = landmarks.get('left_hip')
    right_hip = landmarks.get('right_hip')
    nose = landmarks.get('nose')
    if left_shoulder and left_hip:
        torso_pivot = ((left_shoulder[0] + left_hip[0]) // 2,
                       (left_shoulder[1] + left_hip[1]) // 2)
    else:
        torso_pivot = (img.size[0] // 2, img.size[1] // 2)
    for i in range(num_frames):
        t = i / num_frames
        phase = t * 2 * math.pi
        frame = img.copy()
        if 'head' in masks and nose:
            head_angle = 12 * math.sin(phase)
            frame = body_animator.animate_body_part(frame, masks['head'], nose, head_angle)
        if 'left_arm' in masks and left_shoulder:
            arm_angle = 25 * math.sin(phase)
            frame = body_animator.animate_body_part(frame, masks['left_arm'], left_shoulder, arm_angle)
        if 'right_arm' in masks and right_shoulder:
            arm_angle = 25 * math.sin(phase + math.pi)
            frame = body_animator.animate_body_part(frame, masks['right_arm'], right_shoulder, arm_angle)
        if 'left_leg' in masks and left_hip:
            leg_angle = 15 * math.sin(phase)
            frame = body_animator.animate_body_part(frame, masks['left_leg'], left_hip, leg_angle)
        if 'right_leg' in masks and right_hip:
            leg_angle = 15 * math.sin(phase + math.pi)
            frame = body_animator.animate_body_part(frame, masks['right_leg'], right_hip, leg_angle)
        frames.append(np.array(frame))
    return _frames_to_gif(frames)


def _frames_to_gif(frames: list) -> io.BytesIO:
    bio = io.BytesIO()
    imageio.mimsave(bio, frames, format='GIF', duration=0.08, loop=0)
    bio.seek(0)
    return bio


def _simple_animation(img: Image.Image, anim_type: str) -> io.BytesIO:
    img = img.copy()
    img.thumbnail((512, 512), Image.LANCZOS)
    width, height = img.size
    frames = []
    num_frames = 20
    if anim_type == "breath":
        for i in range(num_frames):
            t = i / num_frames
            scale = 1.0 + 0.1 * math.sin(t * 2 * math.pi)
            new_w, new_h = int(width * scale), int(height * scale)
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - width) // 2
            top = (new_h - height) // 2
            cropped = resized.crop((left, top, left + width, top + height))
            frames.append(np.array(cropped))
    elif anim_type == "zoom":
        for i in range(num_frames):
            t = i / (num_frames - 1)
            scale = 1.0 + 1.5 * t
            new_w, new_h = int(width * scale), int(height * scale)
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - width) // 2
            top = (new_h - height) // 2
            cropped = resized.crop((left, top, left + width, top + height))
            frames.append(np.array(cropped))
    elif anim_type == "shake":
        random.seed(42)
        for i in range(num_frames):
            offset_x = random.randint(-12, 12)
            offset_y = random.randint(-12, 12)
            bg_color = img.getpixel((0, 0))
            shaken = Image.new('RGB', (width, height), bg_color)
            shaken.paste(img, (offset_x, offset_y))
            frames.append(np.array(shaken))
    elif anim_type == "sway":
        for i in range(num_frames):
            t = i / num_frames
            angle = 5 * math.sin(t * 2 * math.pi)
            rotated = img.rotate(angle, resample=Image.BICUBIC, fillcolor=(0, 0, 0))
            frames.append(np.array(rotated))
    return _frames_to_gif(frames)


@dp.callback_query(F.data.in_(["anim_head", "anim_arms", "anim_legs", "anim_breathe", "anim_full"]))
async def animate_body_part_callback(callback_query):
    try:
        user_id = callback_query.from_user.id
        if not hasattr(handle_photo, 'animate_data') or user_id not in handle_photo.animate_data:
            await callback_query.answer("Сначала отправьте фото в режиме оживления!", show_alert=True)
            return

        data = handle_photo.animate_data[user_id]
        if data.get('type') != 'human':
            await callback_query.answer("Для этой анимации нужно фото с человеком!", show_alert=True)
            return

        await callback_query.answer("🎬 Создаю анимацию...")
        await callback_query.message.edit_text("🧠 ИИ создаёт анимацию...\n⏳ Подождите 10-30 секунд")

        img = data['img']
        masks = data['masks']
        landmarks = data['landmarks']
        anim_type = callback_query.data

        gif_bio = None
        caption = ""

        if anim_type == "anim_head":
            gif_bio = _animate_head(img, masks, landmarks)
            caption = "👤 Анимация головы — ИИ двигает лицо!"
        elif anim_type == "anim_arms":
            gif_bio = _animate_arms(img, masks, landmarks)
            caption = "💪 Анимация рук — руки двигаются в локтях!"
        elif anim_type == "anim_legs":
            gif_bio = _animate_legs(img, masks, landmarks)
            caption = "🦵 Анимация ног — шагающие движения!"
        elif anim_type == "anim_breathe":
            gif_bio = _animate_breathe(img, masks, landmarks)
            caption = "🫁 Дыхание — торс расширяется и сжимается!"
        elif anim_type == "anim_full":
            gif_bio = _animate_full(img, masks, landmarks)
            caption = "🕺 ПОЛНЫЙ ТАНЕЦ — двигаются голова, руки, ноги и торс!"

        if gif_bio is None:
            await callback_query.message.edit_text("❌ Не удалось создать анимацию — не найдены нужные части тела.")
            return

        gif_file = BufferedInputFile(gif_bio.read(), filename="animation.gif")
        await callback_query.message.answer_animation(animation=gif_file, caption=caption)
        try:
            await callback_query.message.delete()
        except:
            pass

    except Exception as e:
        logging.error(f"Ошибка анимации тела: {e}")
        try:
            await callback_query.message.edit_text(f"❌ Ошибка: {e}")
        except:
            await callback_query.answer("Ошибка", show_alert=True)


@dp.callback_query(F.data.in_(["simple_breath", "simple_zoom", "simple_shake", "simple_sway"]))
async def simple_animation_callback(callback_query):
    try:
        user_id = callback_query.from_user.id
        if not hasattr(handle_photo, 'animate_data') or user_id not in handle_photo.animate_data:
            await callback_query.answer("Сначала отправьте фото в режиме оживления!", show_alert=True)
            return

        data = handle_photo.animate_data[user_id]
        img = data['img']

        await callback_query.answer("🎬 Создаю анимацию...")
        await callback_query.message.edit_text("⏳ Создаю GIF-анимацию...")

        anim_type = callback_query.data.replace("simple_", "")
        gif_bio = _simple_animation(img, anim_type)

        captions = {
            "breath": "🫁 Дыхание",
            "zoom": "🔍 Зум",
            "shake": "📳 Встряска",
            "sway": "🎡 Покачивание",
        }
        caption = captions.get(anim_type, "🎬 Анимация готова!")

        gif_file = BufferedInputFile(gif_bio.read(), filename="animation.gif")
        await callback_query.message.answer_animation(animation=gif_file, caption=caption)
        try:
            await callback_query.message.delete()
        except:
            pass

    except Exception as e:
        logging.error(f"Ошибка простой анимации: {e}")
        try:
            await callback_query.message.edit_text(f"❌ Ошибка: {e}")
        except:
            await callback_query.answer("Ошибка", show_alert=True)


# ============================================
# 🎮 ИГРЫ
# ============================================

game_states = {}


@dp.message(F.text == "🎮 Игры")
async def games_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔢 Угадай число", callback_data="game_guess_number"),
                InlineKeyboardButton(text="✊ Камень-Ножницы-Бумага", callback_data="game_rps"),
            ],
            [
                InlineKeyboardButton(text="🎲 Кубик", callback_data="game_dice"),
                InlineKeyboardButton(text="🎯 Викторина", callback_data="game_quiz"),
            ],
            [
                InlineKeyboardButton(text="👆 Кликер", callback_data="game_clicker"),
            ],
        ]
    )
    await message.answer(
        "🎮 *Игры!*\n\n"
        "Выберите игру:\n\n"
        "🔢 **Угадай число** - я загадаю число от 1 до 100\n"
        "✊ **Камень-Ножницы-Бумага** - классическая игра\n"
        "🎲 **Кубик** - бросок виртуального кубика\n"
        "🎯 **Викторина** - проверь свои знания\n"
        "👆 **Кликер** - кликай как можно быстрее!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "game_guess_number")
async def start_guess_number(callback_query):
    number = random.randint(1, 100)
    game_states[callback_query.from_user.id] = {
        'game': 'guess_number',
        'number': number,
        'attempts': 0
    }
    await callback_query.message.answer(
        "🔢 **Угадай число!**\n\n"
        "Я загадал число от 1 до 100.\n"
        "Попробуй угадать!\n\n"
        "Введи число:",
        parse_mode="Markdown"
    )
    await callback_query.answer()


@dp.message(lambda message: message.text and message.text.isdigit())
async def handle_guess_number(message: Message):
    user_id = message.from_user.id
    if user_id not in game_states or game_states[user_id].get('game') != 'guess_number':
        return
    guess = int(message.text)
    game_states[user_id]['attempts'] += 1
    attempts = game_states[user_id]['attempts']
    target = game_states[user_id]['number']
    if guess < target:
        await message.answer(f"📈 Больше! Попыток: {attempts}")
    elif guess > target:
        await message.answer(f"📉 Меньше! Попыток: {attempts}")
    else:
        await message.answer(
            f"🎉 **Поздравляю!**\n\n"
            f"Ты угадал число {target} за {attempts} попыток!\n\n"
            f"Хочешь сыграть ещё? Нажми /games",
            parse_mode="Markdown"
        )
        del game_states[user_id]


@dp.callback_query(F.data == "game_rps")
async def start_rps(callback_query):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✊ Камень", callback_data="rps_stone"),
                InlineKeyboardButton(text="✌️ Ножницы", callback_data="rps_scissors"),
                InlineKeyboardButton(text="✋ Бумага", callback_data="rps_paper"),
            ],
        ]
    )
    await callback_query.message.answer(
        "✊ **Камень-Ножницы-Бумага!**\n\n"
        "Выбери:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback_query.answer()


@dp.callback_query(F.data.startswith("rps_"))
async def play_rps(callback_query):
    choices = {
        'rps_stone': ('✊ Камень', 'камень'),
        'rps_scissors': ('✌️ Ножницы', 'ножницы'),
        'rps_paper': ('✋ Бумага', 'бумага')
    }
    user_choice_name, user_choice = choices[callback_query.data]
    computer_choice = random.choice(['камень', 'ножницы', 'бумага'])
    if user_choice == computer_choice:
        result = "🤝 Ничья!"
        result_emoji = "🤝"
    elif (
            (user_choice == 'камень' and computer_choice == 'ножницы') or
            (user_choice == 'ножницы' and computer_choice == 'бумага') or
            (user_choice == 'бумага' and computer_choice == 'камень')
    ):
        result = "🎉 Ты победил!"
        result_emoji = "🏆"
    else:
        result = "😢 Ты проиграл!"
        result_emoji = "💔"
    computer_choice_name = {'камень': '✊ Камень', 'ножницы': '✌️ Ножницы', 'бумага': '✋ Бумага'}[computer_choice]
    await callback_query.message.answer(
        f"{result_emoji} {result}\n\n"
        f"Ты: {user_choice_name}\n"
        f"Компьютер: {computer_choice_name}\n\n"
        f"Сыграем ещё?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="game_rps")]
        ])
    )
    await callback_query.answer()


@dp.callback_query(F.data == "game_dice")
async def roll_dice(callback_query):
    dice_value = random.randint(1, 6)
    dice_emojis = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}
    await callback_query.message.answer(
        f"🎲 **Бросок кубика!**\n\n"
        f"{dice_emojis[dice_value]} Выпало: **{dice_value}**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="game_dice")]
        ]),
        parse_mode="Markdown"
    )
    await callback_query.answer()


QUIZ_QUESTIONS = [
    {
        'question': "Сколько планет в Солнечной системе?",
        'options': ['7', '8', '9', '10'],
        'correct': 1
    },
    {
        'question': "Какой язык программирования используется для бота?",
        'options': ['Java', 'C++', 'Python', 'JavaScript'],
        'correct': 2
    },
    {
        'question': "Сколько будет 2 + 2 × 2?",
        'options': ['6', '8', '4', '10'],
        'correct': 0
    },
    {
        'question': "Какой город столица России?",
        'options': ['Санкт-Петербург', 'Казань', 'Москва', 'Новосибирск'],
        'correct': 2
    },
]


@dp.callback_query(F.data == "game_quiz")
async def start_quiz(callback_query):
    question = random.choice(QUIZ_QUESTIONS)
    game_states[callback_query.from_user.id] = {
        'game': 'quiz',
        'question': question
    }
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=f"quiz_{i}") for i, opt in enumerate(question['options'])]
        ]
    )
    await callback_query.message.answer(
        f"🎯 **Викторина!**\n\n"
        f"{question['question']}\n\n"
        f"Выбери ответ:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback_query.answer()


@dp.callback_query(F.data.startswith("quiz_"))
async def answer_quiz(callback_query):
    user_id = callback_query.from_user.id
    if user_id not in game_states or game_states[user_id].get('game') != 'quiz':
        await callback_query.answer("Сначала начни викторину!")
        return
    question = game_states[user_id]['question']
    answer_index = int(callback_query.data.split('_')[1])
    if answer_index == question['correct']:
        result = "✅ Правильно!"
        result_emoji = "🎉"
    else:
        result = f"❌ Неправильно!\nПравильный ответ: {question['options'][question['correct']]}"
        result_emoji = "😢"
    await callback_query.message.answer(
        f"{result_emoji} {result}\n\n"
        f"Сыграть ещё?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Ещё вопрос", callback_data="game_quiz")]
        ])
    )
    del game_states[user_id]
    await callback_query.answer()


@dp.callback_query(F.data == "game_clicker")
async def start_clicker(callback_query):
    game_states[callback_query.from_user.id] = {
        'game': 'clicker',
        'score': 0,
        'start_time': datetime.now()
    }
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👆 КЛИКАЙ!", callback_data="clicker_click")],
        ]
    )
    await callback_query.message.answer(
        "👆 **Кликер!**\n\n"
        "Кликай по кнопке как можно быстрее!\n"
        "У тебя есть 10 секунд.\n\n"
        "Готов?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback_query.answer()


@dp.callback_query(F.data == "clicker_click")
async def clicker_click(callback_query):
    user_id = callback_query.from_user.id
    if user_id not in game_states or game_states[user_id].get('game') != 'clicker':
        await callback_query.answer("Сначала начни игру!")
        return
    game_states[user_id]['score'] += 1
    score = game_states[user_id]['score']
    elapsed = (datetime.now() - game_states[user_id]['start_time']).total_seconds()
    if elapsed >= 10:
        final_score = score
        del game_states[user_id]
        await callback_query.message.answer(
            f"⏱ **Время вышло!**\n\n"
            f"Твой результат: **{final_score}** кликов за 10 секунд!\n\n"
            f"{'🏆 Отлично!' if final_score > 30 else '👍 Неплохо!' if final_score > 20 else '💪 Попробуй ещё!'}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="game_clicker")]
            ]),
            parse_mode="Markdown"
        )
    else:
        remaining = 10 - int(elapsed)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"👆 КЛИКАЙ! ({score})", callback_data="clicker_click")],
            ]
        )
        await callback_query.message.edit_text(
            f"👆 **Кликер!**\n\n"
            f"Кликов: {score}\n"
            f"Осталось времени: {remaining} сек.\n\n"
            f"Кликай быстрее!",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    await callback_query.answer()


# ============================================
#  ОСНОВНЫЕ ОБРАБОТЧИКИ
# ============================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "👋 Привет! Я бот с ИИ-зрением!\n\n"
        "Могу:\n"
        "• 🎬 Оживлять людей на фото (двигать руки, ноги, голову!)\n"
        "• 🎨 Редактировать фото (эффекты, фильтры)\n"
        "• 🎮 Играть в игры\n"
        "• 🐾 Оживлять животных\n"
        "• 🌤 Показывать погоду\n"
        "• 🎵 Искать музыку\n"
        "• 💰 Показывать курсы валют\n\n"
        "Выберите действие:"
    )
    await message.answer(welcome_text, reply_markup=main_menu)


@dp.message(Command('help'))
async def cmd_help_command(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🤖 *Возможности бота:*\n\n"
        "🖼 *Оживление фото* — ИИ находит человека и:\n"
        "  • Двигает голову, руки, ноги\n"
        "  • Создаёт GIF-анимацию\n\n"
        "🎨 *Редактирование фото* — 10+ эффектов:\n"
        "  • Ч/Б, сепия, размытие\n"
        "  • Резкость, контраст, яркость\n"
        "  • Инверсия, эскиз и другие\n\n"
        "🎮 *Игры* — 5 игр:\n"
        "  • Угадай число\n"
        "  • Камень-Ножницы-Бумага\n"
        "  • Кубик, Викторина, Кликер\n\n"
        "🌤 Погода — прогноз для любого города\n"
        "🎵 Музыка — поиск на YouTube/VK/Яндекс\n"
        "💰 Финансы — курсы криптовалют\n"
        "💵 Курс Доллара — актуальные курсы ЦБ РФ"
    )
    await message.answer(help_text, parse_mode="Markdown")


@dp.message(F.text == "ℹ Помощь")
async def cmd_help_button(message: Message):
    """Обработчик кнопки Помощь"""
    help_text = (
        "🤖 *Возможности бота:*\n\n"
        "🖼 *Оживление фото* — ИИ находит человека и:\n"
        "  • Двигает голову, руки, ноги\n"
        "  • Создаёт GIF-анимацию\n\n"
        "🎨 *Редактирование фото* — 10+ эффектов:\n"
        "  • Ч/Б, сепия, размытие\n"
        "  • Резкость, контраст, яркость\n"
        "  • Инверсия, эскиз и другие\n\n"
        "🎮 *Игры* — 5 игр:\n"
        "  • Угадай число\n"
        "  • Камень-Ножницы-Бумага\n"
        "  • Кубик, Викторина, Кликер\n\n"
        "🌤 Погода — прогноз для любого города\n"
        "🎵 Музыка — поиск на YouTube/VK/Яндекс\n"
        "💰 Финансы — курсы криптовалют\n"
        "💵 Курс Доллара — актуальные курсы ЦБ РФ"
    )
    await message.answer(help_text, parse_mode="Markdown")


@dp.message(F.text == "👋 О боте")
async def about_bot(message: Message):
    about_text = (
        "🤖 Я — умный бот с компьютерным зрением!\n\n"
        "Использую технологию *MediaPipe Pose* от Google, "
        "чтобы находить 33 ключевые точки тела человека на фото.\n\n"
        "Затем я разделяю изображение на части (голова, руки, ноги, торс) "
        "и анимирую каждую часть независимо!\n\n"
        "Также я умею:\n"
        "• 🎨 Редактировать фото (10+ эффектов)\n"
        "• 🎮 Играть в игры (5 игр)\n"
        "• 🌤 Показывать погоду\n"
        "• 🎵 Искать музыку\n"
        "• 💰 Показывать курсы валют\n\n"
        "Это создаёт эффект «оживления» фотографии. 🎬"
    )
    await message.answer(about_text, parse_mode="Markdown")


@dp.message(F.text == "🌤 Погода")
async def weather_request(message: Message):
    user_states[message.from_user.id] = 'weather_mode'
    await message.answer("Введите название города. Пример: 'погода Москва'")


@dp.message(F.text == "🎵 Музыка")
async def music_request(message: Message):
    user_states[message.from_user.id] = 'music_mode'
    await message.answer("Введите название песни или исполнителя.\nПример: 'музыка Queen'")


@dp.message(F.text == "💰 Финансы")
async def finance_request(message: Message):
    await message.answer("⏳ Загрузка курсов криптовалют...")
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,solana&vs_currencies=rub,usd&include_24hr_change=true"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            crypto_text = "💰 *Актуальные курсы криптовалют:*\n\n"
            coins = {
                'bitcoin': ('₿ Bitcoin', 'BTC'),
                'ethereum': ('Ξ Ethereum', 'ETH'),
                'binancecoin': ('BNB', 'BNB'),
                'cardano': ('₳ Cardano', 'ADA'),
                'solana': ('◎ Solana', 'SOL')
            }
            for coin_id, (name, symbol) in coins.items():
                if coin_id in data:
                    rub_price = data[coin_id].get('rub', 0)
                    usd_price = data[coin_id].get('usd', 0)
                    change = data[coin_id].get('usd_24h_change', 0)
                    change_icon = "📈" if change > 0 else "📉"
                    crypto_text += (
                        f"*{name}* ({symbol})\n"
                        f"  💵 {rub_price:,.0f} ₽ / ${usd_price:,.2f}\n"
                        f"  {change_icon} За 24ч: {change:.2f}%\n\n"
                    )
            crypto_text += f"_Данные обновлены: {datetime.now().strftime('%H:%M:%S')}_"
            image = _generate_crypto_image(data, coins)
            bio = io.BytesIO()
            image.save(bio, format='PNG')
            photo_file = bytesio_to_buffered(bio, "crypto.png")
            await message.answer_photo(photo=photo_file, caption=crypto_text, parse_mode="Markdown")
        else:
            await message.answer(f"Ошибка (код {response.status_code}).")
    except Exception as e:
        logging.error(f"Ошибка крипто: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


def _generate_crypto_image(data, coins):
    width, height = 700, 500
    image = Image.new('RGB', (width, height), (20, 20, 40))
    draw = ImageDraw.Draw(image)
    try:
        font_title = ImageFont.truetype(FONT_PATH, 28)
        font_text = ImageFont.truetype(FONT_PATH, 18)
    except IOError:
        font_title = font_text = ImageFont.load_default()
    draw.text((20, 20), "КУРСЫ КРИПТОВАЛЮТ", fill=(0, 255, 255), font=font_title)
    y = 70
    for coin_id, (name, symbol) in coins.items():
        if coin_id in data:
            rub_price = data[coin_id].get('rub', 0)
            change = data[coin_id].get('usd_24h_change', 0)
            color = (0, 255, 0) if change > 0 else (255, 100, 100)
            draw.text((20, y), f"{name}: {rub_price:,.0f} RUB", fill=color, font=font_text)
            y += 30
    return image


@dp.message(F.text == "💵 Курс Доллара")
async def dollar_rate(message: Message):
    """ИСПРАВЛЕНО: Теперь работает корректно"""
    await message.answer("⏳ Загрузка курса валют...")
    try:
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            usd_rate = data['Valute']['USD']['Value']
            eur_rate = data['Valute']['EUR']['Value']
            date = data['Date']

            # Создаём текстовое сообщение
            caption = (
                f"💵 *Актуальный курс валют ЦБ РФ*\n\n"
                f"🇺🇸 Доллар США (USD): *{usd_rate:.2f} ₽*\n"
                f"🇪🇺 Евро (EUR): *{eur_rate:.2f} ₽*\n\n"
                f"_Дата: {date[:10]}_"
            )

            # Создаём и отправляем картинку
            image = _generate_exchange_image(usd_rate, eur_rate, date)
            bio = io.BytesIO()
            image.save(bio, format='PNG')
            bio.seek(0)
            photo_file = bytesio_to_buffered(bio, "exchange.png")
            await message.answer_photo(photo=photo_file, caption=caption, parse_mode="Markdown")
        else:
            await message.answer(f"❌ Не удалось получить курс валют (код {response.status_code}).")
    except Exception as e:
        logging.error(f"Ошибка курса: {e}")
        await message.answer(f"❌ Произошла ошибка: {e}. Попробуйте позже.")


def _generate_exchange_image(usd_rate, eur_rate, date):
    width, height = 600, 400
    image = Image.new('RGB', (width, height), (30, 100, 30))
    draw = ImageDraw.Draw(image)
    try:
        font_large = ImageFont.truetype(FONT_PATH, 40)
        font_medium = ImageFont.truetype(FONT_PATH, 28)
        font_small = ImageFont.truetype(FONT_PATH, 20)
    except IOError:
        font_large = font_medium = font_small = ImageFont.load_default()
    draw.text((150, 40), "КУРС ВАЛЮТ", fill=(255, 255, 255), font=font_large)
    draw.text((50, 130), f"USD: {usd_rate:.2f} RUB", fill=(255, 255, 100), font=font_medium)
    draw.text((50, 200), f"EUR: {eur_rate:.2f} RUB", fill=(255, 255, 100), font=font_medium)
    draw.text((50, 300), f"Дата: {date[:10]}", fill=(200, 200, 200), font=font_small)
    return image


# ============================================
# ПОГОДА И МУЗЫКА
# ============================================

@dp.message(F.text.contains("погода") | F.text.contains("Погода"))
async def handle_weather_request(message: Message):
    city = message.text.replace("погода", "").replace("Погода", "").strip()
    if not city:
        await message.answer("Укажите город. Пример: 'погода Москва'")
        return
    if not WEATHER_API_KEY:
        await message.answer("Сервис погоды недоступен.")
        return
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric", "lang": "ru"}
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            weather_info = data.get('weather', [{}])[0]
            main_info = data.get('main', {})
            weather_desc = str(weather_info.get('description', 'Нет данных'))
            temp = str(main_info.get('temp', 'Нет данных'))
            feels_like = str(main_info.get('feels_like', 'Нет данных'))
            humidity = str(main_info.get('humidity', 'Нет данных'))
            declined_city = decline_city_prepositional(city)
            image = _generate_weather_image(declined_city, weather_desc, temp, feels_like, humidity)
            bio = io.BytesIO()
            image.save(bio, format='PNG')
            photo_file = bytesio_to_buffered(bio, "weather.png")
            await message.answer_photo(photo=photo_file)
        elif response.status_code == 404:
            await message.answer("❌ Город не найден.")
        else:
            await message.answer(f"❌ Ошибка (код {response.status_code})")
    except Exception as e:
        logging.error(f"Ошибка погоды: {e}")
        await message.answer("Ошибка при получении погоды.")


def _generate_weather_image(city, description, temp, feels_like, humidity):
    width, height = 600, 400
    image = Image.new('RGB', (width, height), (45, 175, 230))
    draw = ImageDraw.Draw(image)
    try:
        font_large = ImageFont.truetype(FONT_PATH, 36)
        font_medium = ImageFont.truetype(FONT_PATH, 24)
    except IOError:
        font_large = font_medium = ImageFont.load_default()
    draw.text((50, 30), f"Погода в {city}", fill=(255, 255, 255), font=font_large)
    weather_data = [
        f"Описание: {description.capitalize()}",
        f"Температура: {temp}°C",
        f"Ощущается как: {feels_like}°C",
        f"Влажность: {humidity}%"
    ]
    y = 100
    for line in weather_data:
        draw.text((50, y), line, fill=(255, 255, 255), font=font_medium)
        y += 40
    return image


@dp.message(F.text.contains("музыка") | F.text.contains("Музыка"))
async def handle_music_request(message: Message):
    query = message.text.replace("музыка", "").replace("Музыка", "").strip()
    if not query:
        await message.answer("Укажите песню или исполнителя.")
        return
    try:
        encoded = urllib.parse.quote(query)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎵 YouTube", url=f"https://www.youtube.com/results?search_query={encoded}")],
                [InlineKeyboardButton(text="🎧 VK", url=f"https://vk.com/audio?q={encoded}")],
                [InlineKeyboardButton(text="🎼 Яндекс", url=f"https://music.yandex.ru/search?text={encoded}")],
                [InlineKeyboardButton(text="▶️ Spotify", url=f"https://open.spotify.com/search/{encoded}")],
            ]
        )
        await message.answer(
            f"🎵 *Результаты поиска: {query}*",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Ошибка музыки: {e}")
        await message.answer("Ошибка при поиске музыки.")


@dp.message()
async def handle_phrases(message: Message):
    text = message.text.lower().strip()
    for phrases, response in PHRASES_MAP.items():
        if any(phrase in text for phrase in phrases):
            await message.answer(response)
            return
    await message.answer("Не понял вопрос. Используйте кнопки меню!")


async def main():
    print("🤖 Бот запущен! Все функции работают!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())