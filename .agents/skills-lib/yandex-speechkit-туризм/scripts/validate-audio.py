#!/usr/bin/env python3
"""
Audio Validator for Yandex SpeechKit
Validates audio files before sending to transcription API
"""

import argparse
import sys
from pathlib import Path
from typing import Tuple, List, Dict
import subprocess
import json

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    print("Installing required package: rich")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

console = Console()

# Yandex SpeechKit limits
SYNC_API_MAX_SIZE = 1 * 1024 * 1024  # 1 MB
ASYNC_API_MAX_SIZE = 1024 * 1024 * 1024  # 1 GB
STREAMING_MAX_SIZE = None  # No limit for streaming
MAX_DURATION_WARNING = 30  # seconds
RECOMMENDED_SAMPLE_RATE = 48000
SUPPORTED_FORMATS = ['ogg', 'opus', 'mp3', 'wav', 'pcm', 'flac']


def get_audio_info(file_path: Path) -> Dict:
    """Get audio file information using ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)

        # Extract audio stream info
        audio_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'audio'), None)

        if not audio_stream:
            return None

        format_info = data.get('format', {})

        return {
            'codec': audio_stream.get('codec_name'),
            'sample_rate': int(audio_stream.get('sample_rate', 0)),
            'channels': int(audio_stream.get('channels', 0)),
            'duration': float(format_info.get('duration', 0)),
            'bitrate': int(format_info.get('bit_rate', 0)),
            'size': int(format_info.get('size', 0))
        }
    except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
        # ffprobe not available, use basic file info
        return {
            'codec': None,
            'sample_rate': None,
            'channels': None,
            'duration': None,
            'bitrate': None,
            'size': file_path.stat().st_size
        }


def validate_file(file_path: Path, api_type: str = 'sync') -> Dict:
    """
    Validate audio file for SpeechKit API

    Args:
        file_path: Path to audio file
        api_type: 'sync', 'async', or 'streaming'

    Returns:
        Dict with validation results
    """
    results = {
        'file': file_path.name,
        'path': str(file_path),
        'status': 'unknown',
        'issues': [],
        'warnings': [],
        'recommendations': [],
        'info': {}
    }

    # Check file exists
    if not file_path.exists():
        results['status'] = 'error'
        results['issues'].append(f"File not found: {file_path}")
        return results

    # Check file extension
    extension = file_path.suffix.lower().lstrip('.')
    if extension not in SUPPORTED_FORMATS:
        results['issues'].append(
            f"Unsupported format: {extension}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Get audio info
    info = get_audio_info(file_path)
    if not info:
        results['issues'].append("Cannot read audio file metadata")
        results['status'] = 'error'
        return results

    results['info'] = info

    # Validate file size
    file_size = info['size']
    if api_type == 'sync':
        if file_size > SYNC_API_MAX_SIZE:
            results['issues'].append(
                f"File too large for Sync API: {file_size / 1024 / 1024:.2f} MB > 1 MB"
            )
            results['recommendations'].append("Use Async API for large files")
    elif api_type == 'async':
        if file_size > ASYNC_API_MAX_SIZE:
            results['issues'].append(
                f"File too large: {file_size / 1024 / 1024 / 1024:.2f} GB > 1 GB"
            )

    # Validate duration
    if info['duration']:
        if info['duration'] > MAX_DURATION_WARNING and api_type == 'sync':
            results['warnings'].append(
                f"Long audio: {info['duration']:.1f}s. Sync API may timeout."
            )
            results['recommendations'].append("Consider using Async API for audio >30 sec")

    # Validate sample rate
    if info['sample_rate']:
        if extension == 'opus' and info['sample_rate'] != RECOMMENDED_SAMPLE_RATE:
            results['warnings'].append(
                f"Sample rate {info['sample_rate']} Hz. Recommended for Opus: {RECOMMENDED_SAMPLE_RATE} Hz"
            )

        if info['sample_rate'] < 8000:
            results['warnings'].append(
                f"Low sample rate: {info['sample_rate']} Hz. May affect quality."
            )

    # Validate channels
    if info['channels']:
        if info['channels'] > 2:
            results['warnings'].append(
                f"Multi-channel audio: {info['channels']} channels. Will be converted to mono."
            )

    # Determine overall status
    if results['issues']:
        results['status'] = 'error'
    elif results['warnings']:
        results['status'] = 'warning'
    else:
        results['status'] = 'success'

    return results


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if not seconds:
        return "N/A"

    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def print_validation_result(result: Dict):
    """Print validation result with rich formatting"""
    # Status icon
    if result['status'] == 'success':
        icon = "✅"
        color = "green"
    elif result['status'] == 'warning':
        icon = "⚠️"
        color = "yellow"
    else:
        icon = "❌"
        color = "red"

    # Header
    console.print(f"\n{icon} [{color}]{result['file']}[/{color}]")

    # File info table
    if result['info']:
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Property", style="cyan")
        table.add_column("Value")

        info = result['info']

        if info['codec']:
            table.add_row("Format", info['codec'].upper())

        table.add_row("Size", format_size(info['size']))

        if info['duration']:
            table.add_row("Duration", format_duration(info['duration']))

        if info['sample_rate']:
            table.add_row("Sample Rate", f"{info['sample_rate']} Hz")

        if info['channels']:
            table.add_row("Channels", str(info['channels']))

        if info['bitrate']:
            table.add_row("Bitrate", f"{info['bitrate'] // 1000} kbps")

        console.print(table)

    # Issues
    if result['issues']:
        console.print("\n[red]❌ Issues:[/red]")
        for issue in result['issues']:
            console.print(f"  • {issue}")

    # Warnings
    if result['warnings']:
        console.print("\n[yellow]⚠️  Warnings:[/yellow]")
        for warning in result['warnings']:
            console.print(f"  • {warning}")

    # Recommendations
    if result['recommendations']:
        console.print("\n[blue]💡 Recommendations:[/blue]")
        for rec in result['recommendations']:
            console.print(f"  • {rec}")


def validate_batch(files: List[Path], api_type: str) -> List[Dict]:
    """Validate multiple audio files"""
    results = []

    with console.status("[bold green]Validating files...") as status:
        for i, file_path in enumerate(files, 1):
            status.update(f"[bold green]Validating {i}/{len(files)}: {file_path.name}")
            result = validate_file(file_path, api_type)
            results.append(result)

    return results


def print_summary(results: List[Dict]):
    """Print validation summary"""
    success_count = sum(1 for r in results if r['status'] == 'success')
    warning_count = sum(1 for r in results if r['status'] == 'warning')
    error_count = sum(1 for r in results if r['status'] == 'error')

    # Summary table
    table = Table(title="Validation Summary", show_header=True)
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Percentage", justify="right")

    total = len(results)

    table.add_row(
        "[green]✅ Success[/green]",
        str(success_count),
        f"{success_count / total * 100:.1f}%"
    )
    table.add_row(
        "[yellow]⚠️  Warning[/yellow]",
        str(warning_count),
        f"{warning_count / total * 100:.1f}%"
    )
    table.add_row(
        "[red]❌ Error[/red]",
        str(error_count),
        f"{error_count / total * 100:.1f}%"
    )

    console.print("\n")
    console.print(table)

    # Total size and duration
    total_size = sum(r['info'].get('size', 0) for r in results)
    total_duration = sum(r['info'].get('duration', 0) or 0 for r in results)

    console.print(f"\n[bold]Total Size:[/bold] {format_size(total_size)}")
    if total_duration:
        console.print(f"[bold]Total Duration:[/bold] {format_duration(total_duration)}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate audio files for Yandex SpeechKit API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single file for Sync API
  python validate-audio.py audio.ogg

  # Validate for Async API
  python validate-audio.py audio.mp3 --api async

  # Validate directory
  python validate-audio.py ./audio_files/ --recursive

  # Validate with specific extensions
  python validate-audio.py ./audio_files/ -r --ext ogg mp3
        """
    )

    parser.add_argument(
        'path',
        type=str,
        help='Audio file or directory to validate'
    )

    parser.add_argument(
        '--api',
        choices=['sync', 'async', 'streaming'],
        default='sync',
        help='Target API type (default: sync)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively search directories'
    )

    parser.add_argument(
        '--ext',
        nargs='+',
        default=SUPPORTED_FORMATS,
        help=f'File extensions to check (default: {" ".join(SUPPORTED_FORMATS)})'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    parser.add_argument(
        '--only-errors',
        action='store_true',
        help='Show only files with errors'
    )

    args = parser.parse_args()

    # Collect files
    path = Path(args.path)
    files = []

    if path.is_file():
        files = [path]
    elif path.is_dir():
        pattern = '**/*' if args.recursive else '*'
        for ext in args.ext:
            files.extend(path.glob(f"{pattern}.{ext}"))
    else:
        console.print(f"[red]Error: Path not found: {path}[/red]")
        return 1

    if not files:
        console.print(f"[yellow]No audio files found in {path}[/yellow]")
        return 0

    # Validate files
    console.print(f"[bold]Validating {len(files)} file(s) for {args.api.upper()} API[/bold]\n")

    results = validate_batch(files, args.api)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            if args.only_errors and result['status'] != 'error':
                continue
            print_validation_result(result)

        if len(results) > 1:
            print_summary(results)

    # Exit code
    error_count = sum(1 for r in results if r['status'] == 'error')
    return 1 if error_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
