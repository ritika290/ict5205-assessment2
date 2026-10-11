import json
import os
import uuid
import logging
from pathlib import Path

import boto3
import cv2
import torch

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("ITC5205-ObjectDetections")
MODEL_PATH = "/var/task/yolov5s.pt"
YOLO_PATH = "/var/task/yolov5"

logger.info("Loading YOLOv5 model")

model = torch.hub.load(
    YOLO_PATH,
    "custom",
    path=MODEL_PATH,
    source="local"
)

model.conf = 0.25


def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))

        # Supports direct Lambda tests and API Gateway requests
        if "body" in event:
            body = event["body"]

            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event

        bucket = body.get("bucket")
        key = body.get("key")

        if not bucket or not key:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "bucket and key are required"
                })
            }

        request_id = str(uuid.uuid4())

        filename = Path(key).name
        stem = Path(filename).stem

        local_input = f"/tmp/{filename}"
        local_output = f"/tmp/{stem}-detected.jpg"

        logger.info("Downloading s3://%s/%s", bucket, key)

        s3.download_file(bucket, key, local_input)

        # YOLOv5 inference
        results = model(local_input)

        detections = []

        for row in results.xyxy[0].cpu().numpy():
            x1, y1, x2, y2, confidence, class_id = row

            detections.append({
                "class": model.names[int(class_id)],
                "confidence": round(float(confidence), 4),
                "box": {
                    "x1": round(float(x1), 2),
                    "y1": round(float(y1), 2),
                    "x2": round(float(x2), 2),
                    "y2": round(float(y2), 2)
                }
            })

        # Render bounding boxes
        rendered = results.render()[0]

        cv2.imwrite(local_output, rendered)

        output_key = f"output/{stem}-detected.jpg"
        result_key = f"results/{stem}.json"

        s3.upload_file(local_output, bucket, output_key)

        result_data = {
            "request_id": request_id,
            "input": key,
            "output": output_key,
            "object_count": len(detections),
            "detections": detections
        }
        table.put_item(
            Item={
                "request_id": request_id,
                "input_image": key,
      	        "output_image": output_key,
      	        "result_file": result_key,
                "object_count": len(detections),
                "detected_classes": list(
                    set(item["class"] for item in detections)
	        )
	    }
	)

        s3.put_object(
            Bucket=bucket,
            Key=result_key,
            Body=json.dumps(result_data, indent=2),
            ContentType="application/json"
        )

        logger.info(
            "Detection complete. %s objects found.",
            len(detections)
        )

        return {
            "statusCode": 200,
            "body": json.dumps(result_data)
        }

    except Exception as exc:
        logger.exception("Object detection failed")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Object detection failed",
                "error": str(exc)
            })
        }
