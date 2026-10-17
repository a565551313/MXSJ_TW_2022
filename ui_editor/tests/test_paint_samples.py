"""绘制样样例与对照清单的机检（Qt，offscreen）。

能机检的只有「不崩、尺寸对、清单和代码一致」——外观是否与游戏一致**必须**
人工看真机截图（`ui_editor/docs/PAINT_CHECKLIST.md` 的规矩）。所以这里既钉
住渲染冒烟，也钉住清单不会漏类型：新增控件类型后忘了更新清单，会在这里红。
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import defaults_data, painters  # noqa: E402
from ui_editor.core.assets import AssetResolver  # noqa: E402
from ui_editor.core.pack import FlsPack  # noqa: E402
from ui_editor.core.sprite import MAGICS  # noqa: E402
from ui_editor.ui import paint_samples  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PACK = REPO_ROOT / "data" / "skill.fls"


def checklist_types() -> list[str]:
    """从对照清单 Markdown 里读出类型列（``| 1 | `CButton` | ...``）。"""
    text = paint_samples.CHECKLIST_PATH.read_text(encoding="utf-8")
    types: list[str] = []
    for line in text.splitlines():
        if not line.startswith("|") or "`" not in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or not cells[0].isdigit():
            continue
        types.append(cells[1].strip("`"))
    return types


def checklist_painters() -> dict[str, str]:
    text = paint_samples.CHECKLIST_PATH.read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("|") or "`" not in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4 or not cells[0].isdigit():
            continue
        mapping[cells[1].strip("`")] = cells[2].strip("`")
    return mapping


class SampleSpecTests(unittest.TestCase):
    def test_specs_cover_every_default_template_type(self):
        specs = paint_samples.sample_specs()
        self.assertEqual([spec.wtype for spec in specs],
                         sorted(defaults_data.DEFAULT_PROPS))
        self.assertEqual(len(specs), 38)

    def test_image_fields_get_a_placeholder_path(self):
        for spec in paint_samples.sample_specs():
            expected = tuple(name for name in paint_samples.IMAGE_FIELDS
                             if name in spec.props)
            self.assertEqual(spec.image_fields, expected)
            for name in expected:
                self.assertEqual(spec.props[name], paint_samples.SAMPLE_IMAGE)

    def test_data_widget_has_no_dedicated_painter(self):
        # 38 类模板 vs 37 类登记：唯一缺登记的就是它——清单里要看得见
        self.assertEqual(paint_samples.painter_name("CDataWidget"),
                         "_paint_fallback")
        self.assertNotIn("CDataWidget", painters._PAINTERS)


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    def ctx(self) -> painters.PaintContext:
        return painters.PaintContext(assets=AssetResolver())

    def test_every_type_renders_a_non_empty_image(self):
        ctx = self.ctx()
        for spec in paint_samples.sample_specs():
            with self.subTest(wtype=spec.wtype):
                image = paint_samples.render_sample(spec, ctx)
                self.assertFalse(image.isNull())
                self.assertGreater(image.width(), 0)
                self.assertGreater(image.height(), 0)
                # 尺寸应当与画布用的 effective_size 一致
                from ui_editor.core.model import Widget

                self.assertEqual(
                    (image.width(), image.height()),
                    tuple(max(1, int(v)) for v in painters.effective_size(
                        Widget(spec.props), ctx)))

    def test_contact_sheet_contains_all_samples(self):
        ctx = self.ctx()
        images = [(spec.wtype, paint_samples.render_sample(spec, ctx))
                  for spec in paint_samples.sample_specs()]
        sheet = paint_samples.contact_sheet(images)
        self.assertGreater(sheet.width(), max(img.width() for _t, img in images))
        self.assertGreater(sheet.height(), 0)


class WriteSamplesTests(unittest.TestCase):
    def setUp(self):
        from PySide6.QtWidgets import QApplication

        QApplication.instance() or QApplication([])
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "samples"

    def test_manifest_matches_written_files(self):
        manifest = paint_samples.write_samples(self.out)
        self.assertEqual(len(manifest["items"]), 38)
        self.assertFalse(manifest["real_resources"])
        self.assertFalse(manifest["image_found"])
        self.assertIn("--image", manifest["note"])
        self.assertTrue((self.out / "manifest.json").is_file())
        sheet = manifest["contact_sheet"]
        self.assertTrue((self.out / sheet["file"]).is_file())
        for item in manifest["items"]:
            path = self.out / item["file"]
            self.assertTrue(path.is_file(), item["file"])
            import hashlib

            self.assertEqual(item["sha256"],
                             hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(item["painter"],
                             paint_samples.painter_name(item["wtype"]))

    def test_image_fields_are_faked_only_where_the_template_has_them(self):
        manifest = paint_samples.write_samples(self.out, contact=False)
        faked = {item["wtype"]: item["image_fields_faked"]
                 for item in manifest["items"]}
        # 20 类模板带 sFileName/sBgFileName/sBarFileName（如 CProgress 用
        # sBgFileName/sBarFileName），
        # 其余类型不该被硬塞图片字段——否则清单会误导「这类控件吃图」
        self.assertEqual(sum(1 for names in faked.values() if names), 20)
        # manifest 走 JSON：元组会变成列表，比较时统一成列表
        self.assertEqual(faked["CFrame"], ["sFileName"])
        self.assertEqual(faked["CMainFrame"], [])
        self.assertEqual(faked["CEdit"], [])


class RealResourceSampleTests(unittest.TestCase):
    """真实资源模式：图片字段指向仓库里唯一一份真实精灵时必须真的解码。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])
        if not SKILL_PACK.is_file():
            raise unittest.SkipTest(f"缺少真实资源包：{SKILL_PACK}")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.assets = self.root / "assets"
        (self.assets / "images").mkdir(parents=True)
        self.image_path = "images/paint_sample.png"
        with FlsPack(SKILL_PACK) as pack:
            sprite_bytes = None
            for entry_id in pack.entry_ids:
                data = pack.read_id(entry_id)
                if data and data[:2] in MAGICS:
                    sprite_bytes = data
                    break
        if sprite_bytes is None:
            raise unittest.SkipTest(f"{SKILL_PACK} 里没有精灵条目")
        (self.assets / self.image_path).write_bytes(sprite_bytes)

    def test_real_image_is_used_and_changes_image_types_only(self):
        placeholder = paint_samples.write_samples(
            self.root / "placeholder", contact=False)
        real = paint_samples.write_samples(
            self.root / "real", assets_dir=self.assets,
            image_path=self.image_path, contact=False)
        self.assertFalse(placeholder["image_found"])
        self.assertTrue(real["image_found"])
        self.assertTrue(real["real_resources"])
        self.assertEqual(real["image_path"], self.image_path)

        changed = {a["wtype"] for a, b in zip(placeholder["items"],
                                             real["items"], strict=True)
                   if a["sha256"] != b["sha256"]}
        with_image = {item["wtype"] for item in real["items"]
                      if item["image_fields_faked"]}
        # 真实资源只应影响「模板里有图片字段」的类型，且确实影响了它们
        self.assertEqual(changed, with_image)
        self.assertEqual(len(changed), 20)
        for item in real["items"]:
            if item["wtype"] not in with_image:
                self.assertEqual(
                    next(p for p in placeholder["items"]
                         if p["wtype"] == item["wtype"])["sha256"],
                    item["sha256"], item["wtype"])


class ChecklistTests(unittest.TestCase):
    """清单是给人工核对的表：类型与绘制函数必须与代码同步。"""

    def test_checklist_covers_exactly_the_template_types(self):
        self.assertEqual(sorted(checklist_types()),
                         sorted(defaults_data.DEFAULT_PROPS))

    def test_checklist_painter_column_matches_dispatch_table(self):
        mapping = checklist_painters()
        for wtype, painter in mapping.items():
            with self.subTest(wtype=wtype):
                self.assertEqual(painter, paint_samples.painter_name(wtype))

    def test_game_side_columns_are_empty_until_checked(self):
        """未做真机核对的格子必须留空——这条是规矩，不是建议。"""
        text = paint_samples.CHECKLIST_PATH.read_text(encoding="utf-8")
        filled = 0
        for line in text.splitlines():
            if not line.startswith("|") or "`" not in line:
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 9 or not cells[0].isdigit():
                continue
            if any(cells[index] for index in (5, 6, 7, 8)):
                filled += 1
        self.assertEqual(filled, 0,
                         "清单里出现了已填的游戏侧结论；要么附真机证据，"
                         "要么留空")

    def test_regeneration_is_stable(self):
        """清单由代码生成：重新生成必须与仓库里那份逐字一致。"""
        self.assertEqual(paint_samples.render_checklist_markdown(),
                         paint_samples.CHECKLIST_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
