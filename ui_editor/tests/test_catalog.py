"""布局目录：代际判读与包内缺失名单（纯逻辑，无 Qt）。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.catalog import (  # noqa: E402
    GENERATION_CURRENT,
    GENERATION_LEGACY,
    GENERATION_TRANSITIONAL,
    generation_of,
    known_layout_paths,
)


class TestGenerationOf(unittest.TestCase):
    def test_current_generations(self):
        for path in (
            "dialog4/activity/2021spring/hongbao_main.dlg",
            "dialog4/acctransfer/acctransfer.dlg",
            "login_new/newlogin_800.dlg",
            "dialog/group_new/group_info/group_register.dlg",
            "dialog/new_player_present/signin/signin_main_new.dlg",
            "dialog/nationfight/newnationfight/monsterskillset.dlg",
            "dialog/sysopt_new.dlg",
        ):
            self.assertEqual(generation_of(path), GENERATION_CURRENT, path)

    def test_transitional_and_legacy(self):
        self.assertEqual(
            generation_of("dialog3/activity/mx2018cj/cjend.dlg"),
            GENERATION_TRANSITIONAL)
        for path in (
            "dialog/equip/equip.dlg",
            "dialog/petcombine.dlg",
            "dialog2/signin/signin.dlg",
            "login/service.dlg",
            "avatar.dlg",
        ):
            self.assertEqual(generation_of(path), GENERATION_LEGACY, path)

    def test_catalog_paths_all_classified(self):
        for path in known_layout_paths():
            self.assertIn(generation_of(path), {
                GENERATION_CURRENT, GENERATION_TRANSITIONAL,
                GENERATION_LEGACY}, path)


if __name__ == "__main__":
    unittest.main()
