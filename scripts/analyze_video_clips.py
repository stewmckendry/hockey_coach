import json
import os
from collections import defaultdict

INPUT_FILE = 'data/processed/video_clips.json'
OUTPUT_DIR = 'outputs'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'video_clips_summary.md')

def load_data():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    data = load_data()

    unique_videos = set()
    unique_titles = set()
    total_duration = 0.0

    # For breakdowns
    videos_by_query = defaultdict(set)
    videos_by_skill = defaultdict(set)
    videos_by_source = defaultdict(set)

    for record in data:
        vid = record.get('video_id')
        title = record.get('title')
        start = float(record.get('start_time', 0))
        end = float(record.get('end_time', 0))
        query = record.get('query_term', 'Unknown')
        skills = record.get('hockey_skills', [])
        source = record.get('source', 'Unknown')

        unique_videos.add(vid)
        unique_titles.add(title)
        total_duration += max(0, end - start)

        videos_by_query[query].add(vid)
        for skill in skills:
            videos_by_skill[skill].add(vid)
        videos_by_source[source].add(vid)

    # Prepare markdown
    md_lines = [
        "# Video Clips Summary",
        "",
        f"- **Total unique videos (by video_id):** {len(unique_videos)}",
        f"- **Total unique videos (by title):** {len(unique_titles)}",
        f"- **Total video duration (seconds):** {total_duration:.2f}",
        "",
        "## Breakdown of unique videos by query_term",
        "",
    ]
    for query, vids in sorted(videos_by_query.items()):
        md_lines.append(f"- **{query}:** {len(vids)}")

    md_lines += [
        "",
        "## Breakdown of unique videos by hockey_skills",
        "",
    ]
    for skill, vids in sorted(videos_by_skill.items()):
        md_lines.append(f"- **{skill}:** {len(vids)}")

    md_lines += [
        "",
        "## Breakdown of unique videos by source",
        "",
    ]
    for source, vids in sorted(videos_by_source.items()):
        md_lines.append(f"- **{source}:** {len(vids)}")

    # Write output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    print(f"Summary written to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()