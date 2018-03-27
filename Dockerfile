FROM python:3.6
MAINTAINER Pramod Kotipalli "pramodk@gatech.edu"

WORKDIR src

ADD requirements.txt .
RUN pip install -r requirements.txt

COPY ./ ./

EXPOSE 5000

ENV input_file_path "/dev/null"
ENV output_file_path "/dev/null"

CMD ["sh", "-c", "python app.py -pp ${input_file_path} -o ${output_file_path}"]
