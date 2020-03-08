# Hydroshare Jupyter GUI Server Extension

## Setup Instructions
1. Clone the repository
2. Navigate to hydroshare-jupyter-gui/backend and run these in the command line:

`python setup.py install`

`pip install -r requirements.txt`

3. [Install Node](https://nodejs.org/en/download/), then navigate to hydroshare-jupyter-gui/webapp and run the following in the command line:

`yarn install`

`yarn build`


4. To install jupyter notebook, run the following:

`pip install notebook`

5. Next, you'll need to modify the jupyter config file. Do this by opening it with your editor of choice (here I use gedit):

`gedit ~/.jupyter/jupyter_notebook_config.py`

Find the line that begins with `c.NotebookApp.nbserver_extensions` and change it to `c.NotebookApp.nbserver_extensions = {'backend.hydroshare_gui': True}`

6. Navigate to back to hydroshare_jupyter_gui and run the following:

`export PYTHONPATH=$(pwd)/backend`

`export PYTHONPATH=$PYTHONPATH:$(pwd)`

7. In the same directory, add a file called login.py that contains the following:

```
username = 'your_hydroshare_username'
password = 'your_hydroshare_password'
```

8. Now run:

`jupyter notebook`

You should see a message in the terminal that says "CUAHSI module enabled!"

9. In your web browser, go to localhost:8080 and view the beautiful GUI!
