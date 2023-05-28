In order to launch the application, you may use docker. First, you need to build the container:

'''docker build --tag sdet_task:latest .'''

Then, in order to launch the container, please use command:

'''docker run --publish 8000:8080 sdet_task:latest'''

In case your local port 8000 is occupied, you are welcome to use the alternative one. 