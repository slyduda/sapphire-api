from dotenv import dotenv_values

import quart.flask_patch
from quart import Quart

from routes.event import event

class DictToObjectConverter:
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)

app = Quart(__name__)
app.config.from_object(DictToObjectConverter(dotenv_values(".env")))
app.register_blueprint(event, url_prefix='/v1')
print(app.config)

@app.route('/', methods=['GET'])
async def index():
    return 'Hello World'

if __name__ == '__main__':
    from argparse import ArgumentParser
    # Load this config object for development mode
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=3000)
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)