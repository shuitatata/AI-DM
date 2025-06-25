import pytest
from pathlib import Path
from app.core.template_manager import PromptManager


@pytest.fixture
def template_dir(tmp_path: Path) -> Path:
    """
    创建一个 pytest fixture，用于生成一个临时的、包含测试模板的目录结构。
    这样可以确保测试的独立性和可重复性。
    """
    agents_dir = tmp_path / "agents"

    # 创建一个中文模板
    zh_dir = agents_dir
    zh_dir.mkdir(parents=True, exist_ok=True)
    (zh_dir / "world_form.txt").write_text("世界设定: {{ setting }}")

    # 创建一个英文模板
    en_dir = agents_dir / "en"
    en_dir.mkdir(exist_ok=True)
    (en_dir / "world_form.txt").write_text("World Setting: {{ setting }}")

    # 创建一个内容为空的模板用于边界测试
    (zh_dir / "empty_template.txt").write_text("   ")

    return tmp_path


class TestPromptManager:
    """
    为 PromptManager 类编写的单元测试套件。
    """

    def test_initialization_and_loading(self, template_dir: Path):
        """
        测试：PromptManager 初始化时是否能成功加载指定目录的模板。
        """
        manager = PromptManager(base_directory=template_dir)

        assert "world_form" in manager.templates
        assert "empty_template" in manager.templates

        assert "zh" in manager.templates["world_form"]
        assert "en" in manager.templates["world_form"]

        assert manager.templates["world_form"]["zh"] == "世界设定: {{ setting }}"
        assert manager.templates["world_form"]["en"] == "World Setting: {{ setting }}"
        assert manager.templates["empty_template"]["zh"] == "   "

    def test_get_existing_template(self, template_dir: Path):
        """
        测试：get_template 是否能正确获取一个存在的模板。
        """
        manager = PromptManager(base_directory=template_dir)

        zh_template = manager.get_template("world_form", "zh")
        assert zh_template == "世界设定: {{ setting }}"

        en_template = manager.get_template("world_form", "en")
        assert en_template == "World Setting: {{ setting }}"

    def test_get_non_existent_template(self, template_dir: Path):
        """
        测试：get_template 在模板不存在时是否返回 None。
        """
        manager = PromptManager(base_directory=template_dir)

        assert manager.get_template("non_existent_template", "zh") is None

    def test_render_template_successfully(self, template_dir: Path):
        """
        测试：render_template 是否能成功渲染模板并注入变量。
        """
        manager = PromptManager(base_directory=template_dir)

        rendered_zh = manager.render_template("world_form", "zh", setting="测试世界")
        assert rendered_zh == "世界设定: 测试世界"

        rendered_en = manager.render_template("world_form", "en", setting="Test World")
        assert rendered_en == "World Setting: Test World"

    def test_render_non_existent_template_raises_error(self, template_dir: Path):
        """
        测试：尝试渲染不存在的模板时，是否会按预期抛出 ValueError。
        """
        manager = PromptManager(base_directory=template_dir)
        with pytest.raises(ValueError):
            manager.render_template("non_existent_template", "zh", setting="Test")

    def test_validate_template(self, template_dir: Path):
        """
        测试：validate_template 对有效、无效和空模板的判断是否正确。
        """
        manager = PromptManager(base_directory=template_dir)

        assert manager.validate_template("world_form", "zh")
        assert manager.validate_template("world_form", "en")

        assert not manager.validate_template("non_existent_template", "zh")
        assert not manager.validate_template("non_existent_template", "en")

        assert not manager.validate_template("empty_template", "zh")
