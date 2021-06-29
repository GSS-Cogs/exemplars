
from flask import Flask, request

app = Flask(__name__)

@app.route('/transform')
def transform():
    """
    Run a transform based on parameters recieved via a json post
    The only param is "id", the rest of the info gets picked up from
    the database using that id.
    """

    transform_id = request.args.get('id', None)
    if not transform_id:
        return "An id parameter is required", 400




if __name__ -- "__main__":
    app.run(debug=True)