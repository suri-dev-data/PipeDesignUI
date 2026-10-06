import webview
import os
from models import Pipe
from controller import PipeController

from database import init_db

def main():
    # Initialize Database
    init_db()
    
    # Instantiate Model
    pipe_model = Pipe()
    
    # Instantiate Controller
    controller = PipeController(pipe_model)
    
    # Get absolute path to the local HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, 'ui.html')
    
    # Create and start the webview window
    webview.create_window(
        'Pipe Builder OS - Desktop', 
        url=f'file://{html_file}', 
        js_api=controller,
        width=1366, 
        height=768,
        min_size=(1024, 768),
        fullscreen=True
    )
    
    webview.start(debug=False)

if __name__ == '__main__':
    main()
