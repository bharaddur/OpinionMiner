# OpinionMiner

With the emergence of social media, internet is filled with mass data and this
data has a meaning. People are willingly contributing this big data pool every day
by writing their opinions and uploading their own media. We can actually consider
internet as a brain which has limitless information flowing through it. But every brain
has its own method to evaluate the data that it consists.
This project’s aim is to contribute the evaluation of this big data by creating a
web application for extracting the data from the social media and calculate the opinions
of the social media users. Thanks to Twitter API, we have a way to extract these data
and calculate the opinions of the social media user by using natural language processing
methods.


How To Setup:

First clone the git repository by

    git clone https://github.com/bharaddur/OpinionMiner.git

Than write:

    cd OpinionMiner

Activate Virtual Environment:

    python3 -m venv myvenv

Run Virtual Emvironment:

    source myvenv/bin/activate

Install the requirements:

    pip install - requirements.txt

Than run(note that you need to have postgreSQL in your local and the connection settings should be same with the settings.py document): 

    python manage.py makemigrations

    python manage.py migrate

DB settings:

    'ENGINE': 'django.db.backends.postgresql'
    'NAME': Ominer
    'USER': Ominer
    'PASSWORD': 'Ominer'

Create an .env file in the OpinionMiner/ominer directory and add your Twitter API credentials as below:

    API_KEY= <Your Key>
    API_SECRET= <Your Key>
    ACCESS_TOKEN= <Your Key>
    ACCESS_TOKEN_SECRET= <Your Key>
    BEARER_TOKEN= <Your Key>
    DEVELOPMENT_MODE=True

That is it. Have Fun!


