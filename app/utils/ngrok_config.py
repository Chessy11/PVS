class Config:
    ngrok_url = None
    
def set_ngrok_url(url):
    Config.ngrok_url = url
    
def get_ngrok_url():
    return Config.ngrok_url