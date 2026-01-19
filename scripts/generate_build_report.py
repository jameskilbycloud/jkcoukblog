import json
import subprocess
from pathlib import Path
from datetime import datetime

def generate_build_metrics(output_dir, duration, urls_processed, assets_downloaded, error_count=0):
    """Generate comprehensive build metrics
    
    Args:
        output_dir: Path to the output directory
        duration: Generation duration in seconds
        urls_processed: Number of URLs processed
        assets_downloaded: Number of assets downloaded
        error_count: Number of errors encountered (default: 0)
    
    Returns:
        dict: Build metrics
    """
    output_path = Path(output_dir)
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
    
    # Get git commit hash
    try:
        git_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                            stderr=subprocess.DEVNULL).decode('utf-8').strip()
    except:
        git_commit = 'unknown'
    
    # Generate metrics
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'generation_duration_seconds': round(duration, 2),
        'urls_processed': urls_processed,
        'assets_downloaded': assets_downloaded,
        'errors': error_count,
        'total_size_mb': round(total_size / 1024 / 1024, 2),
        'total_size_bytes': total_size,
        'git_commit': git_commit,
        'output_directory': str(output_path.absolute())
    }
    
    # Save current metrics
    metrics_file = output_path / 'build-metrics.json'
    metrics_file.write_text(json.dumps(metrics, indent=2))
    print(f"   ✅ Created build-metrics.json")
    
    # Track metrics over time (in project root)
    history_file = Path('build-history.json')
    history = json.loads(history_file.read_text()) if history_file.exists() else []
    history.append(metrics)
    # Keep only last 100 builds
    history = history[-100:]
    history_file.write_text(json.dumps(history, indent=2))
    print(f"   ✅ Updated build-history.json (tracking {len(history)} builds)")
    
    # Display summary
    print(f"\n📊 Build Metrics:")
    print(f"   Duration: {metrics['generation_duration_seconds']}s")
    print(f"   URLs: {metrics['urls_processed']}")
    print(f"   Assets: {metrics['assets_downloaded']}")
    print(f"   Size: {metrics['total_size_mb']} MB")
    print(f"   Commit: {metrics['git_commit'][:8]}")
    
    return metrics
