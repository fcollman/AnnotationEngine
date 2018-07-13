from flask import Blueprint, jsonify, request, abort
from annotationengine.schemas import get_schema, get_schemas
from annotationengine.database import get_db
from annotationengine.dataset import get_datasets, get_dataset_db
from emannotationschemas.errors import UnknownAnnotationTypeException
import numpy as np
import json
from functools import partial
import pandas as pd

bp = Blueprint("annotation", __name__, url_prefix="/annotation")


def collect_supervoxels(d):
    svid_set = collect_supervoxels_recursive(d)
    return np.array(list(svid_set), dtype=np.uint64)


def collect_supervoxels_recursive(d, svids=None):
    if svids is None:
        svids = set()
    for k, v in d.items():
        if k == 'supervoxel_id':
            svids.add(v)
        if type(v) is dict:
            svids = collect_supervoxels_recursive(v, svids)
    return svids


@bp.route("/datasets")
def get_annotation_datasets():
    return get_datasets()


def bsp_import_fn(cv, item):
    item.pop('root_id', None)
    svid = cv.lookup_supervoxel(*item['position'])
    item['supervoxel_id'] = svid


def get_schema_with_context(annotation_type, dataset, flatten=False):
    dataset_db = get_dataset_db()
    cv = dataset_db.get_cloudvolume(dataset)
    myp = partial(bsp_import_fn, cv)

    context = {'bsp_fn': myp, 'flatten': flatten}
    Schema = get_schema(annotation_type)
    schema = Schema(context=context)
    return schema


@bp.route("/dataset/<dataset>")
def get_annotation_types(dataset):
    return get_schemas()


def nest_dictionary(d, key_path=None, sep="."):
    if key_path is None:
        key_path = []
    d_new = {}
    for k, v in d.items():
        sub_keys = k.split(sep)
        ds = d_new
        for sub_key in sub_keys[:-1]:
            if sub_key not in ds.keys():
                ds[sub_key] = {}
            ds = ds[sub_key]
        ds[sub_keys[-1]] = v
    return d_new


def import_dataframe(db, dataset, annotation_type, schema, df):
    annotations = []
    for k, row in df.iterrows():
        d = nest_dictionary(dict(row))
        d['type'] = annotation_type
        result = schema.load(d)
        if len(result.errors) > 0:
            abort(422, result.errors)
        ann = result.data
        supervoxels = collect_supervoxels(ann)
        blob = json.dumps(schema.dump(ann).data)
        annotations.append((supervoxels, blob))

    return annotations


@bp.route("/dataset/<dataset>/<annotation_type>", methods=["POST"])
def import_annotations(dataset, annotation_type):
    db = get_db()
    is_bulk = request.args.get('bulk', 'false') == 'true'

    if request.method == "POST":
        user_id = jsonify(origin=request.headers.get('X-Forwarded-For',
                                                     request.remote_addr))
        # iterate through annotations in json posted
        try:
            schema = get_schema_with_context(annotation_type,
                                             dataset)
        except UnknownAnnotationTypeException as m:
            abort(404, str(m))
        d = request.json
        if is_bulk:
            df = pd.read_json(d)
            annotations = import_dataframe(db, dataset,
                                           annotation_type, schema, df)
        else:
            result = schema.load(d, many=True)
            if len(result.errors) > 0:
                abort(422, result.errors)

            annotations = []
            for ann in result.data:
                supervoxels = collect_supervoxels(ann)
                blob = json.dumps(schema.dump(ann).data)
                annotations.append((supervoxels, blob))
        uids = db.insert_annotations(dataset,
                                     annotation_type,
                                     annotations,
                                     user_id)
        return jsonify(np.uint64(uids).tolist())


@bp.route("/dataset/<dataset>/<annotation_type>/<oid>",
          methods=["GET", "PUT", "DELETE"])
def get_annotation(dataset, annotation_type, oid):
    db = get_db()
    user_id = jsonify(origin=request.headers.get('X-Forwarded-For',
                                                 request.remote_addr))
    if request.method == "PUT":
        try:
            schema = get_schema_with_context(annotation_type, dataset)
        except UnknownAnnotationTypeException:
            abort(404)

        result = schema.load(request.json)
        if len(result.errors) > 0:
            abort(422, result.errors)

        ann = result.data
        annotations = [(np.uint64(oid),
                        collect_supervoxels(result.data),
                        json.dumps(schema.dump(ann).data))]

        success = db.update_annotations(dataset,
                                        annotation_type,
                                        annotations,
                                        user_id)

        return jsonify(success)

    if request.method == "DELETE":

        success = db.delete_annotations(dataset,
                                        annotation_type,
                                        np.array([int(oid)], np.uint64),
                                        user_id)
        if success[0]:
            return jsonify(success[0])
        else:
            abort(404)

    if request.method == "GET":
        ann = db.get_annotation_data(dataset,
                                     annotation_type,
                                     int(oid))
        if ann is None:
            msg = 'annotation {} ({}) not in {}'
            msg = msg.format(oid, annotation_type, dataset)
            abort(404, msg)
        schema = get_schema_with_context(annotation_type, dataset)
        ann = json.loads(ann)
        ann['oid'] = oid
        return jsonify(schema.dump(ann)[0])
