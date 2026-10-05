#!/usr/bin/env python3
"""Benchmark different Yandex SpeechKit models and languages"""
import argparse, sys, json, time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict
import requests

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
except ImportError:
    print("ERROR: pip install rich requests")
    sys.exit(1)

console = Console()

@dataclass
class BenchmarkResult:
    file_name: str
    model: str
    language: str
    duration_sec: float
    processing_time_sec: float
    text: str
    cost_rub: float
    speed_ratio: float  # processing_time / audio_duration
    status: str
    error: str = None

class YandexBenchmark:
    SYNC_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    
    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id
        self.session = requests.Session()

    def transcribe(self, file_path: Path, lang: str) -> BenchmarkResult:
        start = time.time()
        
        headers = {"Authorization": f"Api-Key {self.api_key}"}
        params = {"folderId": self.folder_id, "lang": lang}
        
        try:
            with open(file_path, "rb") as f:
                response = self.session.post(self.SYNC_URL, headers=headers, params=params, data=f, timeout=30)
            
            processing_time = time.time() - start
            
            # Calculate cost (0.12 RUB per 15 seconds)
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(file_path))
            duration_sec = len(audio) / 1000.0
            units = int(duration_sec / 15) + (1 if duration_sec % 15 != 0 else 0)
            cost_rub = units * 0.12
            speed_ratio = processing_time / duration_sec if duration_sec > 0 else 0
            
            if response.status_code == 200:
                result = response.json()
                return BenchmarkResult(
                    file_name=file_path.name,
                    model="Sync API",
                    language=lang,
                    duration_sec=duration_sec,
                    processing_time_sec=processing_time,
                    text=result.get("result", ""),
                    cost_rub=cost_rub,
                    speed_ratio=speed_ratio,
                    status="success"
                )
            else:
                return BenchmarkResult(
                    file_name=file_path.name, model="Sync API", language=lang,
                    duration_sec=0, processing_time_sec=processing_time, text="",
                    cost_rub=0, speed_ratio=0, status="error", error=response.text
                )
        except Exception as e:
            return BenchmarkResult(
                file_name=file_path.name, model="Sync API", language=lang,
                duration_sec=0, processing_time_sec=time.time() - start, text="",
                cost_rub=0, speed_ratio=0, status="error", error=str(e)
            )

    def run_benchmark(self, files: List[Path], languages: List[str]) -> List[BenchmarkResult]:
        results = []
        total = len(files) * len(languages)
        
        console.print(f"[cyan]Running benchmark: {len(files)} files x {len(languages)} languages = {total} tests[/cyan]
")
        
        for file_path in track(files, description="Processing files"):
            for lang in languages:
                console.print(f"  Testing {file_path.name} with {lang}...")
                result = self.transcribe(file_path, lang)
                results.append(result)
        
        return results

def print_results(results: List[BenchmarkResult]):
    # Summary statistics
    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "error"]
    
    console.print(f"
[green]Successful: {len(successful)}[/green] | [red]Failed: {len(failed)}[/red]
")
    
    # Results table
    table = Table(title="Benchmark Results")
    table.add_column("File", style="cyan")
    table.add_column("Language", style="yellow")
    table.add_column("Duration", justify="right")
    table.add_column("Process Time", justify="right")
    table.add_column("Speed Ratio", justify="right")
    table.add_column("Cost (RUB)", justify="right", style="green")
    table.add_column("Status")
    
    for r in results:
        status_icon = "[green]OK[/green]" if r.status == "success" else "[red]FAIL[/red]"
        table.add_row(
            r.file_name,
            r.language,
            f"{r.duration_sec:.1f}s" if r.duration_sec > 0 else "-",
            f"{r.processing_time_sec:.2f}s",
            f"{r.speed_ratio:.2f}x" if r.speed_ratio > 0 else "-",
            f"{r.cost_rub:.2f}" if r.cost_rub > 0 else "-",
            status_icon
        )
    
    console.print(table)
    
    # Statistics
    if successful:
        avg_speed = sum(r.speed_ratio for r in successful) / len(successful)
        avg_cost = sum(r.cost_rub for r in successful) / len(successful)
        total_cost = sum(r.cost_rub for r in successful)
        
        console.print(f"
[cyan]Average speed ratio:[/cyan] {avg_speed:.2f}x")
        console.print(f"[cyan]Average cost per file:[/cyan] {avg_cost:.2f} RUB")
        console.print(f"[cyan]Total cost:[/cyan] {total_cost:.2f} RUB")

def main():
    parser = argparse.ArgumentParser(description="Benchmark Yandex SpeechKit")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    parser.add_argument("--api-key", type=str, help="Yandex API key")
    parser.add_argument("--folder-id", type=str, help="Yandex folder ID")
    parser.add_argument("--languages", "-l", nargs="+", default=["ru-RU"], help="Languages to test")
    args = parser.parse_args()
    
    # Get credentials
    import os
    api_key = args.api_key or os.getenv("YANDEX_API_KEY")
    folder_id = args.folder_id or os.getenv("YANDEX_FOLDER_ID")
    
    if not api_key or not folder_id:
        console.print("[red]Error: API key and folder ID required[/red]")
        sys.exit(1)
    
    # Find audio files
    audio_files = []
    for ext in [".ogg", ".mp3", ".wav"]:
        audio_files.extend(args.input.glob(f"*{ext}"))
    
    if not audio_files:
        console.print("[yellow]No audio files found[/yellow]")
        sys.exit(0)
    
    # Run benchmark
    benchmark = YandexBenchmark(api_key, folder_id)
    results = benchmark.run_benchmark(audio_files, args.languages)
    
    # Print results
    print_results(results)
    
    # Export to JSON
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        console.print(f"
[green]Results saved to: {args.output}[/green]")

if __name__ == "__main__":
    main()
