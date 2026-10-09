"""Keep release packaging aligned with the application's actual Qt imports."""

import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]


def test_packaging_includes_the_apps_qt_binding():
    tree = ast.parse((ROOT / "rota-ai.spec").read_text(encoding="utf-8"))
    hiddenimports = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "common_hiddenimports"
            for target in node.targets
        )
    )
    qt_imports = set()
    for path in (ROOT / "desktop").rglob("*.py"):
        if "tests" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("PySide6."):
                qt_imports.add(node.module)
    assert qt_imports
    assert qt_imports <= set(hiddenimports)
    assert not any(name.startswith("PyQt6") for name in hiddenimports)


def test_windows_release_uses_declared_dependencies_and_checks_startup():
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    windows_job = workflow.split("  build-windows:", 1)[1].split("  build-linux:", 1)[0]
    assert "python -m pip install -r requirements.txt" in windows_job
    assert "pip install PyQt6" not in windows_job
    assert "--smoke-test" in windows_job
    assert "WaitForExit(60000)" in windows_job
    assert "$app.ExitCode -ne 0" in windows_job


def test_windows_bundle_uses_system_icu_without_dropping_versioned_qt_icu():
    tree = ast.parse((ROOT / "rota-ai.spec").read_text(encoding="utf-8"))
    guard = next(
        node
        for node in tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "IS_WINDOWS"
        and any(
            isinstance(child, ast.Attribute) and child.attr == "binaries"
            for child in ast.walk(node)
        )
    )
    bundled = SimpleNamespace(
        binaries=[
            ("icuuc.dll", "unrelated/icuuc.dll", "BINARY"),
            ("PySide6/icuuc73.dll", "qt/icuuc73.dll", "BINARY"),
            ("PySide6/Qt6Core.dll", "qt/Qt6Core.dll", "BINARY"),
        ]
    )
    code = compile(ast.Module(body=[guard], type_ignores=[]), "rota-ai.spec", "exec")
    exec(code, {"IS_WINDOWS": True, "a": bundled})
    assert [row[0] for row in bundled.binaries] == ["PySide6/icuuc73.dll", "PySide6/Qt6Core.dll"]
