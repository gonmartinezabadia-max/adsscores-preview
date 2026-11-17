import pathlib, tempfile, unittest
from required_assets import prepare, verify, MANIFEST
class RequiredAssetsTests(unittest.TestCase):
    def test_prepare_and_verify(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d); prepare(root); verify(root)
    def test_each_missing_resource_rejected(self):
        for name in MANIFEST:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                root=pathlib.Path(d);prepare(root);(root/name).unlink()
                with self.assertRaises(SystemExit): verify(root)
    def test_each_altered_resource_rejected(self):
        for name in MANIFEST:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                root=pathlib.Path(d);prepare(root);(root/name).write_bytes(b'changed')
                with self.assertRaises(SystemExit): verify(root)
    def test_prepare_repairs_incomplete_export(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);(root/next(iter(MANIFEST))).write_bytes(b'changed');prepare(root);verify(root)
if __name__=='__main__':unittest.main()
