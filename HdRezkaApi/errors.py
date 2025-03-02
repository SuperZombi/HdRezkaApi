class LoginRequiredError(Exception):
	def __init__(self): super().__init__("Login is required to access this page.")

class LoginFailed(Exception):
	def __init__(self, msg): super().__init__(msg)

class FetchFailed(Exception):
	def __init__(self): super().__init__("Failed to fetch stream!")

class CaptchaError(Exception):
	def __init__(self): super().__init__("Failed to bypass captcha!")

class HTTP(Exception):
	def __init__(self, code, message=""): super().__init__(f"{code}: {message}")
