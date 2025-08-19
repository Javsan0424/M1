import mesa
import numpy as np
import random
import time

class CleaningAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.movements = 0
        self.pos = (0, 0)  # Todos empiezan en (0,0) - equivalente a [1,1] en base 1

    def step(self):
        # Obtener el estado actual de la celda
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        dirty = any(isinstance(obj, DirtyCell) for obj in cell_contents)
        
        if dirty:
            # Limpiar la celda
            for obj in cell_contents:
                if isinstance(obj, DirtyCell):
                    self.model.grid.remove_agent(obj)
                    self.model.dirty_cells -= 1
                    self.model.cleaned_cells += 1
                    break
        else:
            # Mover a celda aleatoria
            self.move()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,  # Permite movimiento en 8 direcciones
            include_center=False
        )
        
        # Filtrar pasos válidos (dentro de los límites)
        valid_steps = [pos for pos in possible_steps 
                      if 0 <= pos[0] < self.model.grid.width 
                      and 0 <= pos[1] < self.model.grid.height]
        
        if valid_steps:
            new_position = random.choice(valid_steps)
            self.model.grid.move_agent(self, new_position)
            self.movements += 1
            self.model.total_movements += 1

class DirtyCell(mesa.Agent):
    """Agente que representa una celda sucia"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class CleaningModel(mesa.Model):
    def __init__(self, width, height, num_agents, dirty_percent):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.dirty_cells = 0
        self.cleaned_cells = 0
        self.total_movements = 0
        self.steps = 0
        self.max_steps = 1000
        
        # Crear celdas sucias
        total_cells = width * height
        num_dirty = int(total_cells * dirty_percent / 100)
        positions = [(x, y) for x in range(width) for y in range(height)]
        dirty_positions = random.sample(positions, num_dirty)
        
        for i, pos in enumerate(dirty_positions):
            dirty_cell = DirtyCell(i + num_agents, self)  # IDs únicos
            self.grid.place_agent(dirty_cell, pos)
            self.dirty_cells += 1
        
        # Crear agentes aspiradora
        for i in range(num_agents):
            agent = CleaningAgent(i, self)
            self.grid.place_agent(agent, (0, 0))
            self.schedule.add(agent)
    
    def step(self):
        self.steps += 1
        self.schedule.step()
        
        # Detener si todas las celdas están limpias o se alcanza el máximo de pasos
        if self.dirty_cells == 0 or self.steps >= self.max_steps:
            self.running = False
    
    def calculate_clean_percent(self):
        total_cells = self.grid.width * self.grid.height
        return 100 - (self.dirty_cells / total_cells * 100)

def run_simulation(width, height, num_agents, dirty_percent):
    start_time = time.time()
    
    model = CleaningModel(width, height, num_agents, dirty_percent)
    while model.running and model.steps < model.max_steps:
        model.step()
    
    end_time = time.time()
    
    # Recolectar resultados
    results = {
        'time_to_clean': model.steps if model.dirty_cells == 0 else model.max_steps,
        'final_clean_percent': model.calculate_clean_percent(),
        'total_movements': model.total_movements,
        'all_cleaned': model.dirty_cells == 0,
        'initial_dirty': int(width * height * dirty_percent / 100),
        'remaining_dirty': model.dirty_cells,
        'cleaned_cells': model.cleaned_cells,
        'execution_time': end_time - start_time
    }
    
    return results

# Parámetros de la simulación
params = {
    'width': 3,
    'height': 4,
    'num_agents': 4,
    'dirty_percent': 30
}

# Ejecutar simulación
results = run_simulation(**params)

# Mostrar resultados
print("\nResultados de la simulación con Mesa:")
print(f"Tamaño de la habitación: {params['width']}x{params['height']}")
print(f"Número de agentes: {params['num_agents']}")
print(f"Porcentaje inicial de celdas sucias: {params['dirty_percent']}%")
print("\nEstadísticas:")
print(f"Pasos hasta limpieza completa: {results['time_to_clean']}")
print(f"Porcentaje final de celdas limpias: {results['final_clean_percent']:.2f}%")
print(f"Total de movimientos: {results['total_movements']}")
print(f"Celdas sucias iniciales: {results['initial_dirty']}")
print(f"Celdas limpiadas: {results['cleaned_cells']}")
print(f"Celdas sucias restantes: {results['remaining_dirty']}")
print(f"¿Se limpió completamente?: {'Sí' if results['all_cleaned'] else 'No'}")
print(f"\nTiempo de ejecución real: {results['execution_time']:.4f} segundos")