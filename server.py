"""Create a wsgi server to upload data to a client."""

import os
import flask

app = flask.Flask(__name__)

PORT = int(os.getenv('PORT', 4444))
WORKDIR = os.getenv('WORKDIR', os.getcwd())
MAXSIZE = int(os.getenv('MAXSIZE', 2))

tokens = [
    fname for fname in os.listdir(WORKDIR)
    if fname.endswith('.txt')
]


def create_route(token):
    """Create a route for a token.

    The route will stream CSV text contents to the client.
    Once sent, the data is lost.

    This script is run on a worker (ie. your raspberry pi)
    And serves data to the master (ie. your desktop)
    """
    def serve_token():
        """Return token data."""
        tempname = '{}.tmp'.format(token)
        origname = '{}.orig'.format(token)

        def generate():
            """Yield data line by line until full. Write rest back to disk."""
            with open(os.path.join(WORKDIR, tempname), 'w') as outfile:
                with open(os.path.join(WORKDIR, token)) as tokenfile:
                    for idx, line in enumerate(tokenfile):
                        if idx < MAXSIZE:
                            yield line
                        else:
                            outfile.write(line)

            # Swap outfile into source file.
            os.rename(
                os.path.join(WORKDIR, token),
                os.path.join(WORKDIR, origname)
            )
            os.rename(
                os.path.join(WORKDIR, tempname),
                os.path.join(WORKDIR, token)
            )
            os.remove(os.path.join(WORKDIR, origname))

        # Start streaming the response to the client.
        return flask.Response("".join(generate()), mimetype='text/csv')
    return serve_token


@app.route('/')
def root():
    """Show the available tokens."""
    return flask.jsonify({'links': tokens})


for token in tokens:
    # Create a route to stream stream token.
    app.route('/{}'.format(token))(
        create_route(token)
    )


if __name__ == '__main__':
    app.run(port=PORT)
