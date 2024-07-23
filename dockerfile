FROM python:3.10.14
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 libsndfile1 alsa-utils -y

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD [ "python", "./main.py" ]