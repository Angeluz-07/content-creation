# Tools for content creation
Personal repo with tools to automate tasks for content creation.

## Docker commands

```
# build image
docker build -t content-creation-img .

# Run docker default script
docker run -p 7860:7860 -it content-creation-img

# Access to service via 'locahost:7860'

# Run docker another script
docker run -it content-creation-img bash
```

## Commands for local dev
```
# create venv
python -m venv .venv

# run denoise script
python process_record_ui.py
```
