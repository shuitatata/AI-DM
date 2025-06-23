"""Template Manager - 模板化Prompt管理系统"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template


class PromptManager:
    """Prompt模板管理器 - 从文件系统加载和管理模板"""

    def __init__(self, base_directory: str = "backend/templates"):
        self.base_directory = Path(base_directory)
        self.templates: Dict[str, Dict[str, str]] = {}
        self._load_templates()

    def _load_templates(self):
        """从文件系统加载所有Prompt模板"""
        agents_dir = self.base_directory / "agents"

        # 如果目录不存在，创建空目录
        if not agents_dir.exists():
            agents_dir.mkdir(parents=True, exist_ok=True)
            return

        # 扫描所有模板文件
        for template_file in agents_dir.glob("**/*.txt"):
            category = template_file.stem
            # 从文件路径推断语言（如果有子目录）
            language = "zh"  # 默认中文
            if template_file.parent.name != "agents":
                language = template_file.parent.name

            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    content = f.read()

                if category not in self.templates:
                    self.templates[category] = {}
                self.templates[category][language] = content

            except Exception as e:
                print(f"加载模板文件 {template_file} 失败: {e}")

    def get_template(self, category: str, language: str = "zh") -> Optional[str]:
        """获取指定分类和语言的模板"""
        return self.templates.get(category, {}).get(language)

    def render_template(self, category: str, language: str = "zh", **kwargs) -> str:
        """渲染模板，支持变量注入"""
        template_content = self.get_template(category, language)
        if not template_content:
            raise ValueError(f"模板不存在: {category}/{language}")

        template = Template(template_content)
        return template.render(**kwargs)

    def get_available_templates(self) -> List[str]:
        """获取所有可用的模板类别"""
        return list(self.templates.keys())

    def validate_template(self, category: str, language: str = "zh") -> bool:
        """验证模板是否存在且有效"""
        template_content = self.get_template(category, language)
        return template_content is not None and len(template_content.strip()) > 0

    def reload_templates(self):
        """重新加载所有模板"""
        self.templates.clear()
        self._load_templates()
