"""v3 structure and authored-UI model checks; not Windows resource acceptance."""
import contextlib
import io
import json
from pathlib import Path
import struct
import sys
import types
import unittest
from unittest.mock import patch as mock_patch
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_visual_preview as visual
base = visual.base


class Node:
    def __init__(self, parent=None, msgid=None, pos=(0, 0), size=(100, 28)):
        self.parent = parent
        self.m_MsgID = msgid
        self.pos = pos
        self.size = size
        self.shown = True
        self.text = 'old caption'
    def GetSize(self): return self.size
    def GetPos(self): return self.pos
    def SetPos(self, x, y): self.pos = (x, y)
    def SetShow(self, value): self.shown = value
    def Topmost(self): pass
    def SetText(self, text): self.text = text
    def SetLimit(self, value): self.limit = value
    def SetNextEdit(self, value): self.next_edit = value
    def Active(self, flag): self.active = flag


class Panel(Node):
    def __init__(self, parent, resource):
        Node.__init__(self, parent)
        self.resource = resource
        self.m_Frames = {'back': Node(self, 1), 'next': Node(self, 2)}
        if resource == 'login/service.dlg':
            self.m_Frames['loc_msg'] = Node(self, size=(520, 290), pos=(140, 140))
        elif resource == 'login_new/newlogin_800.dlg':
            for name, msg in [('close', 3), ('website', 10), ('forgot', 23), ('music', 71)]:
                self.m_Frames[name] = Node(self, msg)
            for name in ('edt_Name', 'edt_Pwd', 'chk_protect', 'chk_agree', 'box_URL', 'btn_Protect', 'btn_Music'):
                self.m_Frames[name] = Node(self)
        else:
            raise AssertionError('unexpected resource')
    def GetObject(self, name): return self.m_Frames.get(name)


class Edit(Node):
    def __init__(self, parent, color, font, x, y, w, h):
        Node.__init__(self, parent, pos=(x, y), size=(w, h))


class ClickBox(Node):
    def __init__(self, parent, w, h, x, y, msgid):
        Node.__init__(self, parent, msgid, (x, y), (w, h))


class Picture(Node):
    def __init__(self, parent, path, directory):
        Node.__init__(self, parent)
        self.path = path
        self.directory = directory


class Output(Node):
    def __init__(self, parent, w, h, x, y, lines, **kwargs):
        Node.__init__(self, parent, pos=(x, y), size=(w, h))
        self.lines = lines
    def SetChatCursor(self, value): pass
    def ResetFromCursor(self): pass
    def ScrollTo(self, value): self.cursor = value


class ValidatedForm(Panel):
    def DoNext(self, validate): self.validation_flag = validate
    def OnMessage(self, msgid):
        if msgid in (2, 3): self.DoNext(msgid == 2)


class VisualPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (base.ROOT / 'data/script.fls').read_bytes()
        cls.keys = (base.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
        cls.output, cls.report = visual.build(cls.source, cls.keys)
        # Only authored source is modeled. No recovered game module is executed.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            from lib2to3.refactor import RefactoringTool
            source = (visual.HERE / 'registration_visual_overlay.py').read_text()
            cls.modeled_source = str(RefactoringTool(['lib2to3.fixes.fix_print']).refactor_string(source, 'authored-v3'))

    def environment(self):
        events = []
        namespace = {'CRegPanel2': ValidatedForm, 'CRegEdit': Edit, 'CMailEdit': Edit,
                     'combdialog': types.SimpleNamespace(CCombPanel=Panel),
                     'interface': types.SimpleNamespace(FontLT14_3=14, COLOR_1=1, CClickBox=ClickBox),
                     'ui': types.SimpleNamespace(CImage=Picture),
                     'Step': lambda n: events.append(('step', n)),
                     'Show': lambda flag: events.append(('show', flag))}
        modules = {'chatoutput': types.SimpleNamespace(COutput=Output),
                   'mainpage': types.SimpleNamespace(Show=lambda flag: events.append(('home', flag)))}
        # loginin/net/HTTP APIs are intentionally NOT provided to this model.
        exec(compile(self.modeled_source, 'authored-v3-model', 'exec'), namespace)
        return namespace, modules, events

    def test_deterministic_same_size_payloads_and_scope(self):
        self.assertEqual(visual.build(self.source, self.keys), (self.output, self.report))
        original = base.entries(self.source)[1]
        after = base.entries(self.output)[1]
        self.assertEqual([i for i,(a,b) in enumerate(zip(original,after)) if a != b], [337,4007])
        for idx in (337,4007):
            self.assertEqual(len(base.zlib.decompress(original[idx][1])), len(base.zlib.decompress(after[idx][1])))
        self.assertEqual(self.output[12:len(self.source)], self.source[12:])

    def test_login_module_is_byte_identical_and_native_not_claimed(self):
        self.assertEqual(base.entries(self.source)[1][4806], base.entries(self.output)[1][4806])
        self.assertFalse(self.report['native_windows_client_tested'])
        self.assertGreater(self.report['details']['register']['padding_bytes'], 0)

    def test_source_manifest_and_png_sizes(self):
        _, manifest = visual.load_overlay()
        for name, size in {'form_card.png':(400,300), 'terms_title.png':(240,34), 'home_register.png':(80,24)}.items():
            data = (visual.HERE / 'visual_assets' / name).read_bytes()
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II', data[16:24]), size)
            self.assertEqual(base.sha(data), manifest['assets'][name])

    def test_home_caption_uses_registration_message_not_anonymous_name(self):
        namespace, _, _ = self.environment()
        home = Panel(None, 'login_new/newlogin_800.dlg')
        before = home.m_Frames['next'].size
        with contextlib.redirect_stdout(io.StringIO()): namespace['GetData'](home)
        self.assertEqual(home.m_Frames['next'].text, '')
        self.assertEqual(home.m_Frames['next'].size, before)
        self.assertEqual(home.m_Frames['next'].m_PreviewCaption.path, 'registration_preview_v3/home_register.png')
        self.assertEqual(home.m_Frames['back'].text, 'old caption')

    def test_ambiguous_home_button_is_logged_not_guessed(self):
        namespace, _, _ = self.environment()
        home = Panel(None, 'login_new/newlogin_800.dlg')
        home.m_Frames['duplicate'] = Node(home, 2)
        output = io.StringIO()
        with contextlib.redirect_stdout(output): namespace['GetData'](home)
        self.assertIn('NOT installed', output.getvalue())
        self.assertEqual(home.m_Frames['next'].text, 'old caption')

    def test_terms_uses_service_template_and_scrollable_notice(self):
        namespace, modules, _ = self.environment()
        with mock_patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
            panel = namespace['CRegPanel1'](None)
        self.assertEqual(panel.resource, 'login/service.dlg')
        self.assertTrue(all(line.endswith('#r') for line in panel.m_PublicTxtBox.lines))
        self.assertEqual(panel.m_PublicTxtBox.cursor, 0)

    def test_agree_and_reject_do_not_enter_login_or_disconnect(self):
        namespace, modules, events = self.environment()
        with mock_patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
            panel = namespace['CRegPanel1'](None)
            panel.OnMessage(1)
            panel.OnMessage(2)
        self.assertEqual(events, [('step',1), ('home',True), ('show',False)])

    def test_form_loads_only_login_art_and_creates_three_fields(self):
        namespace, _, _ = self.environment()
        with contextlib.redirect_stdout(io.StringIO()): panel = namespace['CRegPanel2'](None)
        self.assertEqual(panel.resource, 'login_new/newlogin_800.dlg')
        self.assertEqual(panel.m_EmailEdit.limit, 32)
        self.assertEqual(panel.m_PwdEdit.limit, 16)
        self.assertEqual(panel.m_PwdEdit2.limit, 16)
        self.assertTrue(panel.m_PwdEdit.m_IsPassword)
        self.assertTrue(panel.m_PwdEdit2.m_IsPassword)
        self.assertIs(panel.m_EmailEdit.next_edit, panel.m_PwdEdit)
        self.assertIs(panel.m_PwdEdit.next_edit, panel.m_PwdEdit2)
        self.assertIs(panel.m_PwdEdit2.next_edit, panel.m_EmailEdit)
        self.assertTrue(panel.m_EmailEdit.active)
        self.assertFalse(hasattr(panel, 'm_EmailEdit2'))
        for name in ('website','forgot','music','close','edt_Name','edt_Pwd'):
            self.assertFalse(panel.m_Frames[name].shown)

    def test_form_inherits_validation_and_info_dispatch(self):
        namespace, _, _ = self.environment()
        with contextlib.redirect_stdout(io.StringIO()): panel = namespace['CRegPanel2'](None)
        self.assertIs(namespace['CRegPanel2'].DoNext, ValidatedForm.DoNext)
        panel.OnMessage(2)
        self.assertTrue(panel.validation_flag)
        panel.OnMessage(3)
        self.assertFalse(panel.validation_flag)
        self.assertEqual(panel.m_PreviewInfo.m_MsgID, 3)

    def test_missing_caption_image_does_not_erase_existing_label(self):
        namespace, _, _ = self.environment()
        home = Panel(None, 'login_new/newlogin_800.dlg')
        def unavailable(*args):
            raise RuntimeError('simulated missing PNG')
        namespace['ui'].CImage = unavailable
        output = io.StringIO()
        with contextlib.redirect_stdout(output): namespace['GetData'](home)
        self.assertEqual(home.m_Frames['next'].text, 'old caption')
        self.assertFalse(hasattr(home.m_Frames['next'], 'm_PreviewCaption'))
        self.assertIn('NOT installed', output.getvalue())

    def test_empty_caption_image_does_not_erase_existing_label(self):
        namespace, _, _ = self.environment()
        home = Panel(None, 'login_new/newlogin_800.dlg')
        namespace['ui'].CImage = lambda *args: Node(size=(0, 0))
        with contextlib.redirect_stdout(io.StringIO()): namespace['GetData'](home)
        self.assertEqual(home.m_Frames['next'].text, 'old caption')
        self.assertFalse(hasattr(home.m_Frames['next'], 'm_PreviewCaption'))

    def test_failed_home_creation_does_not_hide_current_agreement(self):
        namespace, modules, events = self.environment()
        def unavailable(flag):
            raise RuntimeError('simulated homepage error')
        modules['mainpage'].Show = unavailable
        with mock_patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
            panel = namespace['CRegPanel1'](None)
            with self.assertRaisesRegex(RuntimeError, 'homepage error'):
                panel.OnMessage(2)
        self.assertEqual(events, [])

    def test_original_files_unchanged(self):
        self.assertEqual((base.ROOT / 'data/script.fls').read_bytes(), self.source)
        self.assertEqual((base.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes(), self.keys)


if __name__ == '__main__': unittest.main()
