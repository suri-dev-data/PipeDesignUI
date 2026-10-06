import webview
from models import Pipe

class PipeController:
    def __init__(self, pipe: Pipe):
        self.pipe = pipe

    def get_dashboard_state(self):
        """Called by PyWebview JS to get full initial state"""
        return self.pipe.get_state()
        
    def get_materials(self):
        """Called by PyWebview JS to get material library"""
        from models import get_all_materials
        import dataclasses
        return [dataclasses.asdict(m) for m in get_all_materials()]

    def get_user(self):
        from models import get_user
        import dataclasses
        return dataclasses.asdict(get_user())

    def update_user_photo(self, base64_data: str):
        from database import get_db_connection
        conn = get_db_connection()
        conn.execute('UPDATE users SET photo_url = ? WHERE id = 1', (base64_data,))
        conn.commit()
        conn.close()
        return True

    def add_layer(self, name: str, material: str, thickness: int, color_hex: str):
        """Called by PyWebview JS to add a new layer"""
        self.pipe.add_layer(name, material, thickness, color_hex)
        return self.get_dashboard_state()

    def delete_layer(self, layer_id: int):
        """Called by PyWebview JS to delete a layer"""
        self.pipe.delete_layer(layer_id)
        return self.get_dashboard_state()

    def minimize_window(self):
        for window in webview.windows:
            window.minimize()
            
    def close_window(self):
        for window in webview.windows:
            window.destroy()
