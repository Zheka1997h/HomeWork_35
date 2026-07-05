# -*- coding: utf-8 -*-
import sys

print(f"Python version: {sys.version}")
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"Stdout encoding: {sys.stdout.encoding}")
print(f"Filesystem encoding: {sys.getfilesystemencoding()}")

# Проверяем эмодзи
print("Тест эмодзи: 🏦 ✅ ❌ 🔎 💳")

# Проверяем запись в файл
with open("test.log", "w", encoding="utf-8") as f:
    f.write("Тест кириллицы и эмодзи: 🏦 ✅ ❌\n")

print("✅ Файл test.log создан")