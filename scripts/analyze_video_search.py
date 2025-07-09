import os
import json
from collections import defaultdict

INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'input')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'video_summary.md')

def main():
    total_videos = 0
    videos_by_search = {}
    videos_by_channel = defaultdict(int)
    total_views = 0

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.json'):
            search_name = filename.replace('video_search_', '').replace('.json', '')
            path = os.path.join(INPUT_DIR, filename)
            with open(path, 'r') as f:
                try:
                    videos = json.load(f)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    continue
                videos_by_search[search_name] = len(videos)
                total_videos += len(videos)
                for video in videos:
                    channel = video.get('channel', 'Unknown')
                    videos_by_channel[channel] += 1
                    total_views += video.get('view_count', 0)

    lines = []
    lines.append(f"# Video Summary\n")
    lines.append(f"- **Total videos:** {total_videos}\n")
    lines.append(f"- **Total view count:** {total_views}\n")

    lines.append("\n## Videos by search\n")
    lines.append("| Search | Video Count |")
    lines.append("|--------|-------------|")
    for search, count in videos_by_search.items():
        lines.append(f"| {search} | {count} |")

    lines.append("\n## Videos by channel\n")
    lines.append("| Channel | Video Count |")
    lines.append("|---------|-------------|")
    for channel, count in videos_by_channel.items():
        lines.append(f"| {channel} | {count} |")

    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Summary written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()