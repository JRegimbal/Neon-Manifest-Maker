import json
import xml.etree.ElementTree as ET
from datetime import datetime
from uuid import uuid4


class CanvasNotFoundError(Exception):
    pass


class MEISourceError(Exception):
    pass


def index_manifest_canvases(manifest_raw):
    # Parse IIIF Manifest
    manifest = json.loads(manifest_raw)
    canvases = []
    for sequence in manifest['sequences']:
        canvases.extend([canvas['@id'] for canvas in sequence['canvases']])

    return canvases


def extract_canvas_from_mei(mei_raw):
    root = ET.fromstring(mei_raw)
    sources = root.findall(
        './/{http://www.music-encoding.org/ns/mei}source[@recordtype="m"]'
    )
    if len(sources) != 1:
        raise MEISourceError("Expected 1 source tag with recordtype 'm' but \
            got " + str(len(sources)) + ".")
    source = sources[0]
    if source.get('auth.uri') is None:
        raise MEISourceError("Source did not have attribute 'auth.uri'.")
    assert source.get('auth.uri') is not None
    return source.get('auth.uri')


def generate_annotation(mei_uri, canvas_uri, canvases):
    try:
        canvases.index(canvas_uri)
    except ValueError:
        raise CanvasNotFoundError("Could not find canvas '" + canvas_uri + "'")

    return {
        'id': 'urn:uuid:' + str(uuid4()),
        'type': 'Annotation',
        'body': mei_uri,
        'target': canvas_uri
    }


def generate_manifest_json(annotations, image, title='Generated Manifest',
                           id=None, indent=4):
    manifest = {
        '@context': [
            'http://www.w3.org/ns/anno.jsonld',
            {
                'schema': 'http://schema.org/',
                'title': 'schema:name',
                'timestamp': 'schema:dateModified',
                'image': {
                    '@id': 'schema:image',
                    '@type': '@id'
                },
                'mei_annotations': {
                    '@id': 'Annotation',
                    '@type': '@id',
                    '@container': '@list'
                }
            }
        ]
    }

    manifest['title'] = title
    if id is None:
        id = 'urn:uuid:' + str(uuid4())
    manifest['@id'] = id
    manifest['timestamp'] = datetime.utcnow().isoformat()
    manifest['image'] = image
    manifest['mei_annotations'] = annotations
    return json.dumps(manifest, indent=indent)
