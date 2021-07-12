
# What is this?

Early days spike around examples and examplars of what the final product we want from producers might look like.

Uses a flask based web application deployed via google cloud via google [cloud Run](https://cloud.google.com/run) (TLDR: sorta like a serverless function but its a container). The corresponding dockerfile is in `/app/Dockerfile`.

_Note: this branch of work is very much teasing out the questions rather than the answers at the moment don't read too much into anything._


## The app

A restful api that I'm using to poke at what outputs closer to our future goals would look like.

Defined in `/app`.

To view a restful summary of csvws for a given resoure, pass a landing page i via `https://flaskapp-cr-v1-no4vxskx7a-nw.a.run.app/v1/landingpage?url=<LANDING PAGE URL>`

The api root of the app can (as at 28/6/2021) be found and explored at [https://flaskapp-cr-v1-no4vxskx7a-nw.a.run.app/v1/organisations](https://flaskapp-cr-v1-no4vxskx7a-nw.a.run.app/v1/organisations)

_NOTE: At time of writing anything the its just a stub with only two (more or less) hard coded ONS landing pages present on the backend to fuel the api._


### How do I deploy?

Export our google projet ID
`export MY_PROJECT_ID=<the project id>`

Build Docker on your local machine
`$ docker build -t gcr.io/$MY_PROJECT_ID/flask_examplar_spike_app:v1 -f Dockerfile . `

Login via googl sdk
`gcloud auth login`

Congigure gcloud docker access (if you've never done it before)
`gcloud auth configure-docker`

Push the Docker image to google Container Registry 
`$ docker push gcr.io/$MY_PROJECT_ID/flask_examplar_spike_app:v1`

Deploy the docker image on cloud run
```
$ gcloud run deploy flaskapp-cr-v1 \
 --image gcr.io/$MY_PROJECT_ID/flask_examplar_spike_app:v1 \
 --region europe-west2 \
 --platform managed \
 --memory 128Mi
```

### How do I run locally for developing?

* cd to the `app` directory.
* `pipenv run python3 main_v1.py`
* navigate to `http://127.0.0.1/v1/organisations`

