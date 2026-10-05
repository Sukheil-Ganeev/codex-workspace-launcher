#!/usr/bin/env python3
"""
Batch Transcription for Yandex SpeechKit
Process multiple audio files in parallel with progress tracking
"""

import argparse
import sys
import json
import csv
import base64
import time
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging

try:
    import requests
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.logging import RichHandler
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "rich"])
    import requests
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.logging import RichHandler

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


class SpeechKitTranscriber:
    """Yandex SpeechKit transcription client"""

    SYNC_API_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

    def __init__(self, api_key: str, folder_id: str, lang: str = "ru-RU",
                 max_retries: int = 3, retry_delay: float = 1.0):
        self.api_key = api_key
        self.folder_id = folder_id
        self.lang = lang
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def transcribe_file(self, file_path: Path) -> Dict:
        """
        Transcribe single audio file

        Returns:
            Dict with transcription result
        """
        result = {
            'file': str(file_path),
            'filename': file_path.name,
            'status': 'pending',
            'text': None,
            'error': None,
            'attempts': 0,
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Read and encode audio
            with open(file_path, 'rb') as f:
                audio_data = f.read()

            # Determine format
            ext = file_path.suffix.lower().lstrip('.')
            if ext == 'ogg':
                format_type = 'oggopus'
            elif ext == 'mp3':
                format_type = 'lpcm'
            else:
                format_type = 'lpcm'

            # Prepare request
            headers = {
                'Authorization': f'Api-Key {self.api_key}'
            }

            params = {
                'lang': self.lang,
                'folderId': self.folder_id,
                'format': format_type
            }

            # Retry loop
            for attempt in range(1, self.max_retries + 1):
                result['attempts'] = attempt

                try:
                    response = requests.post(
                        self.SYNC_API_URL,
                        headers=headers,
                        params=params,
                        data=audio_data,
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        result['status'] = 'success'
                        result['text'] = data.get('result', '')
                        return result

                    elif response.status_code == 429:  # Rate limit
                        if attempt < self.max_retries:
                            time.sleep(self.retry_delay * attempt)
                            continue
                        else:
                            result['status'] = 'error'
                            result['error'] = 'Rate limit exceeded'
                            return result

                    else:
                        result['status'] = 'error'
                        result['error'] = f"HTTP {response.status_code}: {response.text}"
                        return result

                except requests.exceptions.Timeout:
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * attempt)
                        continue
                    else:
                        result['status'] = 'error'
                        result['error'] = 'Request timeout'
                        return result

                except requests.exceptions.RequestException as e:
                    result['status'] = 'error'
                    result['error'] = str(e)
                    return result

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result


def collect_audio_files(input_path: Path, recursive: bool = False,
                       extensions: List[str] = None) -> List[Path]:
    """Collect audio files from input path"""
    if extensions is None:
        extensions = ['ogg', 'opus', 'mp3', 'wav']

    files = []

    if input_path.is_file():
        if input_path.suffix.lower().lstrip('.') in extensions:
            files.append(input_path)
    elif input_path.is_dir():
        pattern = '**/*' if recursive else '*'
        for ext in extensions:
            files.extend(input_path.glob(f"{pattern}.{ext}"))

    return sorted(files)


def transcribe_batch(transcriber: SpeechKitTranscriber, files: List[Path],
                    max_workers: int = 4) -> List[Dict]:
    """
    Transcribe multiple files in parallel

    Args:
        transcriber: SpeechKitTranscriber instance
        files: List of audio files
        max_workers: Number of parallel workers

    Returns:
        List of transcription results
    """
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeRemainingColumn(),
        console=console
    ) as progress:

        task = progress.add_task("[cyan]Transcribing...", total=len(files))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(transcriber.transcribe_file, file): file
                for file in files
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                progress.advance(task)

    return results


def export_csv(results: List[Dict], output_file: Path):
    """Export results to CSV"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'filename', 'status', 'text', 'error', 'attempts', 'timestamp'
        ])
        writer.writeheader()

        for result in results:
            writer.writerow({
                'filename': result['filename'],
                'status': result['status'],
                'text': result.get('text', ''),
                'error': result.get('error', ''),
                'attempts': result['attempts'],
                'timestamp': result['timestamp']
            })


def export_json(results: List[Dict], output_file: Path):
    """Export results to JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def export_txt(results: List[Dict], output_file: Path):
    """Export transcriptions to plain text"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            if result['status'] == 'success' and result['text']:
                f.write(f"=== {result['filename']} ===\n")
                f.write(f"{result['text']}\n\n")


def print_summary(results: List[Dict]):
    """Print transcription summary"""
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = sum(1 for r in results if r['status'] == 'error')
    total = len(results)

    # Summary table
    table = Table(title="Transcription Summary", show_header=True)
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Percentage", justify="right")

    table.add_row(
        "[green]✅ Success[/green]",
        str(success_count),
        f"{success_count / total * 100:.1f}%"
    )
    table.add_row(
        "[red]❌ Error[/red]",
        str(error_count),
        f"{error_count / total * 100:.1f}%"
    )

    console.print("\n")
    console.print(table)

    # Show errors
    if error_count > 0:
        console.print("\n[red]Errors:[/red]")
        for result in results:
            if result['status'] == 'error':
                console.print(f"  • {result['filename']}: {result['error']}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch transcription with Yandex SpeechKit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe single file
  python batch-transcribe.py -i audio.ogg -o results.json --api-key YOUR_KEY --folder-id YOUR_FOLDER

  # Transcribe directory
  python batch-transcribe.py -i ./audio/ -o results.csv --recursive

  # Custom language and parallel processing
  python batch-transcribe.py -i ./audio/ -o results.json --lang en-US --workers 8

  # Export as plain text
  python batch-transcribe.py -i ./audio/ -o transcripts.txt --format txt
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Input audio file or directory'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Output file (CSV, JSON, or TXT)'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        help='Yandex Cloud API key (or set YANDEX_API_KEY env var)'
    )

    parser.add_argument(
        '--folder-id',
        type=str,
        help='Yandex Cloud folder ID (or set YANDEX_FOLDER_ID env var)'
    )

    parser.add_argument(
        '--lang',
        type=str,
        default='ru-RU',
        help='Recognition language (default: ru-RU)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively search directories'
    )

    parser.add_argument(
        '--ext',
        nargs='+',
        default=['ogg', 'opus', 'mp3', 'wav'],
        help='File extensions to process'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )

    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Max retry attempts per file (default: 3)'
    )

    parser.add_argument(
        '--retry-delay',
        type=float,
        default=1.0,
        help='Delay between retries in seconds (default: 1.0)'
    )

    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'txt'],
        help='Output format (auto-detected from file extension)'
    )

    args = parser.parse_args()

    # Get API credentials
    import os
    api_key = args.api_key or os.getenv('YANDEX_API_KEY')
    folder_id = args.folder_id or os.getenv('YANDEX_FOLDER_ID')

    if not api_key or not folder_id:
        console.print("[red]Error: API key and folder ID are required[/red]")
        console.print("Set via --api-key/--folder-id or YANDEX_API_KEY/YANDEX_FOLDER_ID env vars")
        return 1

    # Collect files
    input_path = Path(args.input)
    files = collect_audio_files(input_path, args.recursive, args.ext)

    if not files:
        console.print(f"[yellow]No audio files found in {input_path}[/yellow]")
        return 0

    console.print(f"[bold]Found {len(files)} file(s) to transcribe[/bold]\n")

    # Create transcriber
    transcriber = SpeechKitTranscriber(
        api_key=api_key,
        folder_id=folder_id,
        lang=args.lang,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay
    )

    # Transcribe
    results = transcribe_batch(transcriber, files, args.workers)

    # Determine output format
    output_path = Path(args.output)
    output_format = args.format or output_path.suffix.lower().lstrip('.')

    if output_format not in ['csv', 'json', 'txt']:
        output_format = 'json'  # Default

    # Export results
    if output_format == 'csv':
        export_csv(results, output_path)
    elif output_format == 'json':
        export_json(results, output_path)
    elif output_format == 'txt':
        export_txt(results, output_path)

    console.print(f"\n[green]✅ Results saved to {output_path}[/green]")

    # Print summary
    print_summary(results)

    return 0


if __name__ == '__main__':
    sys.exit(main())
