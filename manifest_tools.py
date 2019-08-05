import json


def index_manifest_canvases(manifest_raw):
    # Parse IIIF Manifest
    manifest = json.loads(manifest_raw)
    canvases = []
    for sequence in manifest['sequences']:
        canvases.extend([canvas['@id'] for canvas in sequence['canvases']])

    return canvases
