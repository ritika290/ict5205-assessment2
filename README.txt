ITC5205 Assignment 2 - YOLOv5 Object Identification System on AWS

Student name: Ritika
Student number: 250146

Short description:
This project implements an image object-identification system on AWS. API Gateway receives a JSON request with an S3 bucket and image key. Lambda runs a YOLOv5 container image, processes the image, writes the annotated output and JSON result to S3, and stores summary metadata in DynamoDB.

Main live API endpoint:
https://p0paz4dgof.execute-api.us-east-1.amazonaws.com/prod/detect

Important security note:
The API key is intentionally not included in this README or the report. I'll share it only through the approved secure submission method if required.

Folder structure:
code/     Lambda source code.
deploy/   Dockerfile and deployment/testing commands.
images/   Screenshots and sample images used in the report.

Required AWS resources used:
- S3 bucket: itc5205-yolov5-ritika
- Lambda function: ITC5205-YOLOv5-Detector
- ECR repository: itc5205-yolov5-lambda
- DynamoDB table: ITC5205-ObjectDetections
- API Gateway REST API: ITC5205-YOLOv5-API
- Usage plan: ITC5205-YOLOv5-UsagePlan
