from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('bucket', image_name, file_object, file_object.size)
        return f"http://localhost:9000/bucket/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def add_pic(new_sat, pic):
    client = Minio(
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    i = new_sat.satellite_id
    img_obj_name = f"{i}.png"

    if not pic:
        return Response({"error": "No file recognised."})
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    new_sat.image_url = result
    new_sat.save()

    return Response({"message": "success"})

def process_file_delete(client, image_name):
    try:
        client.remove_object('bucket', image_name)
        return {'status': 'success'}
    except Exception as e:
        return {'error': str(e)}


def del_pic(satellite):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )

    url = f"{satellite.satellite_id}.png"

    res = process_file_delete(client, url)
    if 'error' in res:
        return Response(res)

    return Response({'status': 'success'})