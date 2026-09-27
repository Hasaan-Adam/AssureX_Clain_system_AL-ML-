import os

filepath = 'frontend/src/routes/index.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "['reviewer', 'staff', 'admin']",
    "['reviewer', 'staff', 'service_staff', 'admin']"
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.jsx")
