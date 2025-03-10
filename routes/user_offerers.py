from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models.pc_object import PcObject
from models.user_offerer import UserOfferer
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.includes import USER_OFFERER_INCLUDES


@app.route('/userOfferers/<offerer_id>', methods=['GET'])
@login_required
def get_user_offerer(offerer_id):
    user_offerers = UserOfferer.query.filter_by(
        user=current_user,
        offererId=dehumanize(offerer_id)
    ).all()
    return jsonify([as_dict(user_offerer, includes=USER_OFFERER_INCLUDES) for user_offerer in user_offerers]), 200


@app.route('/userOfferers', methods=['POST'])
@login_required
def create_user_offerer():
    new_user_offerer = UserOfferer(from_dict=request.json)
    PcObject.save(new_user_offerer)
    return jsonify(as_dict(new_user_offerer, includes=USER_OFFERER_INCLUDES)), 201
