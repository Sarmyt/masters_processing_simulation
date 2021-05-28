import time
import random
from functools import reduce 
from operator import mul
import math
import atexit

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
        
w = 640
h = 480
width_sections = 64
height_sections = 48

xdim = list(linspace(0, w, width_sections))
ydim = list(linspace(0, h, height_sections))
X, Y = meshgrid(xdim,ydim)

step_size = 50
option = 3

agent = 0
num_agents = 5
a = 1
b = 0.0001

isSuccess = [False, False, False, False, False]
reset = True
moving = False
abso_start = millis()
buffer = 0

start = millis()  
changex = 0
changey = 0
temp_agent_x = 0
temp_agent_y = 0
iteration = 0
string_list = []

trans = 150
vor_colors = [[0, 255, 255, trans], [0, 255, 0, trans], [255, 255, 255, trans], [255, 255, 0, trans], [255, 0, 255, trans]]

cent = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

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
    
def exit_handler():
    global string_list
    saveStrings("data/option{}_data_theo.txt".format(option), string_list)

atexit.register(exit_handler)
    
def reshape(lst, shap):
    if len(shap) == 1:
        return lst
    n = reduce(mul, shap[1:])
    return [reshape(lst[i*n:(i+1)*n], shap[1:]) for i in range(len(lst)//n)]
    
def setup():        
    size(w, h)
    noStroke()
    global max_distance
    max_distance = dist(0, 0, width, height)

def draw():
    background(0)
    
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
    
    fill(255, 0, 0)
            
    # Voronoi calculation            

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
                dis = dist(agent_pos[n][0], agent_pos[n][1], xdim[j], ydim[i])
                dis_array[n].append(dis)
        
        distance.insert(n, reshape(dis_array[n], [height_sections, width_sections]))
        
    for n in range(num_agents):
        for i in range(len(ydim)):
            for j in range(len(xdim)):
                
                if distance[n][i][j] \
                <= min(distance[0][i][j], \
                       distance[1][i][j], \
                       distance[2][i][j], \
                       distance[3][i][j], \
                       distance[4][i][j]):
                    
                    vors[n].append([xdim[j],ydim[i]])
                    index[n].append([j,i])
    
    for i in range(num_agents):
        fill(vor_colors[i][0], vor_colors[i][1], vor_colors[i][2], vor_colors[i][3])
        for j in range(len(vors[i])):
            ellipse(vors[i][j][0], vors[i][j][1], 15, 15)
            
    # Centroid calculation
    
    if sum(isSuccess) == 5 or reset:
        
        iteration = iteration + 1
        
        agent = 0        
    
        for i in range(num_agents):
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
        ellipse(target[0], target[1], 10, 10)
    
    fill(0, 0, 255)
    for i in range(num_agents):
        ellipse(cent[i][0], cent[i][1], 10, 10)
    
    fill(0, 0, 0)
    for i in range(num_agents):
        ellipse(agent_pos[i][0], agent_pos[i][1], 10, 10)
        
        
    if moving == False:
        
        angle = math.atan2(-(cent[agent][1] - agent_pos[agent][1]), cent[agent][0] - agent_pos[agent][0])
        temp_distance = dist(agent_pos[agent][0], agent_pos[agent][1], cent[agent][0], cent[agent][1])
                
        if (cent[agent][0] - agent_pos[agent][0]) < 0:
            changex = max(-math.cos(angle)*(-temp_distance), -math.cos(angle)*(-step_size))
        elif (cent[agent][0] - agent_pos[agent][0]) > 0:
            changex = min(math.cos(angle)*(temp_distance), math.cos(angle)*step_size)
        else:
            changex = 0
            
        if (cent[agent][1] - agent_pos[agent][1]) < 0:
            changey = max(math.sin(angle)*(-temp_distance), math.sin(angle)*(-step_size))
        elif (cent[agent][1] - agent_pos[agent][1]) > 0:
            changey = min(-math.sin(angle)*(temp_distance), -math.sin(angle)*step_size)
        else:
            changey = 0
        
        temp_agent_x = agent_pos[agent][0]
        temp_agent_y = agent_pos[agent][1]
        moving = True
        start = millis()    

    # Coverage metric calculation
    
    global_coverage = 0
    
    for i in range(num_agents):
        coverage = 0
        for j in range(len(vors[i])):
            dis = dist(agent_pos[i][0], agent_pos[i][1], vors[i][j][0], vors[i][j][1])
            sense = math.exp(-(dis**2)/(30**2))
            coverage += risk[index[i][j][1]][index[i][j][0]]*sense
            
        global_coverage += coverage   
            
    fill(255, 255, 255)
    
    saveFrame("data/Option {}/frame-######.png".format(option))
    
    if reset:
        reset = False
        buffer = millis() - abso_start 
        string_list.append("Time: {}, Coverage Metric: {}, Iteration: {}, Agent Positions: {}, Desired Positions: {}".format(0, global_coverage, iteration, agent_pos, cent))
    else:
        string_list.append("Time: {}, Coverage Metric: {}, Iteration: {}, Agent Positions: {}, Desired Positions: {}".format((millis() - abso_start - buffer)/1000.0, global_coverage, iteration, agent_pos, cent))
    
    diff = millis() - start
        
    if (diff <= 2000):
        
        agent_pos[agent][0] = temp_agent_x + changex*((diff)/2000.0)
        agent_pos[agent][1] = temp_agent_y + changey*((diff)/2000.0)
                 
    else:
        
        agent_pos[agent][0] = temp_agent_x + changex
        agent_pos[agent][1] = temp_agent_y + changey
                
        moving = False
             
        if int(cent[agent][0] - agent_pos[agent][0]) == 0 and int(cent[agent][1] - agent_pos[agent][1]) == 0:
            isSuccess[agent] = True
            agent = agent + 1
                

    
    

        

    
