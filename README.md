# headhunter
This python script uses Microsoft Azure FaceAPI for Person-To-Face and Face-To-Face comparision. 

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

3. Obtain a Microsoft Azure FaceAPI Endpoint and Key. Place in config.py file. This can either be free or paid version. 
Link: https://azure.microsoft.com/en-us/services/cognitive-services/face/


 <img src="https://drive.google.com/uc?export=view&id=1pdLedj8QJP4_O7qCRdrQ90rQ7l2y5UN9" alt="Image to Endpoint and Key Directory" />

## Grimes Example
I provided a Person Example using Grimes. 
Example 1: Person-To-Face
Description: Create a Person object using example images of Grimes in the KnownPeople/ directory. I provided three photos of Grimes. 
<pre>
./create_person.py KnownPeople/ --name grimes --person-name grimes
./headhunt.py grimes 
</pre>

Example 2: Face-To-Face
<pre>
./headhunt.py ./KnownPerson/Grimes1.webp --compare-dir ./Images
</pre>

## How-to Video
[![How To Video](https://img.youtube.com/vi/IEl-kBQvutU/0.jpg)](https://www.youtube.com/watch?v=IEl-kBQvutU)

