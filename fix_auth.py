import os

filepath = 'frontend/src/context/AuthContext.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'const isStaff = role === ROLES.STAFF || isReviewer || isAdmin;',
    "const isStaff = role === ROLES.STAFF || role === 'service_staff' || isReviewer || isAdmin;"
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated AuthContext.jsx")
