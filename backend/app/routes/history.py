from app.utils.History import History, get_overpass_turbo_args
from flask import Blueprint, abort, jsonify, request
import glob
import os
import json
from datetime import datetime

history = Blueprint('history', __name__)

@history.route('/api/history', methods=['GET'])
def get_history():
    history = {}

    hist = History()

    files = glob.glob(f"{hist.folder_path}/*.json")
    for file in files:
        try:
            with open(file, "r") as f:
                json_data = json.load(f)
                json_data.pop("data", None)

                datetime = json_data["datetime"]
                year = datetime[0:4]
                month = datetime[5:7]
                day = datetime[8:10]

                if year not in history:
                    history[year] = {}
                if month not in history[year]:
                    history[year][month] = {}
                if day not in history[year][month]:
                    history[year][month][day] = []

                history[year][month][day].append(json_data)
        except json.JSONDecodeError:
            continue
    return jsonify(history)

@history.route('/api/history', methods=['DELETE'])
def clear_history():
    hist = History()
    files = glob.glob(f"{hist.folder_path}/*.json")
    for file in files:
        os.remove(file)

    return jsonify({"message": "History cleared"})

@history.route('/api/history', methods=['POST'])
def add_history_element():
    hist = History()
    data = request.json
    if data is None:
        abort(400)

    service_name = data["service"]
    data.pop("service")

    service_args = get_overpass_turbo_args(service_name, data)

    hist.add_element(param_data=data, param_type=service_name, param_args=service_args)
    return jsonify({"message": "History element added"})

@history.route('/api/history/<uuid>', methods=['GET'])
def get_history_element(uuid):
    hist = History()
    file = glob.glob(f"{hist.folder_path}/{uuid}.json")
    if uuid == None or uuid == "" or len(file) == 0:
        abort(404)
    with open(file[0], "r") as f:
        return jsonify(json.load(f))

@history.route('/api/history/<uuid>', methods=['DELETE'])
def delete_history_element(uuid):
    hist = History()
    file = glob.glob(f"{hist.folder_path}/{uuid}.json")
    if uuid == None or id == "" or len(file) == 0:
        abort(404)
    os.remove(file[0])
    return jsonify({"message": "History element deleted"})

@history.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request, please ensure all parameters are provided"}), 400

@history.errorhandler(404)
def bad_request(error):
    return jsonify({"error": "History element not found"}), 404



@history.errorhandler(500)
def bad_request(error):
    return jsonify({"error": "Internal Server Error"}), 500