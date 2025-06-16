import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.subtitle_parser import parse_and_filter_subtitles


def test_profanity_filter(tmp_path):
    sample = tmp_path / "sample.srt"
    sample.write_text("""1\n00:00:01,000 --> 00:00:02,000\nThis is damn bad.\n""")
    filters = {
        "profanity": {
            "enabled": True,
            "word_list": ["damn"],
            "replace_with": "***",
        }
    }
    orig, filtered, actions = parse_and_filter_subtitles(str(sample), filters)
    assert actions[0]["matched_word"].lower() == "damn"
    assert "***" in filtered[0].content
