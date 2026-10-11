FROM public.ecr.aws/lambda/python:3.12

ENV YOLO_CONFIG_DIR=/tmp/Ultralytics
ENV MPLCONFIGDIR=/tmp/matplotlib

COPY yolov5 ${LAMBDA_TASK_ROOT}/yolov5
COPY yolov5s.pt ${LAMBDA_TASK_ROOT}/yolov5s.pt
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/lambda_function.py

RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision

RUN grep -vE '^(torch|torchvision|opencv-python)' \
    ${LAMBDA_TASK_ROOT}/yolov5/requirements.txt \
    > /tmp/yolo-requirements.txt \
    && pip install --no-cache-dir \
    -r /tmp/yolo-requirements.txt \
    && pip install --no-cache-dir \
    opencv-python-headless

CMD ["lambda_function.lambda_handler"]
