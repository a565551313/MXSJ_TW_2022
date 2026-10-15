"""Windows release tests must run GUI and actual compilers, not silently skip."""

from __future__ import annotations

import argparse
import os
import unittest
from pathlib import Path

from .core.compiler.distribution import audit_runtimes
from .core.services.bundled_catalog import audit_catalogs
from .recovery_dependencies import checked_recovery_source

# Independent game/DLL materials are deliberately not part of a standalone tool.
# Only these exact opt-in tests may be absent from a release build environment.
OPTIONAL_MATERIAL_TESTS = {
    "test_data_corpus.RealDataCorpusTests.test_every_real_data_entry_candidate_has_exact_strict_origin",
    "test_data_corpus.RealDataCorpusTests.test_real_data_corpus_probe_compile_publish_reopen_does_not_execute",
    "test_data_corpus.RealDataCorpusTests.test_real_uuid_negative_longs_remain_exact_not_replaced_or_nopped",
    "test_data_corpus.RealDataCorpusTests.test_real_uuid_direct_browser_opens_without_prebuilt_corpus",
    "test_gui_data_corpus.RealDataCorpusGuiTests.test_all_121_real_data_scripts_open_as_editable_vm27_tabs",
    "test_corpus_import.RealCorpusImportTests.test_eight_real_repairs_match_exact_pyc_and_original_catalog_unchanged",
    "test_corpus_import.RealCorpusImportTests.test_124_and_4861_keep_editable_candidates_without_verified_origin",
    "test_corpus_import.RealCorpusImportTests.test_2371_local_repair_delta_not_misrepresented_as_verified",
    "test_corpus_import.RealCorpusImportTests.test_real_repaired_4305_compile_publish_reopen_without_execution",
    "test_corpus_import.RealCorpusImportTests.test_real_large_entry_1182_is_not_blocked_by_live_process_output_limit",
    "test_recovery_candidates.ActualCorpusTests.test_original_archive_path_uses_secondary_after_primary_timeout",
    # Research samples are external test evidence, never a product dependency.
    "test_recovery_candidates.ActualCorpusTests.test_real_partial_source_is_editable_but_never_complete",
    "test_recovery_candidates.ActualCorpusTests.test_real_non_utf8_candidates_keep_exact_engine_bytes",
    "test_recovery_candidates.ActualCorpusTests.test_real_pathological_primary_times_out_secondary_still_recovers",
    "test_recovery_candidates.ActualCorpusTests.test_real_both_fail_has_no_fake_source",
    "test_recovery_candidates.ActualCorpusTests.test_real_complete_pair_keeps_two_candidates_and_origin",
    "test_module_browser.RealModuleBrowserTests.test_real_registration_correct_lists_do_not_bypass_fixed_capacity",
    "test_module_browser.RealModuleBrowserTests.test_real_script_and_data_recover_edit_without_original_authored_source",
    "test_native_evidence.DispatchEvidence.test_current_dll_dispatch_without_executing_it",
    "test_native_legacy.RealMaterialBuild.test_actual_script_register_source",
    "test_native_legacy.RealMaterialBuild.test_actual_data_offline_probe",
    "test_native_legacy.RealMaterialBuild.test_real_mainpage_337_rejected_without_opcode_repairs",
    "test_workflow.RealRegistrationWorkflowTests.test_registration_source_prepare_publish_reopen_continue",
    "test_workflow.RealRegistrationWorkflowTests.test_real_data_offline_prepare_publish_reopen_continue",
}


REQUIRED_RELEASE_TESTS = {
    "test_gui_data_corpus.DataCorpusGuiTests.test_data_manifest_import_is_not_blocked_by_script_only_guard",
    "test_gui_data_corpus.DataCorpusGuiTests.test_data_generation_action_builds_and_associates_vm27_corpus",
    "test_data_corpus.DataCorpusTests.test_full_build_directory_exclusion_strict_pyc_and_exact_raw_roundtrip",
    "test_data_corpus.ActualSignedLongRecoveryTests.test_both_real_vms_negative_long_recovery_recompiles_exact_constants",
    "test_gui_corpus_workspace.CorpusWorkspaceGuiTests.test_project_restores_unsaved_text_candidates_diagnostics_and_vm",
    "test_gui_corpus_workspace.CorpusWorkspaceGuiTests.test_unverified_external_pyc_cannot_reach_native_prepare",
    "test_gui_corpus_workspace.CorpusWorkspaceGuiTests.test_verify_catalog_action_writes_new_file_and_leaves_original_untouched",
    "test_workspace_state.WorkspaceStateTests.test_unsaved_draft_report_and_exact_raw_bytes_roundtrip",
    "test_corpus_import.CorpusImportTests.test_repair_parameters_require_exact_strict_byte_equality",
    "test_recovery_candidates.ActualEngineSmoke.test_both_real_vms_second_engine_compile_without_execution",
    "test_gui_recovery_candidates.CandidateGuiTests.test_other_candidate_opens_fresh_tab_without_overwriting_dirty_edits",
    "test_gui_recovery_candidates.CandidateGuiTests.test_cancel_button_stops_recovery_and_keeps_dirty_buffer",
    "test_gui_module.GuiModuleTests.test_open_archive_auto_pins_catalog_then_recovers_without_manual_source",
    "test_module_browser.ModuleBrowserTests.test_both_real_vms_package_recover_edit_compile_publish_reopen",
    "test_gui_module.GuiModuleTests.test_both_vms_real_unbound_open_edit_review_publish_and_project_reopen",
    "test_archive_revision.ArchiveRevisionTests.test_path_stat_and_fstat_differences_do_not_reject_unchanged_package",
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
        from .core.services.pycdc_engine import discover_pycdc

        checked_recovery_source(root)
        if discover_pycdc(root / "recovery_engines" / "pycdc") is None:
            raise ValueError("missing verified second recovery engine")
        audit_catalogs(root)
        audit_runtimes(root, execute=True)
    except (OSError, ValueError) as exc:
        print(f"Release blocked: {exc}")
        return 2
    previous = {
        key: os.environ.get(key)
        for key in ("MXSJ_PY25", "MXSJ_PY27", "QT_QPA_PLATFORM", "MXSJ_PYCDC_BUNDLE")
    }
    try:
        for vm, suffix in (("py25", "25"), ("py27", "27")):
            os.environ["MXSJ_PY" + suffix] = str(
                root / "runtimes" / vm / "win-x86/python.exe"
            )
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["MXSJ_PYCDC_BUNDLE"] = str(root / "recovery_engines" / "pycdc")
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
        from .core.services.pycdc_engine import discover_pycdc

        checked_recovery_source(root)
        if discover_pycdc(root / "recovery_engines" / "pycdc") is None:
            raise ValueError("missing verified second recovery engine")
        audit_catalogs(root)
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
