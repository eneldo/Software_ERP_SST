"""Tests estáticos de infraestructura: scripts shell, compose, CI y ejemplos de entorno."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = sorted((ROOT / "scripts").glob("*.sh"))
COMPOSE_FILES = ["docker-compose.yml", "docker-compose.prod.yml", "docker-compose.coolify.yml"]


def _find_bash() -> str | None:
    import os

    if os.name == "nt":
        candidate = Path(r"C:\Program Files\Git\bin\bash.exe")
        if candidate.exists():
            return str(candidate)
    bash = shutil.which("bash")
    return bash

BASH = _find_bash()


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class ShellScriptStaticTests(unittest.TestCase):
    def test_scripts_pass_bash_n(self) -> None:
        if BASH is None:
            self.skipTest("bash no disponible")
        for script in SCRIPTS:
            result = subprocess.run(
                [BASH, "-n", str(script)], capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, f"{script.name}: {result.stderr}")

    def test_scripts_pass_shellcheck_warning(self) -> None:
        shellcheck = shutil.which("shellcheck")
        if shellcheck is None:
            self.skipTest("shellcheck no disponible")
        for script in SCRIPTS:
            result = subprocess.run(
                [shellcheck, "--severity=warning", str(script)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{script.name}: {result.stdout}")

    def test_restore_validate_only_fixture(self) -> None:
        if BASH is None:
            self.skipTest("bash no disponible")
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            (fixture / "dump.sql").write_text("SELECT 1;\n", encoding="utf-8")
            import gzip

            with gzip.open(fixture / "erp_sst_backup_fixture_database.sql.gz", "wb") as fh:
                fh.write(b"SELECT 1;\n")
            uploads = fixture / "uploads"
            uploads.mkdir()
            (uploads / "a.txt").write_text("hola\n", encoding="utf-8")
            import tarfile

            with tarfile.open(fixture / "erp_sst_backup_fixture_uploads.tar.gz", "w:gz") as tf:
                tf.add(uploads, arcname=".")
            import hashlib

            digest_lines = []
            for name in (
                "erp_sst_backup_fixture_database.sql.gz",
                "erp_sst_backup_fixture_uploads.tar.gz",
            ):
                digest = hashlib.sha256((fixture / name).read_bytes()).hexdigest()
                digest_lines.append(f"{digest}  {name}")
            (fixture / "erp_sst_backup_fixture.sha256").write_text(
                "\n".join(digest_lines) + "\n", encoding="utf-8", newline="\n"
            )
            (fixture / ".env.production").write_text("", encoding="utf-8")
            import os

            def _msys_path(path: Path) -> str:
                value = str(path)
                if os.name == "nt" and len(value) > 2 and value[1] == ":":
                    drive = value[0].lower()
                    return f"/{drive}{value[2:].replace(chr(92), '/')}"
                return value

            run_env = dict(os.environ)
            run_env["ENV_FILE"] = _msys_path(fixture / ".env.production")
            run_env["VALIDATE_ONLY"] = "true"
            git_bin = str(Path(BASH).parent)
            git_usr_bin = str(Path(BASH).parent.parent / "usr" / "bin")
            run_env["PATH"] = os.pathsep.join([git_usr_bin, git_bin, run_env.get("PATH", "")])
            result = subprocess.run(
                [
                    BASH,
                    _msys_path(ROOT / "scripts" / "restore_postgres.sh"),
                    _msys_path(fixture / "erp_sst_backup_fixture_database.sql.gz"),
                    _msys_path(fixture / "erp_sst_backup_fixture_uploads.tar.gz"),
                    _msys_path(fixture / "erp_sst_backup_fixture.sha256"),
                ],
                capture_output=True,
                text=True,
                env=run_env,
                cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Backup validado sin restaurar.", result.stdout)


class RestoreScriptContractTests(unittest.TestCase):
    def test_restore_supports_validated_swap_and_rollback(self) -> None:
        script = _read("scripts/restore_postgres.sh")
        for marker in (
            "VALIDATE_ONLY",
            "CONFIRM_RESTORE",
            "UPLOADS_SWAPPED",
            "DB_SWAPPED",
            "_uploads_restore_",
            "_uploads_rollback_",
            "pg_terminate_backend",
            "sha256sum --check",
            "tar -tzf",
            "gzip -t",
        ):
            self.assertIn(marker, script, marker)

    def test_docker_check_after_validate_only(self) -> None:
        script = _read("scripts/restore_postgres.sh")
        self.assertLess(
            script.index("VALIDATE_ONLY"),
            script.index("command -v docker"),
            "VALIDATE_ONLY debe funcionar sin docker",
        )

    def test_backup_has_writer_coordination_and_offsite(self) -> None:
        script = _read("scripts/backup_postgres.sh")
        for marker in (
            "BACKUP_WRITER_MODE",
            "OFFSITE_COMMAND",
            "flock",
            "gzip -t",
            "tar -tzf",
            "chmod 700",
            "umask 077",
            "stop backend",
        ):
            self.assertIn(marker, script, marker)


class ComposeStaticTests(unittest.TestCase):
    def test_compose_files_define_migrate_profile(self) -> None:
        for path in ("docker-compose.prod.yml", "docker-compose.coolify.yml"):
            content = _read(path)
            self.assertIn("backend-migrate:", content, path)
            self.assertIn("profiles: [migrations]", content, path)
            self.assertIn("alembic, upgrade, head", content, path)

    def test_coolify_does_not_auto_migrate(self) -> None:
        content = _read("docker-compose.coolify.yml")
        self.assertNotIn("alembic upgrade head && exec gunicorn", content)

    def test_image_tags_by_git_sha_supported(self) -> None:
        for path in ("docker-compose.prod.yml", "docker-compose.coolify.yml"):
            content = _read(path)
            self.assertIn("image: erp-sst-backend:${IMAGE_TAG:-local}", content, path)
            self.assertIn("image: erp-sst-frontend:${IMAGE_TAG:-local}", content, path)

    def test_prod_healthcheck_does_not_hardcode_domain(self) -> None:
        content = _read("docker-compose.prod.yml")
        self.assertIn('Host: $${TRUSTED_HOSTS%%,*}', content)
        self.assertNotIn('Host: vaner.cloud', content)

    def test_env_example_documents_backup_and_artifact_vars(self) -> None:
        content = _read(".env.production.example")
        for marker in ("BACKUP_DIR", "BACKUP_RETENTION_DAYS", "BACKUP_WRITER_MODE", "OFFSITE_COMMAND", "IMAGE_TAG"):
            self.assertIn(marker, content)


class WorkflowStaticTests(unittest.TestCase):
    def test_infrastructure_workflow_covers_shell_and_smoke(self) -> None:
        content = _read(".github/workflows/infrastructure.yml")
        for marker in ("shellcheck", "bash -n", "VALIDATE_ONLY", "PLAYWRIGHT_EXTERNAL_SERVER", "test_infrastructure_static.py"):
            self.assertIn(marker, content)

    def test_yamls_parse(self) -> None:
        import yaml

        for rel in (
            "docker-compose.yml",
            "docker-compose.prod.yml",
            "docker-compose.coolify.yml",
            ".github/workflows/infrastructure.yml",
            ".github/workflows/ci.yml",
            ".github/workflows/secret-scanning.yml",
        ):
            yaml.safe_load(_read(rel))


if __name__ == "__main__":
    unittest.main()
