# Simple Chainguard migration training

You need:
  - Docker
  - Git
  - Internet
  - Grype

Clone the training repository: 
git clone https://github.com/cjohannsen81/training.git 

The repository contains different folders:
  Simple - our first app
  Inky - A sample python app
  Not-Inky - Another sample application

1. Enter the directory
2. Build the image: `docker build . -t image-name`
3. Run the image: `docker run -it image-name`
4. Scan the image: `grype docker.io/library/image-name`
