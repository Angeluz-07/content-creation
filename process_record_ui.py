import gradio as gr
from pathlib import Path
from pydub import AudioSegment
from process_record import transform_m4a_to_wav, split_audio, remove_noise_from_folder, combine_wav_files_with_suffix, generate_timestamp, remove_silence, add_suffix_before_extension
import version

INPUT_AUDIOS_FOLDER = Path(__file__).parent / "input_audios"
INPUT_AUDIOS_FOLDER.mkdir(exist_ok=True)

DEFAULT_EXAMPLE = Path(__file__).parent / "examples" / "Voz 070.m4a"
def postprocess_denoised_audio(denoised_filepath, no_silence):
    #import pdb;pdb.set_trace()
    if denoised_filepath:
        if no_silence:
            # Remove Silences
            input_filepath = denoised_filepath
            output_path = add_suffix_before_extension(input_filepath,"_NS")
            remove_silence(input_filepath, output_file=output_path)
            denoised_and_nosilence_path = output_path
        else: 
            denoised_and_nosilence_path = None
    else:
        return None
    return denoised_and_nosilence_path

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
    return denoised_filepath


with gr.Blocks() as demo:
    # A hidden component to pass the audio data between tabs
    shared_audio_state = gr.State(value=None) 
    # gr.State is better for hidden, non-UI data transfer

    with gr.Tab("Step 1: Denoise Audio"):

        with gr.Row():
            
            with gr.Column():
                input_audio_t1 =  gr.Audio(value=DEFAULT_EXAMPLE, label="Input Audio(*.m4a)", type="filepath")
                run_button_t1 = gr.Button("Submit")
    
            with gr.Column():
                output_audio_t1 = gr.Audio(label="Output Audio. Denoised(*.wav)", type="filepath", interactive=False)


            # The core logic for Tab 1
            fn1_results = run_button_t1.click(
                fn=process_audio,
                inputs=[input_audio_t1],
                outputs=[output_audio_t1]
            )
            
            # !!! KEY STEP 1: Update the hidden shared state component 
            # when Tab 1's function completes.
            fn1_results.then(
                fn=lambda x: x,  # Simple pass-through function
                inputs=[output_audio_t1],
                outputs=[shared_audio_state]
            )

    # Tab 2: Audio Analyzer
    with gr.Tab("Step 2: Postprocess Denoised Audio") as tab2:
        
        with gr.Row():
            # We don't need an input Audio component here, as the input comes from the state
            with gr.Column():
                in2 = gr.Audio(label="Output Audio. Denoised(*.wav)", type="filepath", interactive=False)
                checkbox = gr.Checkbox(label="Remove Silence After Denoise")
                use_tab1_output_button = gr.Button("Submit")
            with gr.Column():
                output_text_t2 = gr.Audio(label="Output Audio. Denoised + No Silences(*.wav)")

        tab2.select(
            fn=lambda x: x,  # Returns path for display and path for the next step
            inputs=[shared_audio_state], 
            outputs=[in2] # State is a dummy output to chain the next call
        )
        # !!! KEY STEP 2: Use the hidden shared state component as 
        # the input for Tab 2's function when the button is clicked.
        use_tab1_output_button.click(
            fn=postprocess_denoised_audio,
            inputs=[shared_audio_state, checkbox ], # Pass the hidden state
            outputs=[output_text_t2]
        )

demo.launch(server_name="0.0.0.0", show_error=True)