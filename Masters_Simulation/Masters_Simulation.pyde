# Import required Python libraries

import time
import random
from functools import reduce 
from operator import mul
import math
import atexit

# Define a linspace function, this function has the same behaviour as the numpy.linspace() function

def linspace(start, stop, num=50, endpoint=True):
    num = int(num)
    start = start * 1.
    stop = stop * 1.

    if num == 1:
        yield stop
        return
    if endpoint:
        step = (stop - start) / (num - 1)
    else:
        step = (stop - start) / num

    for i in range(num):
        yield start + step * i
        
# Define a meshgrid function, this function has the same behaviour as the numpy.meshgrid() function
        
def meshgrid(xdim, ydim):
    X = []
    Y = []
    for i in range(len(ydim)):
        X.append(xdim)
        
    for i in range(len(ydim)):
        temp_Y = []
        for j in range(len(xdim)):
            temp_Y.append(ydim[i])
        Y.append(temp_Y)
        
    return X, Y

# Define an exit handling function, saves all data to a text file when the program exits

def exit_handler():
    global string_list
    saveStrings("data/option{}_data_theo.txt".format(option), string_list)

atexit.register(exit_handler)

# This reshape function reshapes a Python list into a specified shape
    
def reshape(lst, shap):
    if len(shap) == 1:
        return lst
    n = reduce(mul, shap[1:])
    return [reshape(lst[i*n:(i+1)*n], shap[1:]) for i in range(len(lst)//n)]
        
# Width and Height of the environment in pixels        
        
w = 640
h = 480

# Discretization of the environment into 64 width sections and 48 height sections

width_sections = 64
height_sections = 48

# Creation of mesh grid to discretize environment

xdim = list(linspace(0, w, width_sections))
ydim = list(linspace(0, h, height_sections))
X, Y = meshgrid(xdim,ydim)

step_size = 50 # Step size taken by a point agent towards its desired position
agent = 0 # Variable holding agent ID
num_agents = 5 # Number of agents in the environment

# Variables for defining the risk distribution scenario

option = 3 # Variable for selecting between scenario 1, scenario 2 and scenario 3
a = 1
b = 0.0001

isSuccess = [False, False, False, False, False] # Array indicating which agents have arrived at desired position
reset = True # Variable indicating first run through of the loop
moving = False # Variable to indicate point agent motion for 2 seconds
abso_start = millis() # Recording start time of program
buffer = 0 # Time correction to offset time required for simulation setup

start = millis() # Initiating movement timer

# Variables used for changing position of point agents

changex = 0
changey = 0
temp_agent_x = 0
temp_agent_y = 0

# Variables used for storing data output information

iteration = 0
string_list = [] # Storing data to be written t otext

# Color of different Voronoi regions

trans = 150 
vor_colors = [[0, 255, 255, trans], [0, 255, 0, trans], [255, 255, 255, trans], [255, 255, 0, trans], [255, 0, 255, trans]] # Color palette for Voronoi regions

# Array for containing centroids of each Voronoi region

cent = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

# Defining initial agent positions and risk distribution based on selected option

risk = []        
    
if option == 1:
    agent_pos = [[245, 389], [145, 393], [159, 174], [114, 312], [195, 302]]

elif option == 2:
    target = [320, 240]
    agent_pos = [[409, 90], [99, 114], [109, 421], [308, 238], [466, 327]]

elif option == 3:
    target = [485, 320]
    agent_pos = [[168, 231], [248, 101], [335, 271], [138, 140], [372, 121]]

for i in range(len(ydim)):
    temp_risk = []
    for j in range(len(xdim)):
        if option == 1:
            temp_risk.extend([1])
            
        else:
            dis = dist(xdim[j], ydim[i], target[0], target[1])
            dis = dis**2
            temp_risk.append(a*(math.exp(-b*dis)))
    risk.append(temp_risk)
    
# Setup function to create environment with defined Width and Height in pixels
    
def setup():        
    size(w, h)
    noStroke()
    global max_distance
    max_distance = dist(0, 0, width, height)
    
# Loop function which runs continously until program is closed

def draw():

# Erasing background with each new loop    

    background(0)

# Bringing all global variables defined earlier into the "draw" function

    global agent_pos 
    global agent
    global reset
    global cent
    global start
    global step_size
    global option
    global moving
    global changex
    global changey
    global temp_agent_x
    global temp_agent_y
    global abso_start
    global buffer
    global iteration
    global string_list
    global xdim
    global ydim
                    
    # Voronoi diagram calculation            

    dis_array = []
    distance = []
    index = []
    vors = []

    for n in range(num_agents):
        
        dis_array.insert(n,[])
        index.insert(n,[])
        vors.insert(n,[])
        
        for i in range(len(ydim)):
            for j in range(len(xdim)):
                dis = dist(agent_pos[n][0], agent_pos[n][1], xdim[j], ydim[i]) # obtain distance between agent "n" and point [i, j]
                dis_array[n].append(dis)
        
        distance.insert(n, reshape(dis_array[n], [height_sections, width_sections]))
        
    for n in range(num_agents):
        for i in range(len(ydim)):
            for j in range(len(xdim)):
                
                if distance[n][i][j] \ # Ensure that distance between agent "n" and point [i, j] is less than distance between all other agents and point [i, j]
                <= min(distance[0][i][j], \
                       distance[1][i][j], \
                       distance[2][i][j], \
                       distance[3][i][j], \
                       distance[4][i][j]):
                    
                    vors[n].append([xdim[j],ydim[i]])
                    index[n].append([j,i])
    
    for i in range(num_agents): # Draw the Voronoi diagram
        fill(vor_colors[i][0], vor_colors[i][1], vor_colors[i][2], vor_colors[i][3])
        for j in range(len(vors[i])):
            ellipse(vors[i][j][0], vors[i][j][1], 15, 15)
            
    # Centroid calculation for Voronoi cells
    
    if sum(isSuccess) == 5 or reset: # If this is first loop of program, or all agents have arrived at desired location
        
        iteration = iteration + 1
        
        agent = 0        
    
        for i in range(num_agents): # Calculate the centroid of each Voronoi cell given the risk distribution
            isSuccess[i] = False
            risk_t = 0
            risk_x = 0
            risk_y = 0
            for j in range(len(vors[i])):
                risk_t += risk[index[i][j][1]][index[i][j][0]]
                risk_x += vors[i][j][0]*risk[index[i][j][1]][index[i][j][0]]
                risk_y += vors[i][j][1]*risk[index[i][j][1]][index[i][j][0]]
                    
            C_x = (risk_x/risk_t)
            C_y = (risk_y/risk_t)
            cent[i][0] = C_x
            cent[i][1] = C_y
    
    fill(255, 0, 0)
    if not option == 1:
        ellipse(target[0], target[1], 10, 10) # Draw the target (center of risk distribution)
    
    fill(0, 0, 255)
    for i in range(num_agents):
        ellipse(cent[i][0], cent[i][1], 10, 10) # Draw the centroid of each Voronoi region
    
    fill(0, 0, 0)
    for i in range(num_agents):
        ellipse(agent_pos[i][0], agent_pos[i][1], 10, 10) # Draw the position of all agents
        
        
    if moving == False: # If the agent is currently not moving then initiate movement
        
        angle = math.atan2(-(cent[agent][1] - agent_pos[agent][1]), cent[agent][0] - agent_pos[agent][0]) # Calculate angle of movement to get robot to its desired position
        temp_distance = dist(agent_pos[agent][0], agent_pos[agent][1], cent[agent][0], cent[agent][1]) # Calculate distance between agent and its desired position
                
        # Calculate the required movement of agent in the X direction        
                
        if (cent[agent][0] - agent_pos[agent][0]) < 0:
            changex = max(-math.cos(angle)*(-temp_distance), -math.cos(angle)*(-step_size))
        elif (cent[agent][0] - agent_pos[agent][0]) > 0:
            changex = min(math.cos(angle)*(temp_distance), math.cos(angle)*step_size)
        else:
            changex = 0
            
        # Calculate the required movement of agent in the Y direction  
            
        if (cent[agent][1] - agent_pos[agent][1]) < 0:
            changey = max(math.sin(angle)*(-temp_distance), math.sin(angle)*(-step_size))
        elif (cent[agent][1] - agent_pos[agent][1]) > 0:
            changey = min(-math.sin(angle)*(temp_distance), -math.sin(angle)*step_size)
        else:
            changey = 0
        
        temp_agent_x = agent_pos[agent][0]
        temp_agent_y = agent_pos[agent][1]
        moving = True # Record that the robot is now moving, and will move for 2 seconds
        start = millis() # Start 2 second timer for robot movement

    # Coverage metric calculation
    
    global_coverage = 0
    
    for i in range(num_agents): # Calculate coverage metric of the environment in this particular frame of the simulation
        coverage = 0
        for j in range(len(vors[i])):
            dis = dist(agent_pos[i][0], agent_pos[i][1], vors[i][j][0], vors[i][j][1])
            sense = math.exp(-(dis**2)/(30**2))
            coverage += risk[index[i][j][1]][index[i][j][0]]*sense
            
        global_coverage += coverage   
            
    fill(255, 255, 255)
    
    saveFrame("data/Option {}/frame-######.png".format(option)) # Store current frame of simulation for data collection
    
    # Record data metrics of the simulation
    
    if reset:
        reset = False
        buffer = millis() - abso_start 
        string_list.append("Time: {}, Coverage Metric: {}, Iteration: {}, Agent Positions: {}, Desired Positions: {}".format(0, global_coverage, iteration, agent_pos, cent))
    else:
        string_list.append("Time: {}, Coverage Metric: {}, Iteration: {}, Agent Positions: {}, Desired Positions: {}".format((millis() - abso_start - buffer)/1000.0, global_coverage, iteration, agent_pos, cent))
    
    # Record the amount of time an agent has been moving
    
    diff = millis() - start
    
    # If point agent has been moving for less than 2 seconds then continue moving agent to desired position
        
    if (diff <= 2000):
        
        agent_pos[agent][0] = temp_agent_x + changex*((diff)/2000.0)
        agent_pos[agent][1] = temp_agent_y + changey*((diff)/2000.0)
        
    # If point agent has been moving for more than 2 seconds then stop moving agent
                 
    else:
        
        agent_pos[agent][0] = temp_agent_x + changex
        agent_pos[agent][1] = temp_agent_y + changey
                
        moving = False
             
        if int(cent[agent][0] - agent_pos[agent][0]) == 0 and int(cent[agent][1] - agent_pos[agent][1]) == 0: # If distance between agent and its desired position is zero, then agent has arrived at desired position
            isSuccess[agent] = True
            agent = agent + 1
                

    
    

        

    
