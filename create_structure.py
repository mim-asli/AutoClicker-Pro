import os

dirs = ["utils", "core", "ui"]
for d in dirs:
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("# Module initialization\n")

print("✅ تمام پوشه‌ها با موفقیت ساخته شدند!")