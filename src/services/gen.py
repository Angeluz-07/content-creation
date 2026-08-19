from pathlib import Path
from typing import List
from src.domain.download.services import download_vtt
from src.domain.discovery.parser import parse_vtt_
from src.domain.discovery.parser import format_to_text_block
from src.domain.common import read_json, save_json
from pydantic import BaseModel


class SegmentDelimited(BaseModel):
    limits: List[str]
    summary: str


class SegmentsAnalysis(BaseModel):
    items: List[SegmentDelimited]


class Vignette(BaseModel):
    personajes: List[str]
    texto: str
    descripcion: str
    score_atribucion: int


class VignettesAnalysis(BaseModel):
    items: List[Vignette]


def run_structured_llm(
    llm_client,
    prompts_repo,
    prompt_key: str,
    user_content: str,
    response_model: BaseModel,
    temperature: float = 0.1,
    debug: bool = False,
) -> BaseModel:
    _, system_prompt = prompts_repo.get(prompt_key)

    print(f"[{prompt_key}] Sending text to LLM...")
    result = llm_client.generate(
        system_prompt,
        user_content,
        response_model=response_model,
        temperature=temperature,
    )

    if debug:
        print(f"--- DEBUG [{prompt_key}] ---")
        print("System:", system_prompt)
        print("User:", user_content)
        print("Output:", result)

    return result


class SegmentsProvider:

    async def gen(
        self,
        url: str,
        output_filename: str,
        vtt_dir: Path | str,
        cookies_path: Path | str,
    ) -> List[dict]:
        params = {
            "url": url,
            "output_filename": output_filename,
            "output_dir": vtt_dir,
            "cookies_path": cookies_path,
        }
        vtt_path = await download_vtt(**params)
        result = parse_vtt_(vtt_path)
        return result

    async def fetch_or_gen(
        self,
        filepath: Path | str,
        url: str,
        output_filename: str,
        vtt_dir: Path | str,
        cookies_path: Path | str,
        force: bool = False,
    ) -> list[dict]:
        path = Path(filepath)
        class_name = self.__class__.__name__

        if path.exists() and not force:
            print(f"[{class_name}] File exists {path.name} , skipping generation...")
            return parse_vtt_(path)

        print(f"[{class_name}] File missing {path.name} , generating...")
        return await self.gen(url, output_filename, vtt_dir, cookies_path)


class MomentsDetector:

    def __init__(self, prompts_repo, llm_client):
        self.prompts_repo = prompts_repo
        self.llm_client = llm_client

    def gen(self, text_segments, debug: bool):
        text_for_llm = format_to_text_block(text_segments)

        llm_result = run_structured_llm(
            self.llm_client,
            self.prompts_repo,
            prompt_key="textanalizer",
            user_content=text_for_llm,
            response_model=SegmentsAnalysis,
            debug=debug,
        )
        llm_output = llm_result.model_dump(mode="json")["items"]
        result = self.map_delimited_segments(llm_output, json_base=text_segments)
        return result

    def fetch_or_gen(
        self,
        filepath: Path | str,
        text_segments: list[dict],
        debug: bool = False,
        force: bool = False,
    ) -> list[dict]:
        path = Path(filepath)
        class_name = self.__class__.__name__

        if path.exists() and not force:
            print(f"[{class_name}] File exists {path.name}, skipping generation...")
            return read_json(path)

        print(f"[{class_name}] File missing {path.name}, generating...")
        result = self.gen(text_segments, debug=debug)
        save_json(result, path)
        return result

    def map_delimited_segments(
        self, llm_output: list[dict], json_base: list[dict]
    ) -> list[dict]:
        resultado = []
        for item in llm_output:
            idx_inicio, idx_fin = int(item["limits"][0]), int(item["limits"][1])
            segmentos = json_base[idx_inicio : idx_fin + 1]

            resultado.append(
                {
                    "start": segmentos[0]["start"],
                    "end": segmentos[-1]["end"],
                    "summary": item["summary"],
                    "text": " ".join(seg["text"] for seg in segmentos),
                }
            )
        return resultado


class VignettesEditor:

    def __init__(self, prompts_repo, llm_client):
        self.prompts_repo = prompts_repo
        self.llm_client = llm_client

    def gen(self, moments: list[dict], debug: bool = False) -> list[dict]:

        llm_result = run_structured_llm(
            self.llm_client,
            self.prompts_repo,
            prompt_key="texteditor",
            user_content=str(moments),
            response_model=VignettesAnalysis,
            debug=debug,
        )

        return llm_result.model_dump(mode="json")["items"]

    def fetch_or_gen(
        self,
        filepath: Path | str,
        moments: list[dict],
        debug: bool = False,
        force: bool = False,
    ) -> list[dict]:
        path = Path(filepath)
        class_name = self.__class__.__name__

        if path.exists() and not force:
            print(f"[{class_name}] File exists {path.name}, skipping generation...")
            return read_json(path)

        print(f"[{class_name}] File missing {path.name}, generating...")
        result = self.gen(moments, debug=debug)
        save_json(result, path)
        return result


async def gen_imgs(
    url: str,
    output_filename: str,
    vtt_dir: Path | str,
    cookies_path: Path | str,
    llm_client,
    prompts_repo,
    debug: bool = False,
    force: bool = False,
):

    video_id = Path(output_filename).stem
    out_dir = Path(vtt_dir)
    paths = {
        "vtt": out_dir / f"{video_id}.vtt",
        "moments": out_dir / f"{video_id}_moments.json",
        "vignettes": out_dir / f"{video_id}_vignettes.json",
    }
    ts_provider = SegmentsProvider()
    m_detector = MomentsDetector(prompts_repo, llm_client)
    v_editor = VignettesEditor(prompts_repo, llm_client)

    text_segments = await ts_provider.fetch_or_gen(
        filepath=paths["vtt"],
        url=url,
        output_filename=output_filename,
        vtt_dir=out_dir,
        cookies_path=cookies_path,
        force=force,
    )

    moments = m_detector.fetch_or_gen(
        filepath=paths["moments"], text_segments=text_segments, debug=debug, force=force
    )

    vignettes = v_editor.fetch_or_gen(
        filepath=paths["vignettes"], moments=moments, debug=debug, force=force
    )

    return vignettes
