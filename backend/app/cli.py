"""Command-line tasks. The snapshot import runs one time at setup (decision D1)."""
from pathlib import Path

import click
from flask import current_app

from .collection.importer import import_file, rescore_all
from .db import session_scope


def register_cli(app):
    @app.cli.command("import-snapshot")
    @click.option("--dir", "directory", default=None, help="Folder with gaf_*.json files.")
    def import_snapshot(directory):
        """Import all GAF snapshot files, then score the imported prospects."""
        folder = Path(directory or current_app.config["APP_CONFIG"].snapshot_dir)
        files = sorted(folder.glob("gaf_*.json"))
        if not files:
            raise click.ClickException(f"No gaf_*.json files in {folder}.")
        with session_scope() as s:
            imported: list[int] = []
            for f in files:
                r = import_file(s, f)
                imported.extend(r.prospect_ids)
                state = "complete" if r.complete else "partial"
                click.echo(f"{r.file}: {r.valid} valid of {r.expected_total} shown by GAF ({state}); "
                           f"{r.inserted} new, {r.updated} updated, {len(r.invalid)} invalid.")
                for bad in r.invalid[:10]:
                    click.echo(f"  invalid record {bad['index']} ({bad['gaf_source_id']}): {bad['error']}")
            # Only imported rows changed, so only they are rescored. `flask rescore` recalculates all.
            n = rescore_all(s, prospect_ids=imported)
            click.echo(f"Scored {n} prospects with rule version v1.")

    @app.cli.command("rescore")
    def rescore():
        """Recalculate all scores with the current time."""
        with session_scope() as s:
            click.echo(f"Scored {rescore_all(s)} prospects.")
