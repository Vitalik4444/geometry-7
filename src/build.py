# -*- coding: utf-8 -*-
# Сборка index.html: генерирует банки вопросов и задач и подставляет их в шаблон.
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
data, tasks = os.path.join(here, 'data.json'), os.path.join(here, 'tasks.json')
subprocess.run([sys.executable, os.path.join(here, 'gen.py'), data], check=True)
subprocess.run([sys.executable, os.path.join(here, 'tasks_fig.py'), tasks], check=True)
s = open(os.path.join(here, 'template.html'), encoding='utf-8').read()
s = s.replace('/*DATA*/', open(data, encoding='utf-8').read()).replace('/*TASKS*/', open(tasks, encoding='utf-8').read())
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(s)
print('index.html', len(s))
