import dataclasses
import math
from typing import List, Dict, Any
from database import get_db_connection

@dataclasses.dataclass
class Material:
    id: int
    name: str
    category: str
    density: float # kg/m^3
    thermal_conductivity: float # W/(m.K)
    structural_strength: float # MPa
    color_hex: str

@dataclasses.dataclass
class User:
    id: int
    name: str
    code: str
    email: str
    site: str
    photo_url: str

def get_user(user_id=1) -> User:
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if row:
        return User(
            id=row['id'], name=row['name'], code=row['code'], email=row['email'],
            site=row['site'], photo_url=row['photo_url']
        )
    return None

def get_all_materials() -> List[Material]:
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM materials ORDER BY id').fetchall()
    conn.close()
    return [
        Material(
            id=row['id'], name=row['name'], category=row['category'],
            density=row['density'], thermal_conductivity=row['thermal_conductivity'],
            structural_strength=row['structural_strength'], color_hex=row['color_hex']
        ) for row in rows
    ]

@dataclasses.dataclass
class Layer:
    id: int
    pipe_id: int
    name: str
    material: str
    thickness: int
    color_hex: str
    dasharray: str = ""
    opacity: float = 0.8
    is_dashed: bool = False

class Pipe:
    def __init__(self, pipe_id: int = 1):
        self.pipe_id = pipe_id
        self.name = ""
        self.layers: List[Layer] = []
        self._load_from_db()

    def _load_from_db(self):
        conn = get_db_connection()
        pipe_row = conn.execute('SELECT * FROM pipes WHERE id = ?', (self.pipe_id,)).fetchone()
        if pipe_row:
            self.name = pipe_row['name']
        
        layer_rows = conn.execute('SELECT * FROM layers WHERE pipe_id = ? ORDER BY id', (self.pipe_id,)).fetchall()
        self.layers = []
        for row in layer_rows:
            self.layers.append(Layer(
                id=row['id'],
                pipe_id=row['pipe_id'],
                name=row['name'],
                material=row['material'],
                thickness=row['thickness'],
                color_hex=row['color_hex'],
                dasharray=row['dasharray'],
                opacity=row['opacity'],
                is_dashed=bool(row['is_dashed'])
            ))
        conn.close()

    def get_total_thickness(self) -> int:
        return sum(layer.thickness for layer in self.layers)

    def add_layer(self, name: str, material: str, thickness: int, color_hex: str):
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO layers (pipe_id, name, material, thickness, color_hex, dasharray, opacity, is_dashed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.pipe_id, name, material, int(thickness), color_hex, "", 0.8, False))
        conn.commit()
        conn.close()
        self._load_from_db()

    def delete_layer(self, layer_id: int):
        conn = get_db_connection()
        conn.execute('DELETE FROM layers WHERE id = ?', (layer_id,))
        conn.commit()
        conn.close()
        self._load_from_db()

    def calculate_svg_geometry(self) -> List[Dict[str, Any]]:
        """
        Calculates the exact radius and properties for each circle in the SVG.
        Returns them in the order they should be drawn (outermost first).
        """
        geometry = []
        
        # Calculate from inside to outside to perfectly stack layers without overlap
        current_inner_boundary = 50
        
        for layer in self.layers:
            thickness = layer.thickness
            color = layer.color_hex
            
            # The center of the stroke is exactly in the middle of the thickness
            r = current_inner_boundary + (thickness / 2.0)
            
            # Main circle
            geometry.append({
                "type": "main",
                "cx": 200,
                "cy": 200,
                "r": r,
                "stroke": color,
                "stroke_width": thickness,
                "opacity": 0.8,
                "name": layer.name,
                "material": layer.material,
                "thickness": thickness
            })
            
            # Dashed circle for insulation etc
            if layer.is_dashed:
                geometry.append({
                    "type": "dash",
                    "cx": 200,
                    "cy": 200,
                    "r": r,
                    "stroke": "#E8F0EA",  # On-background serene color
                    "stroke_width": thickness,
                    "stroke_dasharray": layer.dasharray,
                    "opacity": layer.opacity
                })
            
            current_inner_boundary += thickness
            
        # SVG draws elements in order (last element is on top).
        # We want the outermost layer to be drawn FIRST, so inner layers draw on top of it.
        return geometry[::-1]

    def get_metrics(self) -> Dict[str, Any]:
        total_thickness_mm = self.get_total_thickness()
        total_diameter_mm = 100 + (total_thickness_mm * 2) # Base ID = 100mm
        
        unit_weight = 0.0 # kg/m
        thermal_resistance = 0.0 # m.K/W
        max_strength = 0.0
        
        current_r_mm = 50.0
        
        material_library = get_all_materials()
        
        for layer in self.layers:
            mat = None
            for m in material_library:
                if m.name == layer.material:
                    mat = m
                    break
            
            if not mat:
                current_r_mm += layer.thickness
                continue
                
            r_inner_m = current_r_mm / 1000.0
            r_outer_m = (current_r_mm + layer.thickness) / 1000.0
            
            # Unit weight = volume per meter * density
            # volume = pi * (r_outer^2 - r_inner^2)
            vol = math.pi * (r_outer_m**2 - r_inner_m**2)
            unit_weight += vol * mat.density
            
            # Thermal resistance for a cylindrical layer per meter = ln(r_outer/r_inner) / (2 * pi * k)
            if mat.thermal_conductivity > 0:
                thermal_resistance += math.log(r_outer_m / r_inner_m) / (2 * math.pi * mat.thermal_conductivity)
                
            # Structural integrity proxy: max structural strength found in layers
            if mat.structural_strength > max_strength:
                max_strength = mat.structural_strength
                
            current_r_mm += layer.thickness

        # Thermal Rating proxy: high thermal resistance = high rating (e.g. 1 K/W -> 100 °C rating just as a UI placeholder proxy)
        thermal_rating = int(20 + thermal_resistance * 200) 
        
        # Structural Integrity %: compare max_strength to a "perfect" baseline (e.g. 450 MPa = 100%)
        structural_integrity = min(100.0, (max_strength / 450.0) * 100.0)
        if structural_integrity == 0:
            structural_integrity = 10.0 # base minimum if no metal
            
        return {
            "total_diameter": total_diameter_mm,
            "unit_weight": round(unit_weight, 1),
            "thermal_rating": thermal_rating,
            "structural_integrity": round(structural_integrity, 1)
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "total_thickness": self.get_total_thickness(),
            "svg_geometry": self.calculate_svg_geometry(),
            "layers": [dataclasses.asdict(l) for l in reversed(self.layers)],
            "metrics": self.get_metrics()
        }
