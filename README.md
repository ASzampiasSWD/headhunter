# headhunter
Find people in face masks, sunglasses, low quality images, hats, and different hair styles using Microsoft Azure FaceAPI. HeadHunter takes an image (or sets of images) and identifies the same face in other photos. Options include People-To-Face, Person-To-Face, and Face-To-Face.

## Steps
1. Install the python libraries using pip3:
<pre>
pip3 install -r requirements.txt
</pre>

2. Give permissions to the scripts for Linux:
<pre>
chmod +x create_person.py
chmod +x headhunt.py
</pre>

3. Obtain a Microsoft Azure FaceAPI Endpoint and Key. Place both in the config.py file. The API subscription can be either free or paid version. 
Link: https://azure.microsoft.com/en-us/services/cognitive-services/face/

<img src="https://i.imgur.com/YDRUT2u.png" width="50%" height="50%" border="1" />

## Examples
I provided Face, Person, and People Examples using the singer-celebrity Grimes and Spaceman Elon. 
### Example 1: Person-To-Face
Description: Create a Person object using example images of Grimes in the KnownPeople/Grimes directory. I provided three photos of Grimes. 
<pre>
./create_person.py KnownPeople/Grimes --name grimes
./headhunt.py grimes 
</pre>

### Example 2: Face-To-Face
<pre>
./headhunt.py ./KnownPeople/Grimes/Grimes1.webp --compare-dir ./Images
</pre>

### Example 3: People-To-Face
Description: Create multiple Person objects using example images of Grimes and Elon in the KnownPeople/ directory. I provided three photos of each person. Change the config_people.txt file with name:{directory path to image folder}. Create a newline for each Person. Be mindful the names are lowercase and match regex requirements.
<pre>
 ./create_people.py --name star
 ./headhunt.py star
</pre>

## Operating Systems
This script is supported on Windows, Linux, and MacOS.

## How-To Video
[![How To Video](https://img.youtube.com/vi/rnMrB7M15pk/0.jpg)](https://www.youtube.com/watch?v=rnMrB7M15pk)
