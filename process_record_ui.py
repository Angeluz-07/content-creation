import gradio as gr
from pathlib import Path
from pydub import AudioSegment
from process_record import transform_m4a_to_wav, split_audio, remove_noise_from_folder, combine_wav_files_with_suffix, generate_timestamp

INPUT_AUDIOS_FOLDER = Path(__file__).parent / "input_audios"
INPUT_AUDIOS_FOLDER.mkdir(exist_ok=True)

def process_audio(audio_filepath):
    # generate workdir folder    
    TS = generate_timestamp()
    WORKDIR_FOLDER = INPUT_AUDIOS_FOLDER / f"{TS}_{Path(audio_filepath).stem}"
    WORKDIR_FOLDER.mkdir(exist_ok=True)

    # convert to wav
    wav_filepath = transform_m4a_to_wav(audio_filepath, output_dir = WORKDIR_FOLDER)

    # Denoise
    input_filepath = wav_filepath
    output_dir = split_audio(input_filepath)
    remove_noise_from_folder(output_dir)
    denoised_filepath = combine_wav_files_with_suffix(
        input_folder=output_dir,
        output_folder=WORKDIR_FOLDER,
        suffix="_noiseRemovedDF",
        output_filename= Path(input_filepath).stem + "_D.wav"
    )
    
    # result
    result_filepath = denoised_filepath
    return result_filepath

demo = gr.Interface(
    fn=process_audio, inputs=[gr.Audio(label="Input Audio", type="filepath")], outputs=[gr.Audio(label="Output Audio")]
)

demo.launch(server_name="0.0.0.0")