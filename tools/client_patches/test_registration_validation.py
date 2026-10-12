"""Run only newly authored v2.2 validation instructions with fake UI boundaries.

No recovered game module is imported/executed, no native engine or network exists.
The small interpreter rejects unsupported instructions/imports and enforces the
original stacksize; this is logic coverage, not Windows native acceptance.
"""
import json
import operator
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_registration_preview as patch


def run_authored(co, args, context):
    if len(args) != co['argcount']:
        raise AssertionError('call arity mismatch')
    values = dict(enumerate(args))
    instructions = {at: (op, arg) for at, op, arg in patch.normalized(co['code'])}
    stack = []
    pc = 0
    globals_ = {'len': len, 'True': True, 'False': False, 'Step': context.steps.append}
    comparisons = {0: operator.lt, 1: operator.le, 2: operator.eq, 3: operator.ne,
                   4: operator.gt, 5: operator.ge, 8: operator.is_, 9: operator.is_not}
    for _ in range(1000):
        op, arg = instructions[pc]
        next_pc = pc + (3 if op >= 90 else 1)
        if op == 100:
            stack.append(co['consts'][arg])
        elif op == 124:
            stack.append(values[arg])
        elif op == 125:
            values[arg] = stack.pop()
        elif op == 116:
            stack.append(globals_[co['names'][arg].decode('ascii')])
        elif op == 105:
            stack.append(getattr(stack.pop(), co['names'][arg].decode('ascii')))
        elif op == 107:
            fromlist, level = stack.pop(), stack.pop()
            if fromlist is not None or level != -1:
                raise AssertionError('unexpected import form')
            name = co['names'][arg]
            if name == b're':
                stack.append(re)
            elif name == b'commondialog':
                stack.append(SimpleNamespace(ShowNewMessageBox=lambda msg, button: context.messages.append((msg, button))))
            else:
                raise AssertionError('unexpected import: ' + repr(name))
        elif op == 131:
            if arg >= 256:
                raise AssertionError('unexpected keyword call')
            call_args = [stack.pop() for _ in range(arg)][::-1]
            func = stack.pop()
            stack.append(func(*call_args))
        elif op == 106:
            right, left = stack.pop(), stack.pop()
            stack.append(comparisons[arg](left, right))
        elif op == 23:
            right, left = stack.pop(), stack.pop()
            stack.append(left + right)
        elif op == 1:
            stack.pop()
        elif op in (111, 112):
            if bool(stack[-1]) == (op == 112):
                next_pc += arg
        elif op == 113:
            next_pc = arg
        elif op == 83:
            result = stack.pop()
            if stack:
                raise AssertionError('nonempty stack at return')
            return result
        else:
            raise AssertionError('unexpected instruction: ' + str(op))
        if len(stack) > co['stacksize']:
            raise AssertionError('stacksize exceeded')
        pc = next_pc
    raise AssertionError('instruction budget exceeded')


class FakeEdit:
    def __init__(self, value):
        self.value = value
        self.reads = 0

    def GetText(self):
        self.reads += 1
        return self.value


class FakePanel:
    def __init__(self, functions, email=b'preview@example.invalid', password=b'Preview123', confirmation=b'Preview123'):
        self.functions = functions
        self.m_EmailEdit = FakeEdit(email)
        self.m_PwdEdit = FakeEdit(password)
        self.m_PwdEdit2 = FakeEdit(confirmation)
        # Deliberately no email2, CAPTCHA, Save or HTTP/browser APIs.
        self.steps = []
        self.messages = []
        self.checks = 0

    def invoke(self, name, *args):
        return run_authored(self.functions['CRegPanel2/' + name], [self, *args], self)

    def DoCheck(self):
        self.checks += 1
        return self.invoke('DoCheck')

    def CheckEmail(self, value):
        return self.invoke('CheckEmail', value)

    def DoNext(self, validate):
        return self.invoke('DoNext', validate)


class RegistrationValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (patch.ROOT / 'data/script.fls').read_bytes()
        cls.keys = (patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
        cls.output, cls.report = patch.build(cls.source, cls.keys, stage='form-validate')
        rows = patch.entries(cls.output)[1]
        metadata = json.loads(cls.keys)['4007']
        raw = patch.xor_payload(patch.zlib.decompress(rows[4007][1]), metadata)
        cls.functions = dict(patch.objects(patch.tree(raw)))

    def panel(self, **kwargs):
        return FakePanel(self.functions, **kwargs)

    def error(self, idx):
        return self.functions['CRegPanel2/DoCheck']['consts'][idx]

    def offline(self):
        return self.functions['CRegPanel2/DoNext']['consts'][10]

    def test_only_authored_bodies_enter_the_test_interpreter(self):
        for name, generator in [('DoCheck', patch.validation_check), ('CheckEmail', patch.validation_email),
                                ('DoNext', patch.validation_next), ('OnMessage', patch.validation_messages)]:
            co = self.functions['CRegPanel2/' + name]
            body = generator(co)
            self.assertEqual(co['code'], body + patch.assemble((9, None)) * (len(co['code']) - len(body)))

    def test_every_field_is_required_including_whitespace_only(self):
        for field in ('email', 'password', 'confirmation'):
            for value in (b'', b' ', b'\t\r\n'):
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.panel(**{field: value}).DoCheck(), self.error(5))

    def test_password_length_boundaries(self):
        for length in (1, 5, 6, 16, 17, 40):
            with self.subTest(length=length):
                value = b'A' * length
                result = self.panel(password=value, confirmation=value).DoCheck()
                self.assertEqual(result, None if 6 <= length <= 16 else self.error(2))

    def test_password_confirmation_exact_and_case_sensitive(self):
        for value in (b'Preview124', b'preview123', b'Preview123 '):
            self.assertEqual(self.panel(confirmation=value).DoCheck(), self.error(3))

    def test_email_maximum_matches_existing_32_character_edit_limit(self):
        for length in (32, 33, 100):
            value = b'a' * (length - len(b'@example.com')) + b'@example.com'
            with self.subTest(length=length):
                self.assertEqual(self.panel(email=value).DoCheck(), None if length == 32 else self.error(8))

    def test_email_outer_whitespace_is_trimmed(self):
        self.assertIsNone(self.panel(email=b'  preview@example.invalid  ').DoCheck())

    def test_basic_email_syntax_rejects_common_malformed_values(self):
        for value in (b'a', b'abc', b'@example.com', b'a@', b'a@example', b'a@@example.com',
                      b'a@.example.com', b'a@example..com', b'a@exa_mple.com', b'a b@example.com',
                      b'a\nb@example.com', b'a@example.com/xx', '测试@example.com'.encode('utf-8')):
            with self.subTest(value=value):
                self.assertEqual(self.panel(email=value).DoCheck(), self.error(4))

    def test_basic_email_profile_accepts_common_ascii_addresses(self):
        for value in (b'a@b.co', b'preview@example.invalid', b'user.name@example.com',
                      b'user_name@a-b.example.com', b'USER-NAME@EXAMPLE.COM'):
            with self.subTest(value=value):
                self.assertIsNone(self.panel(email=value).DoCheck())

    def test_email_helper_checks_its_own_length(self):
        panel = self.panel()
        self.assertFalse(panel.CheckEmail(b'a@b'))
        self.assertFalse(panel.CheckEmail(b'a' * 21 + b'@example.com'))
        self.assertTrue(panel.CheckEmail(b'a' * 20 + b'@example.com'))

    def test_next_invalid_shows_error_not_offline_notice(self):
        cases = [({'password': b'123', 'confirmation': b'123'}, 2),
                 ({'email': b''}, 5), ({'confirmation': b'Other123'}, 3),
                 ({'email': b'invalid'}, 4), ({'email': b'a' * 21 + b'@example.com'}, 8)]
        for values, idx in cases:
            panel = self.panel(**values)
            panel.invoke('OnMessage', 2)
            self.assertEqual(panel.checks, 1)
            self.assertEqual(panel.messages, [(self.error(idx), '確定'.encode('cp950'))])
            self.assertNotEqual(panel.messages[0][0], self.offline())

    def test_next_valid_only_shows_offline_notice(self):
        panel = self.panel()
        panel.invoke('OnMessage', 2)
        self.assertEqual(panel.checks, 1)
        self.assertEqual(panel.messages, [(self.offline(), '確定'.encode('cp950'))])

    def test_info_bypasses_validation_and_does_not_read_fields(self):
        panel = self.panel(email=b'', password=b'', confirmation=b'')
        panel.invoke('OnMessage', 3)
        self.assertEqual(panel.checks, 0)
        self.assertEqual(panel.messages, [(self.offline(), '確定'.encode('cp950'))])
        self.assertEqual([panel.m_EmailEdit.reads, panel.m_PwdEdit.reads, panel.m_PwdEdit2.reads], [0, 0, 0])

    def test_back_returns_to_terms_without_validation(self):
        panel = self.panel()
        panel.invoke('OnMessage', 1)
        self.assertEqual(panel.steps, [0])
        self.assertEqual(panel.checks, 0)
        self.assertEqual(panel.messages, [])

    def test_unknown_and_disabled_captcha_actions_do_nothing(self):
        panel = self.panel()
        for message in (0, 4, 99):
            panel.invoke('OnMessage', message)
        self.assertEqual(panel.steps, [])
        self.assertEqual(panel.messages, [])
        self.assertEqual(panel.checks, 0)

    def test_explicit_arity_change_is_limited_to_next(self):
        self.assertEqual(self.functions['CRegPanel2/DoNext']['argcount'], 2)
        self.assertEqual(self.functions['CRegPanel2/DoCheck']['argcount'], 1)
        self.assertEqual(self.functions['CRegPanel2/CheckEmail']['argcount'], 2)

    def test_safety_stubs_still_return_none(self):
        for path in (patch.NETWORK_PATHS - {'CRegPanel2/DoNext'}) | {
                'CRegPanel2/Save', 'Register2980', 'CRegPanel2/OnEditChange'}:
            co = self.functions[path]
            seq = patch.normalized(co['code'])
            self.assertEqual(seq[:2], [(0, 100, co['consts'].index(None)), (3, 83, None)])
            self.assertTrue(all(op == 9 for _, op, _ in seq[2:]), path)

    def test_archive_scope_and_deterministic_output(self):
        rows = patch.entries(self.source)[1]
        new_rows = patch.entries(self.output)[1]
        self.assertEqual([i for i, (a, b) in enumerate(zip(rows, new_rows)) if a != b], [337, 4007])
        self.assertEqual(patch.build(self.source, self.keys, stage='form-validate'), (self.output, self.report))
        self.assertEqual(patch.sha(self.output), '29d36efac4d1d941cec0f50a1b3956d24ba65f925b066756e9510362de1f0938')

    def test_no_native_or_live_registration_claim(self):
        self.assertFalse(self.report['native_windows_client_tested'])
        self.assertFalse(self.report['recovered_code_executed'])
        self.assertEqual(self.report['kind'], 'registration_locally_validated_offline_preview_only')
        self.assertEqual((patch.ROOT / 'data/script.fls').read_bytes(), self.source)
        self.assertEqual((patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes(), self.keys)


if __name__ == '__main__':
    unittest.main()
