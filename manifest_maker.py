from datetime import datetime
from rodan.jobs.base import RodanTask
import manifest_tools as tools
import json


class ManifestMaker(RodanTask):
    name = 'Neon Manifest Maker'
    author = 'Juliette Regimbal'
    description = 'Make a Neon manifest from MEI files'
    settings = {}
    enabled = True
    category = 'Miscellaneous'
    interactive = False

    input_port_types = [
        {
            'name': 'MEI',
            'minimum': 1,
            'maximum': 0,
            'resource_types': ['application/mei+xml']
        },
        {
            'name': 'IIIF Manifest',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/json']
        }
    ]

    output_port_types = [
        {
            'name': 'Neon Manifest',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/ld+json']
        }
    ]

    def run_my_task(self, inputs, settings, outputs):
        manifest = open(inputs['IIIF Manifest'][0]['resource_path'], 'r')
        canvases = tools.index_manifest_canvases(manifest.read())
        manifest.close()

        annotations = []
        for mei_input in inputs['MEI']:
            mei_file = open(mei_input['resource_path'], 'r')
            canvas = tools.extract_canvas_from_mei(mei_file.read())
            annotations.append(tools.generate_annotation(
                mei_input['resource_url'],
                canvas,
                canvases
            ))
            canvases.remove(canvas)

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
        manifest['title'] = 'Rodan-generated Manifest'
        manifest['@id'] = outputs['Neon Manifest'][0]['resource_url']
        manifest['timestamp'] = datetime.utcnow().isoformat()
        manifest['mei_annotations'] = annotations

        manifest_jsonld = json.dumps(manifest, indent=4)

        manifest_file = open(outputs['Neon Manifest'][0]['resource_path'], 'w')
        manifest_file.write(manifest_jsonld)
        manifest_file.close()
        return True
