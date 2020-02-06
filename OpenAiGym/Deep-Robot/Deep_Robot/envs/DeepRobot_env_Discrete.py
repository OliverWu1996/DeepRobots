import gym
from gym import error, spaces, utils
from gym.utils import seeding

import math
from math import cos, sin, pi
import numpy as np
import random
from scipy.integrate import quad, odeint
# SET BACKEND
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

class DeepRobot(gym.Env):
    metadata = {'render.modes': ['human']}
    
    #required method for environment setup
    def __init__(self):
        self.x = 0 #robot's initial x- displacement
        self.y = 0 #robot's initial y- displacement
        self.theta = 0 #robot's initial angle
        self.theta_displacement = 0
        self.a1 = round((0.5*cos(1))-0.6,8) #-pi/4 #joint angle of proximal link
        self.a2 = round(1.1,8) #pi/4 #joint angle of distal link
        self.a1dot = 0
        self.a2dot = 0

        self.state = (self.theta, self.a1, self.a2)

        # constants
        self.t_interval = 0.001 #discretization of time
        self.timestep = 1
        self.R = 2 #length of every robot link
        
        #for visualization
        self.x_pos = [self.x]
        self.y_pos = [self.y]
        self.thetas = [self.theta]
        self.time = [0]
        self.a1 = [self.a1]
        self.a2 = [self.a2]
        
        #for env requirements
        self.action_space = spaces.Box(np.array([pi/8, pi/8]),np.array([-pi/8,-pi/8]))

        self.observation_space = spaces.Box(low=0, high=255, shape=
                    (HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8)


    # mutator methods
    def set_state(self, theta, a1, a2):
        self.state = (theta, a1, a2)

    # accessor methods
    def get_position(self):
        return self.x, self.y

    # helper methods
    @staticmethod
    def TeLg(theta):
        """
        :param theta: the inertial angle in radians
        :return: the lifted left action matrix given the angle
        """
        arr = np.array([[cos(theta), -sin(theta), 0],
                        [sin(theta), cos(theta), 0],
                        [0, 0, 1]])
        return arr

    @staticmethod
    def discretize(val, interval):
        '''
        :param val: input non-discretized value
        :param interval: interval for discretization
        :return: discretized value
        '''
        quotient = val / interval
        floor = math.floor(quotient)
        diff = quotient - floor
        if diff >= 0.5:
            discretized_val = (floor + 1) * interval
        else:
            discretized_val = floor * interval
        return discretized_val

    def D_inverse(self, a1, a2):
        """
        :return: the inverse of D function
        """
        R = self.R
        D = (2/R) * (-sin(a1) - sin(a1 - a2) + sin(a2))
        return 1/D

    def A(self, a1, a2):
        """
        :return: the Jacobian matrix
        """
        R = self.R
        A = np.array([[cos(a1) + cos(a1 - a2), 1 + cos(a1)],
                      [0, 0],
                      [(2/R) * (sin(a1) + sin(a1 - a2)), (2/R) * sin(a1)]])
        return A

    def M(self, theta, a1, a2, da1, da2):
        """
        :return: the 5 * 1 dv/dt matrix: xdot, ydot, thetadot, a1dot, a2dot
        """
        da = np.array([[da1],
                       [da2]])
        f = self.D_inverse(a1, a2) * (self.TeLg(theta) @ (self.A(a1, a2) @ da))
        xdot = f[0,0]
        ydot = f[1,0]
        thetadot = f[2,0]
        M = [xdot, ydot, thetadot, da1, da2]
        return M

    def robot(self, v, t, da1, da2):
        """
        :return: function used for odeint integration
        """
        _, _, theta, a1, a2 = v
        dvdt = self.M(theta, a1, a2, da1, da2)
        return dvdt

    def perform_integration(self, action, t_interval):
        """
        :return: perform integration of ode, return the final displacements and x-velocity
        """

        if t_interval == 0:
            return self.x, self.y, self.theta, self.a1, self.a2
        a1dot, a2dot = action
        v0 = [self.x, self.y, self.theta, self.a1, self.a2]
        t = np.linspace(0, t_interval, 11)
        sol = odeint(self.robot, v0, t, args=(a1dot, a2dot))
        x, y, theta, a1, a2 = sol[-1]
        return x, y, theta, a1, a2
    
    def move(self, a1dot, a2dot, timestep):
        """
        Implementation of Equation 9
        given the joint velocities of the 2 controlled joints
        and the number of discretized time intervals
        move the robot accordingly
        :param a1dot: joint velocity of the proximal joint
        :param a2dot: joint velocity of the distal joint
        :param timestep: number of time intevvals
        :return: new state of the robot
        """
        action = (a1dot, a2dot)
        t = timestep * self.t_interval
        x, y, theta, a1, a2 = self.perform_integration(action, t)

        # update robot variables
        self.x = x
        self.y = y
        self.time += t
        self.a1dot = a1dot
        self.a2dot = a2dot

        self.theta = self.rnd(self.discretize(theta, self.a_interval))

        self.enforce_theta_range()

        self.a1 = self.rnd(self.discretize(a1, self.a_interval))
        self.a2 = self.rnd(self.discretize(a2, self.a_interval))
        self.state = (self.theta, self.a1, self.a2)

        return self.state

    def enforce_theta_range(self):
        angle = self.theta
        if angle > pi:
            angle = angle % (2 * pi)
            if angle > pi:
                angle = angle - 2 * pi
        elif angle < -pi:
            angle = angle % (-2 * pi)
            if angle < -pi:
                angle = angle + 2 * pi
        self.theta = angle

    @staticmethod
    def rnd(number):
        return round(number, 8)

    def print_state(self):
        """
        print the current state
        :return: None
        """
        print('\nthe current state is: ' + str(self.state) + '\n')

    
    # required methods for environment setup
    def step(self, action):
        self.move(action)
        self.x_pos.append(self.x)
        self.y_pos.append(self.y)
        self.thetas.append(self.theta)
        self.time.append(self.time[-1]+1)
        self.a1.append(self.a1)
        self.a2.append(self.a2)
        
    def reset(self):
        self.__init__(self)
    
    def render(self, mode='human', close=False):
        # view results
        print('x positions are: ' + str(x_pos))
        print('y positions are: ' + str(y_pos))
        print('thetas are: ' + str(thetas))

        plt.plot(time, a1)
        plt.ylabel('a1 displacements')
        plt.show()

        plt.plot(time, a2)
        plt.ylabel('a2 displacements')
        plt.show()

        plt.plot(time, x_pos)
        plt.ylabel('x positions')
        plt.show()

        plt.plot(time, y_pos)
        plt.ylabel('y positions')
        plt.show()

        plt.plot(time, thetas)
        plt.ylabel('thetas')
        plt.show()
        plt.close()

