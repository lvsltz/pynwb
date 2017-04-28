import unittest

from pynwb.spec import GroupSpec, DatasetSpec, AttributeSpec, Spec
from pynwb.spec.spec import SpecCatalog

import json

class AttributeSpecTests(unittest.TestCase):

    def test_constructor(self):
        spec = AttributeSpec('attribute1',
                             'str',
                             'my first attribute')
        self.assertEqual(spec['name'], 'attribute1')
        self.assertEqual(spec['dtype'], 'str')
        self.assertEqual(spec['doc'], 'my first attribute')
        self.assertIsNone(spec.parent)
        json.dumps(spec)


class DatasetSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'str', 'my first attribute'),
            AttributeSpec('attribute2', 'str', 'my second attribute')
        ]

    def test_constructor(self):
        spec = DatasetSpec('my first dataset',
                           'int',
                           name='dataset1',
                           attributes=self.attributes)
        self.assertEqual(spec['dtype'], 'int')
        self.assertEqual(spec['name'], 'dataset1')
        self.assertEqual(spec['doc'], 'my first dataset')
        self.assertNotIn('linkable', spec)
        self.assertNotIn('neurodata_type_def', spec)
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        json.dumps(spec)

    def test_constructor_nwbtype(self):
        spec = DatasetSpec('my first dataset',
                           'int',
                           name='dataset1',
                           dimension=(None, None),
                           attributes=self.attributes,
                           linkable=False,
                           neurodata_type_def='EphysData')
        self.assertEqual(spec['dtype'], 'int')
        self.assertEqual(spec['name'], 'dataset1')
        self.assertEqual(spec['doc'], 'my first dataset')
        self.assertEqual(spec['neurodata_type_def'], 'EphysData')
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        json.dumps(spec)

class GroupSpecTests(unittest.TestCase):
    def setUp(self):
        self.attributes = [
            AttributeSpec('attribute1', 'str', 'my first attribute'),
            AttributeSpec('attribute2', 'str', 'my second attribute')
        ]

        dset1_attributes = [
            AttributeSpec('attribute3', 'str', 'my third attribute'),
            AttributeSpec('attribute4', 'str', 'my fourth attribute')
        ]

        dset2_attributes = [
            AttributeSpec('attribute5', 'str', 'my fifth attribute'),
            AttributeSpec('attribute6', 'str', 'my sixth attribute')
        ]

        self.datasets = [
            DatasetSpec('my first dataset',
                        'int',
                        name='dataset1',
                        attributes=dset1_attributes,
                        linkable=True),
            DatasetSpec('my second dataset',
                        'int',
                        name='dataset2',
                        dimension=(None, None),
                        attributes=dset2_attributes,
                        linkable=True,
                        neurodata_type_def='EphysData')
        ]

        self.subgroups = [
            GroupSpec('A test subgroup',
                      name='subgroup1',
                      linkable=False),
            GroupSpec('A test subgroup',
                      name='subgroup2',
                      linkable=False)

        ]

    def test_constructor(self):
        spec = GroupSpec('A test group',
                          name='root_constructor',
                         groups=self.subgroups,
                         datasets=self.datasets,
                         attributes=self.attributes,
                         linkable=False)
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertNotIn('neurodata_type_def', spec)
        self.assertIs(spec, self.subgroups[0].parent)
        self.assertIs(spec, self.subgroups[1].parent)
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        self.assertIs(spec, self.datasets[0].parent)
        self.assertIs(spec, self.datasets[1].parent)
        json.dumps(spec)

    def test_constructor_nwbtype(self):
        spec = GroupSpec('A test group',
                         name='root_constructor_nwbtype',
                         datasets=self.datasets,
                         attributes=self.attributes,
                         linkable=False,
                         neurodata_type_def='EphysData')
        self.assertFalse(spec['linkable'])
        self.assertListEqual(spec['attributes'], self.attributes)
        self.assertListEqual(spec['datasets'], self.datasets)
        self.assertEqual(spec['neurodata_type_def'], 'EphysData')
        self.assertIs(spec, self.attributes[0].parent)
        self.assertIs(spec, self.attributes[1].parent)
        self.assertIs(spec, self.datasets[0].parent)
        self.assertIs(spec, self.datasets[1].parent)
        json.dumps(spec)

    def test_set_dataset(self):
        spec = GroupSpec('A test group',
                         name='root_test_set_dataset',
                         linkable=False,
                         neurodata_type_def='EphysData')
        spec.set_dataset(self.datasets[0])
        self.assertIs(spec, self.datasets[0].parent)

    def test_set_group(self):
        spec = GroupSpec('A test group',
                         name='root_test_set_group',
                         linkable=False,
                         neurodata_type_def='EphysData')
        spec.set_group(self.subgroups[0])
        spec.set_group(self.subgroups[1])
        self.assertListEqual(spec['groups'], self.subgroups)
        self.assertIs(spec, self.subgroups[0].parent)
        self.assertIs(spec, self.subgroups[1].parent)
        json.dumps(spec)

class SpecCatalogTest(unittest.TestCase):

    def setUp(self):
        self.catalog = SpecCatalog()
        self.attributes = [
            AttributeSpec('attribute1', 'str', 'my first attribute'),
            AttributeSpec('attribute2', 'str', 'my second attribute')
        ]
        self.spec = DatasetSpec('my first dataset',
                           'int',
                           name='dataset1',
                           dimension=(None, None),
                           attributes=self.attributes,
                           linkable=False,
                           neurodata_type_def='EphysData')

    def test_register_spec(self):
        self.catalog.register_spec('EphysData', self.spec)
        result = self.catalog.get_spec('EphysData')
        self.assertIs(result, self.spec)

    def test_hierarchy(self):
        spikes_spec = DatasetSpec('my extending dataset', 'int',
                                neurodata_type='EphysData',
                                neurodata_type_def='SpikeData')

        lfp_spec = DatasetSpec('my second extending dataset', 'int',
                                neurodata_type='EphysData',
                                neurodata_type_def='LFPData')

        self.catalog.register_spec('EphysData', self.spec)
        self.catalog.register_spec('SpikeData', spikes_spec)
        self.catalog.register_spec('LFPData', lfp_spec)

        spike_hierarchy = self.catalog.get_hierarchy('SpikeData')
        lfp_hierarchy = self.catalog.get_hierarchy('LFPData')
        ephys_hierarchy = self.catalog.get_hierarchy('EphysData')
        self.assertTupleEqual(spike_hierarchy, ('SpikeData', 'EphysData'))
        self.assertTupleEqual(lfp_hierarchy, ('LFPData', 'EphysData'))
        self.assertTupleEqual(ephys_hierarchy, ('EphysData',))

if __name__ == '__main__':
    unittest.main()
