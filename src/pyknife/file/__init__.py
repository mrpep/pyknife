from pathlib import Path
import tqdm

class CompressedFile:
    """
    Class to wrap compressed files
    """
    def __init__(self,path):
        """
        path: path to the compressed file
        """
        self.file = Path(path).expanduser()
        self.extension = self.file.suffix

    def add_file(self,filename,filename_inside):
        """
        add file to the container (supports .zip)
        filename:        path to the file to include in the container
        filename_inside: name of the file when inside the container
        """
        if self.extension == '.zip':
            zip_file = zipfile.ZipFile(self.file(),'w')
            zip_file.write(filename,arcname=filename_inside)
            zip_file.close()

    def extract(self,destination_path):
        """
        extract files in container (supports .zip and .gz)
        destination_file: path where the files will be extracted
        """
        destination_path = Path(destination_path).expanduser()
        if not destination_path.exists():
            destination_path.mkdir(parents=True)
        if self.extension == '.gz':
            import tarfile
            tar = tarfile.open(self.file)
            tar_members = tar.getnames()
            for member in tqdm.tqdm(tar_members):
                if not Path(destination_path,member).exists():
                    tar.extract(member,destination_path)
            tar.close()
        elif self.extension == '.zip':
            import zipfile
            zip_file = zipfile.ZipFile(self.file)
            zip_members = zip_file.namelist()
            for member in tqdm.tqdm(zip_members):
                if not Path(destination_path,member).exists():
                    zip_file.extract(member,destination_path)
            zip_file.close()