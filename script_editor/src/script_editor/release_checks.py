"""Windows release tests must run GUI and actual compilers, not silently skip."""

from __future__ import annotations

import argparse
import os
import unittest
from pathlib import Path

from .core.compiler.distribution import audit_runtimes

# Independent game/DLL materials are deliberately not part of a standalone tool.
# Only these exact opt-in tests may be absent from a release build environment.
OPTIONAL_MATERIAL_TESTS = {
    "test_native_evidence.DispatchEvidence.test_current_dll_dispatch_without_executing_it",
    "test_native_legacy.RealMaterialBuild.test_actual_script_register_source",
    "test_native_legacy.RealMaterialBuild.test_actual_data_offline_probe",
    "test_native_legacy.RealMaterialBuild.test_real_mainpage_337_rejected_without_opcode_repairs",
    "test_workflow.RealRegistrationWorkflowTests.test_registration_source_prepare_publish_reopen_continue",
    "test_workflow.RealRegistrationWorkflowTests.test_real_data_offline_prepare_publish_reopen_continue",
}


REQUIRED_RELEASE_TESTS = {
    "test_gui.GuiTests.test_large_tree_uses_supported_qt_without_none_reference_corruption",
    "test_gui.GuiTests.test_workspace_toolbar_shares_real_actions_and_welcome",
    "test_gui.GuiTests.test_search_case_whole_word_unicode_and_single_undo",
    "test_gui.GuiTests.test_window_native_build_disabled",
    "test_gui_workflow.GuiWorkflowTests.test_real_worker_callback_runs_on_gui_thread_and_restores_actions",
    "test_gui_workflow.GuiWorkflowTests.test_project_adoption_rolls_back_partial_widgets",
    "test_compiler.LegacyCompilation.test_actual_cpython25",
    "test_compiler.LegacyCompilation.test_actual_cpython27",
    "test_native_legacy.ActualLegacyBuild.test_full_actual_py25_compile_native_package_readback",
    "test_native_legacy.ActualLegacyBuild.test_full_actual_py27_compile_native_package_readback",
    "test_workflow.ActualWorkflowTests.test_real_both_vm_preview_publish_save_reopen_and_continue",
}


def suite_ids(suite):
    result = set()
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            result.update(suite_ids(test))
        else:
            result.add(test.id())
    return result


def forbidden_skips(result):
    return [
        (test.id(), reason)
        for test, reason in result.skipped
        if test.id() not in OPTIONAL_MATERIAL_TESTS
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Strict Windows editor release checks")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve(strict=True)
    try:
        audit_runtimes(root, execute=True)
    except (OSError, ValueError) as exc:
        print(f"Release blocked: {exc}")
        return 2
    previous = {
        key: os.environ.get(key)
        for key in ("MXSJ_PY25", "MXSJ_PY27", "QT_QPA_PLATFORM")
    }
    try:
        for vm, suffix in (("py25", "25"), ("py27", "27")):
            os.environ["MXSJ_PY" + suffix] = str(
                root / "runtimes" / vm / "win-x86/python.exe"
            )
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        suite = unittest.defaultTestLoader.discover(str(root / "tests"))
        missing = REQUIRED_RELEASE_TESTS - suite_ids(suite)
        if missing:
            print(
                "Release blocked: mandatory tests were not discovered: "
                + ", ".join(sorted(missing))
            )
            return 2
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        blocked = forbidden_skips(result)
        for name, reason in blocked:
            print(f"Release blocked by skipped test: {name}: {reason}")
        # Detect standard-library bytecode writes or other runtime changes by tests.
        audit_runtimes(root, execute=True)
        return 0 if result.wasSuccessful() and not blocked else 1
    except (OSError, ValueError) as exc:
        print(f"Release blocked: {exc}")
        return 2
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    raise SystemExit(main())
