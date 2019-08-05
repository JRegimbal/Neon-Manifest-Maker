import json
import xml.etree.ElementTree as ET
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
    except ValueError e:
        throw CanvasNotFoundError()

    return {
        'id': 'urn:uuid' + str(uuid4()),
        'type': 'Annotation',
        'body': mei_uri,
        'target': canvas_uri
    }
