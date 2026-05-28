import gradio as gr
from pathlib import Path
from pydub import AudioSegment
from process_record import transform_m4a_to_wav, split_audio, remove_noise_from_folder, combine_wav_files_with_suffix, generate_timestamp, add_suffix_before_extension, increase_wav_gain, remove_silence

# Example usage
if __name__ == "__main__":
    INPUT_FILE = "input_audios/"
    INPUT_FILE+="Voz 071" + ".m4a"

    WORKDIR_FOLDER = Path(INPUT_FILE).parent / Path(INPUT_FILE).stem
    WORKDIR_FOLDER.mkdir(exist_ok=True)
    DENOISE = 1 #default 0
    
    if DENOISE:
        # Convert to wav
        wav_filepath = transform_m4a_to_wav(INPUT_FILE, WORKDIR_FOLDER)

        # Denoise
        output_dir = split_audio(wav_filepath)
        remove_noise_from_folder(output_dir)
        outfile = combine_wav_files_with_suffix(
            input_folder=output_dir,
            output_folder=WORKDIR_FOLDER,
            suffix="_noiseRemovedDF",
            output_filename= Path(INPUT_FILE).stem + "_D.wav"
        )

    denoised_filepath = WORKDIR_FOLDER / (Path(INPUT_FILE).stem + "_D.wav")

    # Increase volume
    input = denoised_filepath
    gain_increased_filepath = add_suffix_before_extension(input,"_GI")
    increase_wav_gain(input, gain_increased_filepath, 0)  

    # Remove silence gaps
    input = gain_increased_filepath
    wav_file_no_silence = add_suffix_before_extension(input,"_NS")
    remove_silence(input,output_file=wav_file_no_silence)
