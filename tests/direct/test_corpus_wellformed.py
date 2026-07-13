import glob
import json


def test_all_manifests_wellformed():
    files = glob.glob("attacks/*/manifest.json")
    assert files
    required = {"id", "payload", "target_sink", "expected_effect", "countering_layer"}
    for f in files:
        with open(f, encoding="utf-8") as fh:
            records = json.load(fh)
        assert isinstance(records, list) and records
        ids = set()
        for r in records:
            assert required.issubset(r.keys()), f"{f}: missing keys in {r.get('id')}"
            assert r["id"] not in ids, f"{f}: duplicate id {r['id']}"
            ids.add(r["id"])
