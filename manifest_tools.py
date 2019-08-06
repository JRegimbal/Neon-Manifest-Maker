import json
import xml.etree.ElementTree as ET
from datetime import datetime
from uuid import uuid4


class CanvasNotFoundError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


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
    assert len(sources) == 1
    source = sources[0]
    assert source.get('auth.uri') is not None
    return source.get('auth.uri')


def generate_annotation(mei_uri, canvas_uri, canvases):
    try:
        canvases.index(canvas_uri)
    except ValueError:
        raise CanvasNotFoundError

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
