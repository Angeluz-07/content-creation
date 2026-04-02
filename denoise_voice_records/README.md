# Denoise Voice Records
App built with Gradio and 'deepfilternet' to denoise voice records in format .m4a

## Docker commands

```
# Build img
docker_build_img.bat

# Run docker img
docker_run_img.bat

# Access to service via 'locahost:7860'

# Run bash in the running docker img
docker_bash_img.bat
```

## Commands for local dev(TODO: Review)
```
# create venv
python -m venv .venv

# run denoise script
python process_record_ui.py
```
