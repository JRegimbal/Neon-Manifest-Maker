from rodan.jobs.base import RodanTask


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
