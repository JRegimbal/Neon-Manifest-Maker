from datetime import datetime
from rodan.jobs.base import RodanTask
from rodan.models import RunJob
from .manifest_tools import *
import json


class ManifestMaker(RodanTask):
    name = 'Neon Manifest Maker'
    author = 'Juliette Regimbal'
    description = 'Make a Neon manifest from MEI files'
    settings = {
        'job_queue': 'Python3'
    }
    enabled = True
    category = 'Miscellaneous'
    interactive = False

    input_port_types = [
        {
            'name': 'MEI',
            'minimum': 1,
            'maximum': 200,
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

    def run(self, runjob_id):
        self.runjob_id = runjob_id
        super(ManifestMaker, self).run(runjob_id)

    def run_my_task(self, inputs, settings, outputs):
        runjob = RunJob.objects.get(uuid=self.runjob_id)
        url_inputs = self._inputs(runjob, with_urls=True)
        manifest = open(inputs['IIIF Manifest'][0]['resource_path'], 'r')
        canvases = index_manifest_canvases(manifest.read())
        manifest.close()

        annotations = []
        for mei_input in url_inputs['MEI']:
            mei_file = open(mei_input['resource_path'], 'r')
            canvas = extract_canvas_from_mei(mei_file.read())
            annotations.append(generate_annotation(
                mei_input['resource_url'],
                canvas,
                canvases
            ))
            canvases.remove(canvas)

        manifest_jsonld = generate_manifest_json(
            annotations,
            url_inputs['IIIF Manifest'][0]['resource_url'],
            title='Rodan-generated Manifest',
            indent=4
        )

        manifest_file = open(outputs['Neon Manifest'][0]['resource_path'], 'w')
        manifest_file.write(manifest_jsonld)
        manifest_file.close()
        return True
