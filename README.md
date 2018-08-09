# Holograph Back-End
This tool was done as a part of my Master's thesis for the University of Tartu. It is a resource impact analysis tool, that provides data to the front-end implementation of Holograph, which can be found [here](https://github.com/gersonnoboa/Holograph_FrontEnd).

Holograph Back-End is the service that provides the information needed for displaying the different visualizations that Holograph Front-End supports. It was developed in Python with the Flask framework. Although it was made with Holograph Front-End in mind, since it is a service that receives and provides data, any application could be built on top of it. Just as the front-end implementation, Holograph Back-End can be divided into three parts: file upload, general mining, and results.

In order to deploy, do the following steps (Windows only):

1. Clone the repository
2. Install python and pip
3. Install flask, flask_cors, jsonpickle and arrow. If there are missing packages, go to the requirements.txt in order to double-check.
4. Execute the "holograph.py" file with the Python file in the venv/Scripts directory.