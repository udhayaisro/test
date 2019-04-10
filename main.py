from brewtils.plugin import RemotePlugin
from brewtils.decorators import command, system,parameter
import os
import stat
import json
from datetime import datetime
from array import array


@system 
class FileUtilities(object):
	
	@parameter(key="path",description="Enter the file Path",type="String")

	@command(description="Check if file path is valid")
	def exists_in_directory(self,path):
    		if os.path.exists(path):
        		return True, 'Exists'
    		else:
        		return False, 'NotExists'
	
	@parameter(key="filename",description="Enter the FileName",type="String")

	@command(description="Creates a new file")
	def create(self,filename, contents=None, overwrite=False):
    		if (not overwrite) and os.path.exists(filename):
        		return False, 'AlreadyExists'
    		else:
        		try:
            			with open(filename, 'w') as new_file:
                			new_file.write(contents)
            			return True, 'FileCreated'
        		except IOError:
            			print("Error writing or creating file.")
            			return False, 'Error'


	@parameter(key="filename",description="Enter the FileName to append",type="String")
	@parameter(key="contents",description="Write the content that you want to append",type="String")

	@command(description="Append content into the file")
	def append(self,filename, contents, newline=False):
    		try:
        		with open(filename, 'a') as f:
            			if newline:
                			f.write("\n")
            			f.write(contents)
        		return True, 'FileWritten'
    		except IOError:
        		print("Error writing file.")
        		return False, 'Error'
        
	@parameter(key="filename",description="Enter the FileName to remove",type="String")
	@command(description="Remove a file from the directory")
	def remove(self,filename):
    		try:
        		os.remove(filename)
        		return True, 'Success'
    		except IOError:
        		print("Error deleting file")
        		return False, 'Error'
	
	@parameter(key="filename",description="Enter the FileName to make it Read-Only",type="String")

	@command(description="Making file read only")
	def make_read_only(self,filename):
    		try:
        		READ_ONLY = ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
        		cur_perms = stat.S_IMODE(os.lstat(filename).st_mode)
        		os.chmod(filename, cur_perms & READ_ONLY)
        		return True, 'Success'
    		except IOError:
        		print("Error making file read only")
        		return False, 'Error'

	@parameter(key="filename",description="Enter the FileName to make it writable",type="String")	
	
	@command(description="Making file writable only")
	def make_writable(self,filename):
    		try:
        		WRITE_ALLOWED = stat.S_IWUSR | stat.S_IWGRP
        		cur_perms = stat.S_IMODE(os.lstat(filename).st_mode)
        		os.chmod(filename, cur_perms | WRITE_ALLOWED)
        		return True, 'Success'
    		except IOError:
        		print("Error making file writable")
        		return False, 'Error'
	
	@parameter(key="elements",description="Enter the path to join",type="String")

	@command(description="Join the file path elements")
	def join_path_elements(self,elements):
    		print(elements)
    		return os.path.join(*elements)

	@parameter(key="path_from",description="Enter the file path to move",type="String")	
	@parameter(key="path_to",description="Enter the destination path to move the file",type="String")	
	
	@command
	def copy_and_bitswap(self,path_from, path_to):
    		if not os.path.exists(path_from) or not os.path.isfile(path_from):
        		return 'File not found', 'FileNotFound'

    		with open(path_from, 'rb') as file_in:
        		exe_bytes = array('B', file_in.read())

    		exe_bytes.byteswap()

    		if not path_to:
        		path = os.path.join('.', 'apps', 'FileUtilities', 'data')
        		filename = '{}-quarantine.bin'.format(os.path.basename(path_from).split('.')[0])
        		if not os.path.exists(path):
            			os.mkdir(path)
        		filename = os.path.join(path, filename)
    		else:
        		dirname = os.path.dirname(path_to)
        		if dirname and not os.path.exists(dirname):
            			os.mkdir(dirname)
        		filename = path_to

    		with open(filename, 'wb') as file_out:
        		exe_bytes.tofile(file_out)

    		return filename

	@parameter(key="filename",description="Enter the Json filename to read",type="String")

	@command(description="Reading Json Files")
	def read_json(self,filename):
    		if not os.path.exists(filename) or not os.path.isfile(filename):
        		return 'File does not exist', 'FileDoesNotExist'
    		try:
        		with open(filename, 'r') as file_in:
            			return json.loads(file_in.read())
    		except (IOError, IOError) as e:
        		return {'error': 'Could not read file', 'reason': format_exception_message(e)}, 'FileDoesNotExist'
    		except ValueError:
        		return 'Could not read file as json. Invalid JSON', 'InvalidJson'
	
	@parameter(key="filename",description="Enter the Json filename to write",type="String")
	@parameter(key="data",description="Enter the Json data to write into the file",type="String")

	@command(description="Writing New Json File")
	def write_json(self,data, filename):
    		dirname = os.path.dirname(filename)
    		if dirname and not os.path.exists(dirname):
                	os.mkdir(dirname)
    		with open(filename, 'w') as config_file:
      	        	config_file.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
	return 'Success'

	def stats(filename):
		def add_if_exists(stat, attr, name, results):
        		if hasattr(stat, attr):
        			results[name] = getattr(stat, attr)

		def add_time_if_exists(stat, attr, name, results):
    	        	if hasattr(stat, attr):
		    	results[name] = str(datetime.fromtimestamp(getattr(stat, attr)))

		if os.path.exists(filename):
        		stats = os.stat(filename)
        		result = {}
        		add_if_exists(stats, 'st_mode', 'mode', result)
        		add_if_exists(stats, 'st_ino', 'inode', result)
        		add_if_exists(stats, 'st_dev', 'device', result)
        		add_if_exists(stats, 'st_nlink', 'num_links', result)
        		add_if_exists(stats, 'st_uid', 'uid', result)
        		add_if_exists(stats, 'st_gid', 'gid', result)
        		add_if_exists(stats, 'st_size', 'size', result)
        		add_if_exists(stats, 'st_blocks', 'blocks', result)
        		add_if_exists(stats, 'st_blksize', 'block_size', result)
        		add_if_exists(stats, 'st_rdev', 'device_type', result)
        		add_if_exists(stats, 'st_flags', 'flags', result)
        		add_time_if_exists(stats, 'st_atime', 'access_time', result)
        		add_time_if_exists(stats, 'st_mtime', 'modification_time', result)
        		add_time_if_exists(stats, 'st_ctime', 'metadata_time', result)

        		return result
    		else:
			return 'File does not exist', 'FileDoesNotExist'

def main():
    plugin = RemotePlugin(FileUtilities(),
                          name='FileUtilities',
                          version='1.0.0',
                          description='Working around File operations',
                          bg_host="localhost",
                          bg_port="2337",
                          ssl_enabled='false',
                          max_concurrent=5,
                          metadata={'foo': 'bar'})
    plugin.run()

if __name__ == "__main__":
    main()
