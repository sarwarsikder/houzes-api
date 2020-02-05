import json
import os
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/get-lat-long')
def get_lat_long():
    address = request.args.get('address')
    if address:
        subprocess.check_output(['scrapy', 'crawl', 'lat-long', "-o", "output.json", "-a", "address=" + address])
        with open("output.json") as items_file:
            data = items_file.read()
            os.remove("output.json")
            return jsonify({'status': 200, 'data': json.loads(data)})
    else:
        return jsonify({'status': 500, 'data': 'Address Needed For Parsing'})


if __name__ == '__main__':
    app.run(debug=True)
