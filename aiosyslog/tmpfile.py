import os
import uuid

class TempFile:
    def __init__(self, data=None, path="/tmp"):
        """
        Initialize a TempFile object.
        
        :param data: Content to be written to the file (optional)
        :param path: Directory where the temporary file will be created (default: /tmp)
        """
        self.path = None
        self._data = data
        self._base_path = path
        self._file_created = False

    def save(self):
        """
        Create the file with the specified data.
        Generates a unique filename using UUID.
        
        :return: Full path to the created file
        """
        # Generate a unique filename using UUID
        filename = str(uuid.uuid4())
        self.path = os.path.join(self._base_path, filename)
        
        # Ensure the base directory exists
        os.makedirs(self._base_path, exist_ok=True)
        
        # Write data to the file if provided
        if self._data is not None:
            with open(self.path, 'w') as f:
                f.write(str(self._data))
        
        self._file_created = True
        return self.path

    def delete(self):
        """
        Delete the temporary file if it exists.
        """
        if self._file_created and self.path and os.path.exists(self.path):
            os.unlink(self.path)
            self._file_created = False
            self.path = None

    def __enter__(self):
        """
        Context manager entry point.
        Creates the file when entering the context.
        
        :return: Self
        """
        self.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        Deletes the file when exiting the context.
        """
        self.delete()

    @property
    def data(self):
        """
        Getter for the file data.
        
        :return: Content of the file
        """
        if self.path and os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return f.read()
        return self._data