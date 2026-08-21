from pathlib import Path

async def delete_file(file: Path):
    """
    Deletes a file from the filesystem.
    """
    file.unlink()