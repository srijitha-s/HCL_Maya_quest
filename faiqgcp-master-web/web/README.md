Add the Dockerfile to folder(alredy added)

#build image

docker build -t image_name ./

#list images and check the image name

docker images

#tag the image for push

docker tag image_name gcr.io/project_name/image_name

#check for image and tag

docker images

# push image to container registry
docker push gcr.io/project_name/image_name

Now check  conatiner registry in GCP console for image
click on image and click deploy to cloud  run    ------ here u can deploy to GKE,GCE
create service in cloud run by allowing unautheticated invocations
once done click on the URL to access the app     ------currently getting error


(2nd way)from app engine:
-----------------
after deploying the app in app engine
container registry holds the image
now deploy this image to cloud run
create service in cloud run by allowing unautheticated invocations
once done click on the URL to access the app     ------currently working


