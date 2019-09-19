# RDPwnFinder
Uses Python and machine learning to identify RDP servers with a Sticky Keys backdoor.

![Example Screenshot](/ExampleScreenshot.png)

## Scripts
The scripts directory contains various scripts to help collect images, train models, classify images, etc.
* RDPwnFinder.py - Connects to an IP, screenshots, and classifies the image based on a provided training model.
* nmap-rdp-scanner.sh - Helper script to scan an input list of IPs and output a list of IPs with RDP supporting RDP encryption.
* create_training_model.py - Provide pre-classified images and output a training model for later use
* RDP_image_reformatter.py - Reformat previously captured RDP screenshots for use with create_training_model.py.
* image_sort_helper.py - Helps you manually sort captured images into "clean" and "hacked" for training.
* test_against_training_model.py - Tests a single image against a provided training model.
* test_and_sort_against_training_model.py - Test a single image against a provided training model and sort it into a directory.

## Models
This repository comes with a single AdaBoostClassifier training model. It has been trained with several thousand images and seems to work very well.

## Usage
Basic usage to test an RDP server is:
cd images
python ../scripts/RDPwnFinder.py -n ../models/ADABoostClassifier.mdl -g gray -c color -p hacked <IP>

If you want to test many IPs, you can do it with Bash
for host in $(cat ip_list.txt); do python ../scripts/RDPwnFinder.py -n ../models/ADABoostClassifier.mdl -g gray -c color -p hacked $host; done

## Other Info
No training images are provided with this repo to protect the privacy of others.

## Bugs
There are some unhandled exceptions in either these scripts or in the RDP Screen Capture libraries used. Sometimes it will break and you have to manually kill the python process.