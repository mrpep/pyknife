from pathlib import Path
import tqdm

class CompressedFile:
    def __init__(self,path):
        self.file = Path(path)
        self.extension = self.file.suffix
    def extract(self,destination_path):
        destination_path = Path(destination_path)
        if not destination_path.exists():
            destination_path.mkdir(parents=True)
        if self.extension == '.gz':
            import tarfile
            tar = tarfile.open(self.file)
            tar_members = tar.getnames()
            for member in tqdm.tqdm(tar_members):
                if not Path(destination_path,member).expanduser().exists():
                    tar.extract(member,destination_path)
            tar.close()
        elif self.extension == '.zip':
			import zipfile
			zip_file = zipfile.ZipFile(self.file)
			zip_members = zip_file.namelist()
			for member in tqdm.tqdm(zip_members):
				if not Path(destination_path,member).expanduser().exists():
					zip_file.extract(member,destination_path)
			zip_file.close()