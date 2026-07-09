from src.domain.discovery.parser import parse_vtt, format_to_text_block
from src.config import TEST_DATA_DIR
from pathlib import Path

test_vtts = [str(Path(TEST_DATA_DIR) / "example00.es.vtt")]


expected_result = [
    {"start": "00:01:56.190", "end": "00:01:56.200", "text": "Estamos causa."},
    {"start": "00:01:56.200", "end": "00:01:58.429", "text": "Llegamos a Mecausa."},
    {
        "start": "00:01:58.439",
        "end": "00:02:02.630",
        "text": "La [ __ ] está en Mecausa.",
    },
    {
        "start": "00:02:06.709",
        "end": "00:02:06.719",
        "text": "Jovi 21 en la casa. O pais activado.",
    },
    {"start": "00:02:06.719", "end": "00:02:07.670", "text": "Me causa."},
    {
        "start": "00:02:07.680",
        "end": "00:02:21.190",
        "text": "No, no nos pusimos modo mundial.",
    },
]


def test_parse_vtt():
    result = parse_vtt(test_vtts[0])
    # result = format_to_text_block(result)
    # test mapped structured
    assert "start" in result[0].keys()
    assert "end" in result[0].keys()
    assert "text" in result[0].keys()

    # test expected output
    assert result == expected_result
