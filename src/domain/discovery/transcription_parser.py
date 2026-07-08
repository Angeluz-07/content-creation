from typing import List
from .models import TextSegment
from src.domain.common import read_json

class TranscriptionParser:

    def _format_time(self, seconds: float) -> str:
        """
        Helper method to convert seconds into an exact HH:MM:SS.ffffff string
        matching the '%H:%M:%S.%f' format specifier.
        """
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        # Extract the fractional part and convert to microseconds (6 digits)
        microseconds = int(round((seconds % 1) * 1_000_000))
        
        return f"{hrs:02d}:{mins:02d}:{secs:02d}.{microseconds:06d}"

    def run(self, file_path,  min_words: int = 90) -> List[TextSegment]:
        """
        Parses the JSON file, groups segments based on a minimum word count threshold,
        and returns a list of TextSegment objects.
        """
        data = read_json(file_path)
        segments = data.get("segments", [])
        if not segments:
            return []

        result = []
        
        # Temporary placeholders for the current block we are building
        current_text = []
        current_start = None
        
        for seg in segments:
            text = seg.get("text", "").strip()
            if not text:
                continue  # Skip completely empty segments
            
            # If we aren't currently tracking a block, start a new one
            if current_start is None:
                current_start = seg["start"]
            
            current_text.append(text)
            
            # Count words in the current accumulated block
            combined_text = " ".join(current_text)
            word_count = len(combined_text.split())
            
            # If we hit the min_words threshold, close the block and create the segment
            if word_count >= min_words:
                result.append(
                    TextSegment(
                        text=combined_text,
                        start=self._format_time(current_start),
                        end=self._format_time(seg["end"])
                    )
                )
                # Reset buffers for the next block
                current_text = []
                current_start = None
        
        # Handling edge case: if there are leftover segments that didn't reach min_words
        if current_text and current_start is not None:
            result.append(
                TextSegment(
                    text=" ".join(current_text),
                    start=self._format_time(current_start),
                    end=self._format_time(segments[-1]["end"])
                )
            )

        return result