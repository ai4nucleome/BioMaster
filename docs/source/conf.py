# docs/source/conf.py

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))  # 将项目根目录加入路径

project = 'BioMaster'
author = 'Su Houcheng et al.'
release = '0.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo'
]

# 使用 Read the Docs 主题
html_theme = 'sphinx_rtd_theme'

# 设置模板路径（如果你使用自定义模板）
templates_path = ['_templates']

# 设置不包含的文件和目录
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# 静态文件（如 logo 或 css）路径
html_static_path = ['_static']

# TODO 显示设置
todo_include_todos = True
