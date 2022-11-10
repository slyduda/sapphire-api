from dotenv import dotenv_values

import quart.flask_patch
from quart import Quart
from quart_cors import cors

from routes.event import event
from utils.general import DictToObjectConverter

app = Quart(__name__)
app.config.from_object(DictToObjectConverter(dotenv_values(".env")))
app.register_blueprint(event, url_prefix='/v1')
print(app.config.get('ENV'))

app = cors(app,
    allow_headers=["content-type", "x-csrf-token"],
    allow_methods=["POST", "PUT", "DELETE", "GET"],
    allow_origin='*'
    )

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