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

3. Obtain a Microsoft Azure FaceAPI Endpoint and Key. Place both in the config.py file. The API subscription can be either free or paid version. 
Link: https://azure.microsoft.com/en-us/services/cognitive-services/face/

<img src="https://i.imgur.com/YDRUT2u.png" width="50%" height="50%" border="1" />

## Grimes Example
I provided a Person Example using the singer-celebrity Grimes. 
### Example 1: Person-To-Face
Description: Create a Person object using example images of Grimes in the KnownPerson/ directory. I provided three photos of Grimes. 
<pre>
./create_person.py KnownPerson/ --name grimes
./headhunt.py grimes 
</pre>

### Example 2: Face-To-Face
<pre>
./headhunt.py ./KnownPerson/Grimes1.webp --compare-dir ./Images
</pre>

## Operating Systems
This script is supported on Windows, Linux, and MacOS.
