import json
import xml.etree.ElementTree as ET


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
