FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Install PyTorch CPU version
RUN pip install -v torch torchaudio -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install cargo && c++ compilers for deepfilternet
RUN apt-get install -y cargo build-essential

# Install deepfilter net
RUN pip install deepfilternet

# Install requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose gradio port
EXPOSE 7860 

CMD ["sh", "-c", "python process_record_ui.py"]
