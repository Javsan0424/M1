import agentpy as ap
import numpy as np
import random
import time

class CleaningAgent(ap.Agent):
    def setup(self):
        self.movements = 0
        self.position = (0, 0) 

    def act(self, room):
        if room.grid[self.position]:
            room.grid[self.position] = False
            room.dirty_cells -= 1
            room.cleaned_cells += 1
        else:
            self.move(room)
    
    def move(self, room):
        directions = [(-1, -1), (-1, 0), (-1, 1),(0, -1),(0, 1),(1, -1),(1, 0),(1, 1)]
        
        dr, dc = random.choice(directions)
        new_row = max(0, min(room.shape[0]-1, self.position[0] + dr))
        new_col = max(0, min(room.shape[1]-1, self.position[1] + dc))
        
        self.position = (new_row, new_col)
        self.movements += 1
        room.total_movements += 1

class CleaningRoom(ap.Model):
    def setup(self):
        # Configuración del espacio
        self.shape = (self.p.rows, self.p.cols)
        self.grid = np.zeros(self.shape, dtype=bool)
        self.dirty_cells = 0
        self.cleaned_cells = 0
        self.total_movements = 0
        
        # Inicializar celdas sucias
        total_cells = self.p.rows * self.p.cols
        dirty_cells = int(total_cells * self.p.dirty_percent / 100)
        
        positions = [(i, j) for i in range(self.p.rows) for j in range(self.p.cols)]
        dirty_positions = random.sample(positions, dirty_cells)
        
        for pos in dirty_positions:
            self.grid[pos] = True
            self.dirty_cells += 1
        
        # Crear agentes
        self.agents = ap.AgentList(self, self.p.num_agents, CleaningAgent)
    
    def step(self):
        for agent in self.agents:
            agent.act(self)
        
        if self.dirty_cells == 0:
            self.stop()
    
    def end(self):
        # Calcular métricas finales
        clean_percent = 100 - (self.dirty_cells / (self.p.rows * self.p.cols) * 100)
        
        # Resultados como diccionario
        self.reporters = {
            'final_clean_percent': float(clean_percent),
            'total_movements': int(self.total_movements),
            'time_to_clean': int(self.t if self.dirty_cells == 0 else self.p.max_time),
            'all_cleaned': bool(self.dirty_cells == 0),
            'initial_dirty': int(self.p.rows * self.p.cols * self.p.dirty_percent / 100),
            'remaining_dirty': int(self.dirty_cells),
            'cleaned_cells': int(self.cleaned_cells),
            'execution_time': None  
        }

parameters = {'rows': 3, 'cols': 4, 'num_agents': 4,'dirty_percent': 30,'steps': 1000,'max_time': 1000,}
start_time = time.time()
model = CleaningRoom(parameters)
model.run()
end_time = time.time()
model.reporters['execution_time'] = end_time - start_time

print("\nResultados de la simulación con AgentPy:")
print(f"Tamaño de la habitación: {parameters['rows']}x{parameters['cols']}")
print(f"Número de agentes: {parameters['num_agents']}")
print(f"Porcentaje inicial de celdas sucias: {parameters['dirty_percent']}%")
print(f"Tiempo máximo de ejecución: {parameters['max_time']} pasos")
print("\nEstadísticas:")
print(f"Tiempo hasta limpieza completa: {model.reporters['time_to_clean']} pasos")
print(f"Porcentaje final de celdas limpias: {model.reporters['final_clean_percent']:.2f}%")
print(f"Total de movimientos de todos los agentes: {model.reporters['total_movements']}")
print(f"Celdas sucias iniciales: {model.reporters['initial_dirty']}")
print(f"Celdas limpiadas durante simulación: {model.reporters['cleaned_cells']}")
print(f"Celdas sucias restantes: {model.reporters['remaining_dirty']}")
print(f"¿Se limpió completamente?: {'Sí' if model.reporters['all_cleaned'] else 'No'}")
print(f"\nTiempo de ejecución real: {model.reporters['execution_time']:.4f} segundos")