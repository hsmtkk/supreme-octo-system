FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ./

# chroma requires C++ compiler
RUN dnf install g++ -y

RUN python3.12 -m pip install -r requirements.txt -t .

COPY app.py ./

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]
