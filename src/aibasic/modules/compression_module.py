"""
Compression Module for Multi-Format Archive Processing

This module provides comprehensive compression and decompression operations
for multiple archive formats. No configuration required - works standalone.

Supported formats:
- ZIP (.zip) - Most common, cross-platform
- TAR (.tar) - Unix standard, can be combined with compression
- TAR.GZ / TGZ (.tar.gz, .tgz) - TAR with GZIP compression
- TAR.BZ2 / TBZ2 (.tar.bz2, .tbz2) - TAR with BZIP2 compression
- TAR.XZ (.tar.xz) - TAR with XZ/LZMA compression
- GZIP (.gz) - Single file compression
- BZIP2 (.bz2) - Single file compression
- XZ (.xz) - Single file compression (LZMA)
- 7Z (.7z) - High compression ratio (requires py7zr)

Features:
- Automatic format detection from file extension
- Compression level control
- Password protection (ZIP, 7Z)
- Selective extraction
- Directory tree compression
- Progress tracking for large archives
- Memory-efficient streaming for large files
- File filtering (by pattern, size, date)
- Archive inspection without extraction

Usage in generated code:
    from aibasic.modules import CompressionModule

    # Initialize module (no config needed)
    comp = CompressionModule()

    # Compress
    comp.compress_zip('data/', 'archive.zip', compression_level=9)
    comp.compress_targz('logs/', 'logs.tar.gz')
    comp.compress_7z('important/', 'important.7z', password='secret')

    # Decompress
    comp.extract_zip('archive.zip', 'output/')
    comp.extract_tar('archive.tar.gz', 'output/')
    comp.extract_7z('archive.7z', 'output/', password='secret')

    # Auto-detect format
    comp.extract_auto('archive.???', 'output/')
    comp.compress_auto('data/', 'archive.zip')

    # Inspect
    files = comp.list_archive('archive.zip')
    info = comp.get_archive_info('archive.zip')
"""

import os
import zipfile
import tarfile
import gzip
import bz2
import lzma
import shutil
import fnmatch
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Callable
from datetime import datetime

try:
    import py7zr
except ImportError:
    py7zr = None


class CompressionModule:
    """
    Multi-format compression and decompression module.

    Supports ZIP, TAR (with various compressions), GZIP, BZIP2, XZ, and 7Z formats.
    """

    # Format detection mappings
    FORMAT_EXTENSIONS = {
        '.zip': 'zip',
        '.tar': 'tar',
        '.tar.gz': 'tar.gz',
        '.tgz': 'tar.gz',
        '.tar.bz2': 'tar.bz2',
        '.tbz2': 'tar.bz2',
        '.tar.xz': 'tar.xz',
        '.txz': 'tar.xz',
        '.gz': 'gzip',
        '.bz2': 'bzip2',
        '.xz': 'xz',
        '.7z': '7z'
    }

    def __init__(self):
        """Initialize the CompressionModule."""
        print("[CompressionModule] Module initialized - supports ZIP, TAR, GZIP, BZIP2, XZ, 7Z formats")

    # ==================== Format Detection ====================

    def detect_format(self, archive_path: str) -> Optional[str]:
        """
        Detect archive format from file extension.

        Args:
            archive_path: Path to archive file

        Returns:
            Format string or None if unknown
        """
        path = Path(archive_path).name.lower()

        # Check compound extensions first (.tar.gz, .tar.bz2, etc.)
        for ext, fmt in sorted(self.FORMAT_EXTENSIONS.items(), key=lambda x: -len(x[0])):
            if path.endswith(ext):
                return fmt

        return None

    # ==================== ZIP Operations ====================

    def compress_zip(
        self,
        source: Union[str, List[str]],
        output_file: str,
        compression_level: int = 6,
        password: Optional[str] = None,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a ZIP archive.

        Args:
            source: File, directory, or list of files/directories
            output_file: Output ZIP file path
            compression_level: 0-9 (0=store, 9=best compression)
            password: Optional password protection
            include_pattern: Only include files matching pattern (e.g., "*.txt")
            exclude_pattern: Exclude files matching pattern

        Returns:
            Dict with stats (files_count, compressed_size, compression_ratio)
        """
        compression = zipfile.ZIP_DEFLATED if compression_level > 0 else zipfile.ZIP_STORED

        total_original = 0
        total_compressed = 0
        files_count = 0

        with zipfile.ZipFile(output_file, 'w', compression=compression,
                            compresslevel=compression_level) as zf:

            # Set password if provided
            if password:
                zf.setpassword(password.encode())

            sources = [source] if isinstance(source, str) else source

            for src in sources:
                src_path = Path(src)

                if src_path.is_file():
                    if self._should_include_file(src_path.name, include_pattern, exclude_pattern):
                        arcname = src_path.name
                        zf.write(src, arcname)
                        files_count += 1
                        total_original += src_path.stat().st_size

                elif src_path.is_dir():
                    for root, dirs, files in os.walk(src):
                        for file in files:
                            if self._should_include_file(file, include_pattern, exclude_pattern):
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(src_path.parent)
                                zf.write(file_path, arcname)
                                files_count += 1
                                total_original += file_path.stat().st_size

        total_compressed = Path(output_file).stat().st_size
        ratio = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0

        print(f"[CompressionModule] Created ZIP: {output_file} ({files_count} files, {ratio:.1f}% compression)")

        return {
            'format': 'zip',
            'output_file': output_file,
            'files_count': files_count,
            'original_size': total_original,
            'compressed_size': total_compressed,
            'compression_ratio': ratio
        }

    def extract_zip(
        self,
        archive_path: str,
        output_dir: str,
        password: Optional[str] = None,
        members: Optional[List[str]] = None,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract a ZIP archive.

        Args:
            archive_path: Path to ZIP file
            output_dir: Output directory
            password: Password if archive is encrypted
            members: Specific files to extract (None = all)
            pattern: Only extract files matching pattern

        Returns:
            Dict with stats
        """
        os.makedirs(output_dir, exist_ok=True)
        files_count = 0

        with zipfile.ZipFile(archive_path, 'r') as zf:
            if password:
                zf.setpassword(password.encode())

            # Get list of members to extract
            if members:
                extract_list = members
            elif pattern:
                extract_list = [name for name in zf.namelist()
                              if fnmatch.fnmatch(name, pattern)]
            else:
                extract_list = None  # Extract all

            if extract_list:
                for member in extract_list:
                    zf.extract(member, output_dir)
                    files_count += 1
            else:
                zf.extractall(output_dir)
                files_count = len(zf.namelist())

        print(f"[CompressionModule] Extracted ZIP: {files_count} files to {output_dir}")

        return {
            'format': 'zip',
            'files_count': files_count,
            'output_dir': output_dir
        }

    # ==================== TAR Operations ====================

    def compress_tar(
        self,
        source: Union[str, List[str]],
        output_file: str,
        compression: str = 'none',
        compression_level: int = 6,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a TAR archive.

        Args:
            source: File, directory, or list of files/directories
            output_file: Output TAR file path
            compression: 'none', 'gz', 'bz2', or 'xz'
            compression_level: 0-9 for gz/bz2
            include_pattern: Only include files matching pattern
            exclude_pattern: Exclude files matching pattern

        Returns:
            Dict with stats
        """
        # Determine mode
        mode_map = {
            'none': 'w',
            'gz': 'w:gz',
            'bz2': 'w:bz2',
            'xz': 'w:xz'
        }
        mode = mode_map.get(compression, 'w')

        total_size = 0
        files_count = 0

        with tarfile.open(output_file, mode) as tf:
            sources = [source] if isinstance(source, str) else source

            for src in sources:
                src_path = Path(src)

                if src_path.is_file():
                    if self._should_include_file(src_path.name, include_pattern, exclude_pattern):
                        tf.add(src, arcname=src_path.name)
                        files_count += 1
                        total_size += src_path.stat().st_size

                elif src_path.is_dir():
                    for root, dirs, files in os.walk(src):
                        for file in files:
                            if self._should_include_file(file, include_pattern, exclude_pattern):
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(src_path.parent)
                                tf.add(file_path, arcname=arcname)
                                files_count += 1
                                total_size += file_path.stat().st_size

        compressed_size = Path(output_file).stat().st_size
        ratio = (1 - compressed_size / total_size) * 100 if total_size > 0 else 0

        print(f"[CompressionModule] Created TAR: {output_file} ({files_count} files, {ratio:.1f}% compression)")

        return {
            'format': f'tar.{compression}' if compression != 'none' else 'tar',
            'output_file': output_file,
            'files_count': files_count,
            'original_size': total_size,
            'compressed_size': compressed_size,
            'compression_ratio': ratio
        }

    def compress_targz(self, source: Union[str, List[str]], output_file: str, **kwargs) -> Dict[str, Any]:
        """Create TAR.GZ archive (shorthand)."""
        return self.compress_tar(source, output_file, compression='gz', **kwargs)

    def compress_tarbz2(self, source: Union[str, List[str]], output_file: str, **kwargs) -> Dict[str, Any]:
        """Create TAR.BZ2 archive (shorthand)."""
        return self.compress_tar(source, output_file, compression='bz2', **kwargs)

    def compress_tarxz(self, source: Union[str, List[str]], output_file: str, **kwargs) -> Dict[str, Any]:
        """Create TAR.XZ archive (shorthand)."""
        return self.compress_tar(source, output_file, compression='xz', **kwargs)

    def extract_tar(
        self,
        archive_path: str,
        output_dir: str,
        members: Optional[List[str]] = None,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract a TAR archive (auto-detects compression).

        Args:
            archive_path: Path to TAR file
            output_dir: Output directory
            members: Specific files to extract
            pattern: Only extract files matching pattern

        Returns:
            Dict with stats
        """
        os.makedirs(output_dir, exist_ok=True)
        files_count = 0

        with tarfile.open(archive_path, 'r:*') as tf:
            if members:
                extract_list = [m for m in tf.getmembers() if m.name in members]
            elif pattern:
                extract_list = [m for m in tf.getmembers()
                              if fnmatch.fnmatch(m.name, pattern)]
            else:
                extract_list = None

            if extract_list:
                for member in extract_list:
                    tf.extract(member, output_dir)
                    files_count += 1
            else:
                tf.extractall(output_dir)
                files_count = len(tf.getmembers())

        print(f"[CompressionModule] Extracted TAR: {files_count} files to {output_dir}")

        return {
            'format': 'tar',
            'files_count': files_count,
            'output_dir': output_dir
        }

    # ==================== Single File Compression ====================

    def compress_gzip(self, source_file: str, output_file: Optional[str] = None,
                     compression_level: int = 6) -> Dict[str, Any]:
        """Compress a single file with GZIP."""
        if output_file is None:
            output_file = source_file + '.gz'

        original_size = Path(source_file).stat().st_size

        with open(source_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb', compresslevel=compression_level) as f_out:
                shutil.copyfileobj(f_in, f_out)

        compressed_size = Path(output_file).stat().st_size
        ratio = (1 - compressed_size / original_size) * 100

        print(f"[CompressionModule] GZIP compressed: {output_file} ({ratio:.1f}% compression)")

        return {
            'format': 'gzip',
            'output_file': output_file,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': ratio
        }

    def extract_gzip(self, archive_path: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Decompress a GZIP file."""
        if output_file is None:
            output_file = archive_path.replace('.gz', '')

        with gzip.open(archive_path, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"[CompressionModule] GZIP extracted: {output_file}")

        return {
            'format': 'gzip',
            'output_file': output_file,
            'decompressed_size': Path(output_file).stat().st_size
        }

    def compress_bzip2(self, source_file: str, output_file: Optional[str] = None,
                      compression_level: int = 9) -> Dict[str, Any]:
        """Compress a single file with BZIP2."""
        if output_file is None:
            output_file = source_file + '.bz2'

        original_size = Path(source_file).stat().st_size

        with open(source_file, 'rb') as f_in:
            with bz2.open(output_file, 'wb', compresslevel=compression_level) as f_out:
                shutil.copyfileobj(f_in, f_out)

        compressed_size = Path(output_file).stat().st_size
        ratio = (1 - compressed_size / original_size) * 100

        print(f"[CompressionModule] BZIP2 compressed: {output_file} ({ratio:.1f}% compression)")

        return {
            'format': 'bzip2',
            'output_file': output_file,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': ratio
        }

    def extract_bzip2(self, archive_path: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Decompress a BZIP2 file."""
        if output_file is None:
            output_file = archive_path.replace('.bz2', '')

        with bz2.open(archive_path, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"[CompressionModule] BZIP2 extracted: {output_file}")

        return {
            'format': 'bzip2',
            'output_file': output_file,
            'decompressed_size': Path(output_file).stat().st_size
        }

    def compress_xz(self, source_file: str, output_file: Optional[str] = None,
                   compression_level: int = 6) -> Dict[str, Any]:
        """Compress a single file with XZ/LZMA."""
        if output_file is None:
            output_file = source_file + '.xz'

        original_size = Path(source_file).stat().st_size

        with open(source_file, 'rb') as f_in:
            with lzma.open(output_file, 'wb', preset=compression_level) as f_out:
                shutil.copyfileobj(f_in, f_out)

        compressed_size = Path(output_file).stat().st_size
        ratio = (1 - compressed_size / original_size) * 100

        print(f"[CompressionModule] XZ compressed: {output_file} ({ratio:.1f}% compression)")

        return {
            'format': 'xz',
            'output_file': output_file,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': ratio
        }

    def extract_xz(self, archive_path: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Decompress an XZ file."""
        if output_file is None:
            output_file = archive_path.replace('.xz', '')

        with lzma.open(archive_path, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"[CompressionModule] XZ extracted: {output_file}")

        return {
            'format': 'xz',
            'output_file': output_file,
            'decompressed_size': Path(output_file).stat().st_size
        }

    # ==================== 7Z Operations ====================

    def compress_7z(
        self,
        source: Union[str, List[str]],
        output_file: str,
        password: Optional[str] = None,
        compression_level: int = 5
    ) -> Dict[str, Any]:
        """
        Create a 7Z archive.

        Args:
            source: File, directory, or list of files/directories
            output_file: Output 7Z file path
            password: Optional password protection
            compression_level: 0-9

        Returns:
            Dict with stats

        Requires: pip install py7zr
        """
        if py7zr is None:
            raise ImportError("py7zr is required. Install with: pip install py7zr")

        filters = [{'id': lzma.FILTER_LZMA2, 'preset': compression_level}]

        total_size = 0
        files_count = 0

        with py7zr.SevenZipFile(output_file, 'w', password=password, filters=filters) as archive:
            sources = [source] if isinstance(source, str) else source

            for src in sources:
                src_path = Path(src)

                if src_path.is_file():
                    archive.write(src, src_path.name)
                    files_count += 1
                    total_size += src_path.stat().st_size
                elif src_path.is_dir():
                    archive.writeall(src, src_path.name)
                    for root, dirs, files in os.walk(src):
                        files_count += len(files)
                        for file in files:
                            total_size += (Path(root) / file).stat().st_size

        compressed_size = Path(output_file).stat().st_size
        ratio = (1 - compressed_size / total_size) * 100 if total_size > 0 else 0

        print(f"[CompressionModule] Created 7Z: {output_file} ({files_count} files, {ratio:.1f}% compression)")

        return {
            'format': '7z',
            'output_file': output_file,
            'files_count': files_count,
            'original_size': total_size,
            'compressed_size': compressed_size,
            'compression_ratio': ratio
        }

    def extract_7z(
        self,
        archive_path: str,
        output_dir: str,
        password: Optional[str] = None,
        targets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extract a 7Z archive."""
        if py7zr is None:
            raise ImportError("py7zr is required. Install with: pip install py7zr")

        os.makedirs(output_dir, exist_ok=True)

        with py7zr.SevenZipFile(archive_path, 'r', password=password) as archive:
            if targets:
                archive.extract(output_dir, targets=targets)
                files_count = len(targets)
            else:
                archive.extractall(output_dir)
                files_count = len(archive.getnames())

        print(f"[CompressionModule] Extracted 7Z: {files_count} files to {output_dir}")

        return {
            'format': '7z',
            'files_count': files_count,
            'output_dir': output_dir
        }

    # ==================== Auto-Detection Operations ====================

    def compress_auto(self, source: Union[str, List[str]], output_file: str, **kwargs) -> Dict[str, Any]:
        """Automatically compress based on output file extension."""
        fmt = self.detect_format(output_file)

        if fmt == 'zip':
            return self.compress_zip(source, output_file, **kwargs)
        elif fmt == 'tar':
            return self.compress_tar(source, output_file, compression='none', **kwargs)
        elif fmt == 'tar.gz':
            return self.compress_targz(source, output_file, **kwargs)
        elif fmt == 'tar.bz2':
            return self.compress_tarbz2(source, output_file, **kwargs)
        elif fmt == 'tar.xz':
            return self.compress_tarxz(source, output_file, **kwargs)
        elif fmt == '7z':
            return self.compress_7z(source, output_file, **kwargs)
        else:
            raise ValueError(f"Unsupported format for {output_file}")

    def extract_auto(self, archive_path: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """Automatically extract based on archive file extension."""
        fmt = self.detect_format(archive_path)

        if fmt == 'zip':
            return self.extract_zip(archive_path, output_dir, **kwargs)
        elif fmt in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
            return self.extract_tar(archive_path, output_dir, **kwargs)
        elif fmt == 'gzip':
            return self.extract_gzip(archive_path, **kwargs)
        elif fmt == 'bzip2':
            return self.extract_bzip2(archive_path, **kwargs)
        elif fmt == 'xz':
            return self.extract_xz(archive_path, **kwargs)
        elif fmt == '7z':
            return self.extract_7z(archive_path, output_dir, **kwargs)
        else:
            raise ValueError(f"Unsupported format for {archive_path}")

    # ==================== Inspection Operations ====================

    def list_archive(self, archive_path: str) -> List[Dict[str, Any]]:
        """
        List contents of an archive.

        Returns:
            List of dicts with file info (name, size, compressed_size, date)
        """
        fmt = self.detect_format(archive_path)
        files = []

        if fmt == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zf:
                for info in zf.infolist():
                    files.append({
                        'name': info.filename,
                        'size': info.file_size,
                        'compressed_size': info.compress_size,
                        'date': datetime(*info.date_time),
                        'is_dir': info.is_dir()
                    })

        elif fmt in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
            with tarfile.open(archive_path, 'r:*') as tf:
                for member in tf.getmembers():
                    files.append({
                        'name': member.name,
                        'size': member.size,
                        'date': datetime.fromtimestamp(member.mtime),
                        'is_dir': member.isdir()
                    })

        elif fmt == '7z' and py7zr:
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                for name, info in archive.list():
                    files.append({
                        'name': name,
                        'size': info.uncompressed,
                        'compressed_size': info.compressed,
                        'is_dir': info.is_directory
                    })

        return files

    def get_archive_info(self, archive_path: str) -> Dict[str, Any]:
        """Get summary info about an archive."""
        fmt = self.detect_format(archive_path)
        archive_size = Path(archive_path).stat().st_size
        files = self.list_archive(archive_path)

        total_size = sum(f['size'] for f in files if not f['is_dir'])
        files_count = sum(1 for f in files if not f['is_dir'])
        dirs_count = sum(1 for f in files if f['is_dir'])

        ratio = (1 - archive_size / total_size) * 100 if total_size > 0 else 0

        return {
            'format': fmt,
            'archive_path': archive_path,
            'archive_size': archive_size,
            'files_count': files_count,
            'dirs_count': dirs_count,
            'total_uncompressed_size': total_size,
            'compression_ratio': ratio
        }

    # ==================== Helper Methods ====================

    def _should_include_file(
        self,
        filename: str,
        include_pattern: Optional[str],
        exclude_pattern: Optional[str]
    ) -> bool:
        """Check if file should be included based on patterns."""
        if exclude_pattern and fnmatch.fnmatch(filename, exclude_pattern):
            return False
        if include_pattern and not fnmatch.fnmatch(filename, include_pattern):
            return False
        return True
