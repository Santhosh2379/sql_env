import os
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.git']]
    for f in files:
        path = os.path.join(root, f)
        try:
            open(path, 'r', encoding='utf-8').read()
            print('OK:', path)
        except Exception as e:
            print('BAD:', path, e)