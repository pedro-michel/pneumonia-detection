#!/usr/bin/env python
# coding: utf-8

# In[10]:


import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont


# In[11]:



def start_model(project_arn, model_arn, version_name, min_inference_units):

    client=boto3.client('rekognition')

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response=client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        #Get the running status
        describe_response=client.describe_project_versions(ProjectArn=project_arn,
            VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage']) 
    except Exception as e:
        print(e)
        
    print('Done...')
    
def main():
    project_arn='arn:aws:rekognition:us-east-1:857369467568:project/proj4/1637929150171'
    model_arn='arn:aws:rekognition:us-east-1:857369467568:project/proj4/version/proj4.2021-11-26T09.36.42/1637930203660'
    min_inference_units=1 
    version_name='proj4.2021-11-26T09.36.42'
    start_model(project_arn, model_arn, version_name, min_inference_units)

if __name__ == "__main__":
    main()


# In[18]:


def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
            draw.text((left,top), customLabel['Name'], fill='#00d400', font=fnt)

            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Label Width: ' + "{0:.0f}".format(width))
            print('Label Height: ' + "{0:.0f}".format(height))

            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill='#00d400', width=5)

    image.show()

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    display_image(bucket,photo,response)

    return len(response['CustomLabels'])

def main():

    bucket='proj4-bucket'
    photo='NORMAL/testimage.jpeg'
    model='arn:aws:rekognition:us-east-1:857369467568:project/proj4/version/proj4.2021-11-26T09.36.42/1637930203660'
    min_confidence=95

    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    print("Custom labels detected: " + str(label_count))


if __name__ == "__main__":
    main()


# In[ ]:




