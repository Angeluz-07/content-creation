from src.domain.common import save_json, read_json
from src.domain.download.services import download_vtt
from src.domain.discovery.parser import parse_vtt_
from src.domain.discovery.parser import format_to_text_block
from typing import List
from pathlib import Path
from pydantic import BaseModel


async def get_text_segments(
    data, vtt_dir: Path | str, cookies_path: Path | str
) -> List[dict]:
    output_filename = data["output_filename"]
    vtt_path = Path(vtt_dir) / f"{output_filename}.vtt"

    if Path(vtt_path).is_file():  # vtt exists
        print(f"Vtt exists {output_filename}. Skipping download...")
        result = parse_vtt_(vtt_path)
        return result

    params = {**data, "output_dir": vtt_dir, "cookies_path": cookies_path}
    print("Vtt doesnt exists, downloading...")
    vtt_path = await download_vtt(**params)
    result = parse_vtt_(vtt_path)
    return result


class SegmentDelimited(BaseModel):
    limits: List[str]
    summary: str


class TextAnalysisResult(BaseModel):
    # Este modelo envuelve la lista para que Gemini devuelva el formato JSON correcto
    segments: List[SegmentDelimited]


def map_delimited_segments(llm_output, json_base):
    resultado = []
    for item in llm_output:
        idx_inicio = int(item["limits"][0])
        idx_fin = int(item["limits"][1])
        segmentos_seleccionados = json_base[idx_inicio : idx_fin + 1]
        texto_agrupado = " ".join(seg["text"] for seg in segmentos_seleccionados)

        resultado.append(
            {
                "start": segmentos_seleccionados[0]["start"],
                "end": segmentos_seleccionados[-1]["end"],
                "summary": item["summary"],
                "text": texto_agrupado,
            }
        )

    return resultado


def get_text_analysis(text_segments, prompts_repo, llm_client, debug):
    metadata, system_prompt = prompts_repo.get("textanalizer")
    text_for_llm = format_to_text_block(text_segments)
    print("Sending text to llm...")
    llm_result = llm_client.generate(
        system_prompt,
        text_for_llm,
        response_model=TextAnalysisResult,
        temperature=0.1,
    )
    if debug:
        print("systempromt", system_prompt)
        print("usercontent", text_for_llm)
        print("llm_output", llm_result)

    llm_output = llm_result.model_dump(mode="json")["segments"]
    result = map_delimited_segments(llm_output, json_base=text_segments)
    return result


async def get_moments(
    data,
    vtt_dir: Path | str,
    cookies_path: Path | str,
    llm_client,
    prompts_repo,
    debug=False,
):
    output_filename = data["output_filename"]
    text_analysis_path = (
        Path(vtt_dir) / f"{output_filename}_textanalysis.json"  # todo change
    )

    if Path(text_analysis_path).is_file():  # file exists
        print(f"Text analysis exists {output_filename}. Skipping generation...")
        result = read_json(text_analysis_path)
        return result

    print("Text analysis doesnt exist, generating...")
    text_segments = await get_text_segments(data, vtt_dir, cookies_path)
    result = get_text_analysis(text_segments, prompts_repo, llm_client, debug)
    save_json(result, text_analysis_path)
    return result
