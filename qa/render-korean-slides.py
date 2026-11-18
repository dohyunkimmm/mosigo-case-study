"""Render Korean slides without Impress inserting gaps between digits and units."""
from pathlib import Path
from subprocess import run
from sys import argv
from tempfile import TemporaryDirectory
from zipfile import ZipFile

source = Path(argv[1]).resolve()
output = Path(argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)

with TemporaryDirectory() as work:
    root = Path(work)
    office = ["libreoffice", f"-env:UserInstallation={(root / 'profile').as_uri()}", "--headless"]
    run([*office, "--convert-to", "odp", "--outdir", work, str(source)], check=True)
    original = root / (source.stem + ".odp")
    # Use the original stem so LibreOffice exports the expected PDF filename.
    revised = root / "normalized" / original.name
    revised.parent.mkdir()
    with ZipFile(original) as src, ZipFile(revised, "w") as out:
        for entry in src.infolist():
            data = src.read(entry)
            if entry.filename in {"styles.xml", "content.xml"}:
                data = data.replace(b'style:text-autospace="ideograph-alpha"',
                                    b'style:text-autospace="none"')
            out.writestr(entry, data)
    run([*office, "--convert-to", "pdf", "--outdir", str(output), str(revised)], check=True)
