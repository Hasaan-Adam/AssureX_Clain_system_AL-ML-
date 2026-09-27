import os

filepath = 'src/api/v1/claims.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'from src.dependencies import get_current_user, require_role',
    'from src.dependencies import get_current_user, require_reviewer'
)
content = content.replace(
    'current_user: User = Depends(require_role(RoleEnum.REVIEWER))',
    'current_user: User = Depends(require_reviewer)'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated claims.py")
