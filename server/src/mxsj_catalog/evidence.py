"""Validate review evidence structure and cross-file consistency, without execution."""
from collections import Counter
from typing import Any

from .errors import CatalogIntegrityError


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CatalogIntegrityError(message)


def evidence_record(item: Any, kind: str) -> dict:
    """Reject missing/empty evidence rather than manufacturing default values."""
    require(type(item) is dict, f"{kind}: expected an evidence object")
    common = {"entry_index", "table"}
    extra = ({"record_key", "reasons", "native_verified", "value_under_applied_profile"}
             if kind == "quarantine" else {"order", "code_offset", "key", "old_value", "new_value"})
    require(common | extra <= item.keys(), f"{kind}: missing required evidence fields")
    require(type(item["entry_index"]) is int and type(item["table"]) is str and bool(item["table"]),
            f"{kind}: invalid source identity")
    if kind == "quarantine":
        require(type(item["record_key"]) is int, "quarantine: expected integer record key")
        require(item["native_verified"] is False, "quarantine: must remain native-unverified")
        reasons = item["reasons"]
        require(type(reasons) is list and bool(reasons)
                and all(type(r) is str and bool(r.strip()) for r in reasons),
                "quarantine: missing/invalid reasons")
        fields = ("value_under_applied_profile",)
    else:
        require(all(type(item[f]) is int and item[f] >= 0 for f in ("order", "code_offset", "key")),
                "overwrites: invalid order, code offset or key")
        fields = ("old_value", "new_value")
    for field in fields:
        value = item[field]
        require(type(value) is dict and len(value) == 1
                and next(iter(value)) in ("dict", "tuple", "list")
                and type(next(iter(value.values()))) is list and bool(next(iter(value.values()))),
                f"{kind}: {field} must retain a nonempty typed evidence envelope")
    return item


def validate_consistency(quarantine, overwrites, validation, overwrite_summary) -> None:
    """Hashes prove bytes match the manifest, not that those bytes agree with each other."""
    require(type(validation) is dict, "validation: expected summary object")

    def expected(mapping, key, label):
        value = mapping.get(key)
        require(type(value) is int and value >= 0, f"{label}: missing/invalid expected count {key}")
        return value

    require(len(quarantine) == expected(validation, "quarantined_record_count", "quarantine"),
            "quarantine: record count differs from validation summary")
    require(len(overwrites) == expected(validation, "skill_overwrite_count", "overwrites"),
            "overwrites: record count differs from validation summary")
    identities = [(q.entry_index, q.table, q.record_key) for q in quarantine]
    require(len(set(identities)) == len(identities), "quarantine: duplicate evidence identity")
    tables = validation.get("tables")
    require(type(tables) is dict and bool(tables), "validation: missing table quarantine counts")
    observed = Counter(str(q.entry_index) for q in quarantine)
    require(not observed.keys() - tables.keys(), "quarantine: source not declared in validation")
    for source, table in tables.items():
        require(type(table) is dict, "validation: invalid table summary")
        require(observed[source] == expected(table, "quarantined_records", "quarantine"),
                f"quarantine: count for source {source} differs from validation summary")

    evidence_keys = [(o.entry_index, o.table, o.order) for o in overwrites]
    require(len(set(evidence_keys)) == len(evidence_keys), "overwrites: duplicate write identity")
    summary = {r["write_order"]: r for r in overwrite_summary.records}
    require(len(summary) == len(overwrites), "overwrites: count differs from CSV write summary")
    for item in overwrites:
        row = summary.get(item.order)
        require(row is not None and row["skill_id"] == item.key
                and row["code_offset"] == item.code_offset and row["source_entry"] == item.entry_index,
                "overwrites: identity/offset differs from CSV write summary")
        require(row["identical_values"] == (item.old_value == item.new_value),
                "overwrites: identical-values flag differs from full evidence")
