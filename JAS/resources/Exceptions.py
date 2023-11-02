import traceback

def exception_msg(code, str):
	codeline = f'>> Error: {code}'
	errorline = f'==={str[0]}==='
	return codeline+' : '+errorline

# General 00
class ConnectionError(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E00-000'
	def __str__(self):
		return exception_msg(self.code, self.args)
		
class NoToken(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E00-001'
	def __str__(self):
		return exception_msg(self.code, self.args)
		
class IncorrectPlace(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E00-003'
	def __str__(self):
		return exception_msg(self.code, self.args)
		
# Manage 09
class NoUser(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E09-001'
	def __str__(self):
		return exception_msg(self.code, self.args)
		
class VaildationError(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E09-002'
	def __str__(self):
		return exception_msg(self.code, self.args)

# fishing 01    
class FishingLimit(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E01-001'
	def __str__(self):
		return exception_msg(self.code, self.args)

class FishingError(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E01-002'
	def __str__(self):
		return exception_msg(self.code, self.args)

class CannotAddFish(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E01-003'
	def __str__(self):
		return exception_msg(self.code, self.args)

class CannotChangeFish(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E01-004'
	def __str__(self):
		return exception_msg(self.code, self.args)

class CannotDeleteFish(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E01-005'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
class FishNotFOund(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E01-404'
	def __str__(self):
		return exception_msg(self.code, self.args)

# gather 02
class GatherLimit(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E02-001'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
class GatherError(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E02-002'
	def __str__(self):
		return exception_msg(self.code, self.args)

class CannotAddGather(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E02-003'
	def __str__(self):
		return exception_msg(self.code, self.args)

class CannotChangeGather(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E02-004'
	def __str__(self):
		return exception_msg(self.code, self.args)

class CannotDeleteGather(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E02-005'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
# inventory 03
class NotEnoughGold(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E03-001'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
class NotEnoughSpace(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E03-001'
	def __str__(self):
		return exception_msg(self.code, self.args)

class SellingError(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E03-002'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
class ItemNotFound(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E03-003'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
# Community 05
class NoChara(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E05-001'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
# Licensing 90
class NoLicense(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E90-000'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
class IncorrectLicense(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E90-001'
	def __str__(self):
		return exception_msg(self.code, self.args)
	
class ExpiredLicense(Exception):
	def __init__(self, *args: object):
		self.args = args
		self.code = 'E90-002'
	def __str__(self):
		return exception_msg(self.code, self.args)