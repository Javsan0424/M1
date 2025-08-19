import agentpy as ap
import numpy as np
import random
import time

class Message:
    def __init__(self, key, content):
        self.key = key
        self.content = content

class CleaningAgent(ap.Agent):
    def setup(self):
        self.movements = 0
        self.position = (0, 0) 
        self.next_position = None
        self.direction = random.choice([(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)])
    
    def intent(self, room):
        if room.grid[self.position]:
            self.next_position = self.position  
        else:
            new_row = self.position[0] + self.direction[0]
            new_col = self.position[1] + self.direction[1]
            
            if 0 <= new_row < room.shape[0] and 0 <= new_col < room.shape[1]:
                self.next_position = (new_row, new_col)
            else:
                self.direction = random.choice([(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)])
                self.next_position = self.position
        
        others = []
        for ag in room.agents:
            if ag != self and ag.next_position == self.next_position:
                others.append(ag)

        if len(others) > 0:
            self.negotiate(others[0])

        if others:
            self.negotiate(others[0])
    
    def execute(self, room):
        if room.grid[self.position]:
            room.grid[self.position] = False
            room.dirty_cells -= 1
            room.cleaned_cells += 1
        else:
            self.position = self.next_position
            self.movements += 1
            room.total_movements += 1

    def act(self, room):
        self.intent(room)
        self.execute(room)
    
    def send_message(self, other_agent, message):
        return other_agent.receive_message(self, message)
    
    def receive_message(self, other_agent, message):
        if message.key == 0: 
            flip_result = np.random.rand() > 0.5
            if flip_result:
                pass
            else:
                self.next_position = self.position
                self.direction = random.choice([(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)])
            return Message(1, flip_result)
    
    def negotiate(self, other_agent):
        message = Message(0, "Negociando posición")
        response = self.send_message(other_agent, message)
        if response.content:  
            pass  
        else:  
            self.next_position = self.position
            self.direction = random.choice([(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)])

class CleaningRoom(ap.Model):
    def setup(self):
        self.shape = (self.p.rows, self.p.cols)
        self.grid = np.zeros(self.shape, dtype=bool)
        self.dirty_cells = 0
        self.cleaned_cells = 0
        self.total_movements = 0
        
        total_cells = self.p.rows * self.p.cols
        dirty_cells = int(total_cells * self.p.dirty_percent / 100)
        
        positions = [(i, j) for i in range(self.p.rows) for j in range(self.p.cols)]
        dirty_positions = random.sample(positions, dirty_cells)
        
        for pos in dirty_positions:
            self.grid[pos] = True
            self.dirty_cells += 1
        
        self.agents = ap.AgentList(self, self.p.num_agents, CleaningAgent)
    
    def step(self):
        for agent in self.agents:
            agent.intent(self)
        
        for agent in self.agents:
            agent.execute(self)
        
        if self.dirty_cells == 0:
            self.stop()
    
    def end(self):
        clean_percent = 100 - (self.dirty_cells / (self.p.rows * self.p.cols) * 100)
        
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

parameters = {'rows': 3, 'cols': 4, 'num_agents': 3,'dirty_percent': 30,'steps': 1000,'max_time': 1000,}
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

