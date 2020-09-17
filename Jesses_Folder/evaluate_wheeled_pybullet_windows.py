import os

from envs.WheeledRobotPybulletEnv import WheeledRobotPybulletEnv
from stable_baselines.ppo2.ppo2 import PPO2
from stable_baselines.common.vec_env import DummyVecEnv
import matplotlib.pyplot as plt

raw_env = WheeledRobotPybulletEnv(decision_interval=1, use_GUI=True,num_episode_steps=5)
# Optional: PPO2 requires a vectorized environment to run
# the env is now wrapped automatically when passing it to the constructor
vec_env = DummyVecEnv([lambda: raw_env])

dir_name = "results\LearningResults\PPO_WheeledRobotPybullet"
tensorboard_dir = dir_name + "\\tensorboard"
model_dir = dir_name + "\\model"
model = PPO2.load(model_dir, vec_env)
# model.learn(total_timesteps=100, tb_log_name="test")
# model.save(model_dir)

env = vec_env.envs[0]
obs_prev = env.reset()

x_poss = [env.snake_robot.x]
y_poss = [env.snake_robot.y]
thetas = [env.snake_robot.theta]
times = [0]
a1s = [env.snake_robot.a1]
a2s = [env.snake_robot.a2]
a1dots = [env.snake_robot.a1dot]
a2dots = [env.snake_robot.a2dot]
# robot_params = []

# Calculate number of time steps based on decsion interval to have 30sec rollout
# decision interval = dt , num_steps = n, rollout_time = t = 30sec,  dt*n = t --> n = t/dt
t = 100 #sec
n = int(t/env.snake_robot.decision_interval)
n = (env.num_episode_steps)*3
for i in range(n):
    x_prev = env.snake_robot.x
    action, _states = model.predict(obs_prev)
    obs, rewards, dones, info = env.step(action)
    x = env.snake_robot.x
    print(
        "Timestep: {} | State: {} | Action: {} | Reward: {} | dX: {}".format(i, obs_prev, action, rewards, x - x_prev))
    obs_prev = obs
    x_poss.append(env.snake_robot.x)
    y_poss.append(env.snake_robot.y)
    thetas.append(env.snake_robot.theta)
    times.append(i)
    a1s.append(env.snake_robot.a1)
    a2s.append(env.snake_robot.a2)
    a1dots.append(env.snake_robot.a1dot)
    a2dots.append(env.snake_robot.a2dot)

plots_dir = dir_name + "\\PolicyRolloutPlotsFromLoading\\"
if not os.path.isdir(plots_dir):
    os.mkdir(plots_dir)


#----- Seperate data into 3 trials and plot results "double check reset theta and indecies used for plot" -------------#

import matplotlib
import numpy as np
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.size'] = 12
policy_fig = plt.figure(figsize=(10, 10))
plt.subplot(1, 2, 1)
plt.title('Position-Orientation vs Time')
colors = ['red','green','blue']; maps = ['Reds','Greens','Blues']

reset_steps = env.num_episode_steps
for i in range(3):
    index = reset_steps*i
    Time = np.arange(0,len(x_poss[reset_steps*i+1:reset_steps*(i+1)]),1) * env.snake_robot.decision_interval
    plt.plot(x_poss[reset_steps*i+1:reset_steps*(i+1)], y_poss[reset_steps*i+1:reset_steps*(i+1)], color=colors[i], linestyle='dashed', marker="o", alpha=0.2, label='trial'+str(i)) #+'theta ='+str(thetas[index]) )
    plt.quiver(x_poss[reset_steps*i+1:reset_steps*(i+1)], y_poss[reset_steps*i+1:reset_steps*(i+1)], np.cos( thetas[reset_steps*i+1:reset_steps*(i+1)] ), np.sin( thetas[reset_steps*i+1:reset_steps*(i+1)] ), Time, edgecolors='k', units='xy', cmap=maps[i])

plt.legend() #[r'$ \hat P_{(x_i,y_i,\theta_i)} $'])
plt.xlabel('X position (meters)'); plt.ylabel('Y position (meters)')

plt.subplot(1, 2, 2)
plt.title('Joint Angle Space vs Time')
for i in range(3):
    A1s = a1s[reset_steps*i+1:reset_steps*(i+1)]
    A2s =  a2s[reset_steps*i+1:reset_steps*(i+1)]
    T = np.arange(0,len(a1s[reset_steps*i+1:reset_steps*(i+1)]),1) * env.snake_robot.decision_interval
    plt.plot(A1s, A2s, alpha=(i+1)/3,color= colors[i],label='trial'+str(i))
    plt.scatter(A1s, A2s, c=T, marker='d',cmap = maps[i])
plt.legend()
plt.xlabel(r'$\alpha_1$')
plt.ylabel(r'$\alpha_2$')

plt.tight_layout()
plt.savefig(plots_dir + 'PolicyRolloutPlot' + '.png')
plt.close()

#-------------------------------- End of Policy Rollout Plot ---------------------------------#



# view results
# print('x positions are: ' + str(x_pos))
# print('y positions are: ' + str(y_pos))
# print('thetas are: ' + str(thetas))

plot_style = "--bo"
marker_size = 3

plt.plot(x_poss, y_poss, plot_style, markersize=marker_size)
plt.xlabel('x')
plt.ylabel('y')
plt.savefig(plots_dir + 'y vs x' + '.png')
plt.close()

plt.plot(times, a1s, plot_style, markersize=marker_size)
plt.ylabel('a1 displacements')
plt.xlabel('time')
plt.savefig(plots_dir + 'a1 displacements' + '.png')
plt.close()

plt.plot(times, a2s, plot_style, markersize=marker_size)
plt.ylabel('a2 displacements')
plt.xlabel('time')
plt.savefig(plots_dir + 'a2 displacements' + '.png')
plt.close()

plt.plot(times, x_poss, plot_style, markersize=marker_size)
plt.ylabel('x positions')
plt.xlabel('time')
plt.savefig(plots_dir + 'x positions' + '.png')
plt.close()

plt.plot(times, y_poss, plot_style, markersize=marker_size)
plt.ylabel('y positions')
plt.xlabel('time')
plt.savefig(plots_dir + 'y positions' + '.png')
plt.close()

plt.plot(times, thetas, plot_style, markersize=marker_size)
plt.ylabel('thetas')
plt.xlabel('time')
plt.savefig(plots_dir + 'thetas' + '.png')
plt.close()

plt.plot(times, a1dots, plot_style, markersize=marker_size)
plt.ylabel('a1dot')
plt.xlabel('time')
plt.savefig(plots_dir + 'a1dot' + '.png')
plt.close()

plt.plot(times, a2dots, plot_style, markersize=marker_size)
plt.ylabel('a2dot')
plt.xlabel('time')
plt.savefig(plots_dir + 'a2dot' + '.png')
plt.close()

""""""
# Comprehensive Plot of Policy Rollout Data
# - Joint angles vs Time
# - Joint States vs Time
# - Actions vs Time
# - Position/Orientation vs Time

# convert time scale based on decsion interval
TIME = []
for t_steps in times:
    TIME.append(env.snake_robot.decision_interval*t_steps)
times = TIME

import matplotlib
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['image.cmap'] = 'gray'

import math
policy_fig = plt.figure(figsize=(10, 10))

plt.subplot(2, 2, 1)
plt.title('Joint Angles vs Time')
plt.plot(times,a1s,marker='d',alpha = 0.5,color='red')
plt.plot(times,a2s,marker='p',alpha = 0.5,color='blue')
plt.xlabel('time (sec)')
plt.ylabel(r'$\alpha $'+ '  ' + '(radians)')
plt.legend([r'$\alpha_1$',r'$\alpha_2$'])

plt.subplot(2, 2, 2)
plt.title('Joint States vs Time')
plt.plot(a1s,a2s, 'k--', alpha = 0.1)
plt.scatter(a1s,a2s, c=times, marker='d')
cbar = plt.colorbar();  cbar.set_label('time (sec)')
plt.xlabel(r'$\alpha_1$')
plt.ylabel(r'$\alpha_2$')

plt.subplot(2, 2, 3)
plt.title('Actions vs Time')
plt.plot(times,a1dots,marker='d',alpha = 0.5,color='red')
plt.plot(times,a2dots,marker='p',alpha = 0.5,color='blue')
plt.xlabel('time (sec)')
plt.ylabel(r'$\.\alpha $'+ '  ' + '(radians/sec)')
plt.legend([r'$\.\alpha_1$',r'$\.\alpha_2$'])


plt.subplot(2, 2, 4)
plt.title('Position-Orientation vs Time')
sys_info = ("Evaluation Time: {} | Decision Interval: {} | X Displacment: {} | Gait Speed: {} |".format(t, env.snake_robot.decision_interval, round(x_poss[-1]-x_poss[0],2), round( ((x_poss[-1]-x_poss[0])/t),2) ))
plt.suptitle(sys_info)
xv,yv,Lx,Ly = [],[],[],[]
for i in range(len(thetas)):
    xv.append(math.cos(thetas[i])); yv.append(math.sin(thetas[i]))
    Lx.append(0); Ly.append(1)
plt.scatter(x_poss, y_poss, c=times)
B = plt.quiver(x_poss,y_poss,xv,yv,times,edgecolors='k',units='xy')
cbar = plt.colorbar(); cbar.set_label('time (sec)')
plt.plot(x_poss, y_poss, color='black', linestyle='dashed', marker="o", alpha=0.2)
plt.xlabel('X position (meters)'); plt.ylabel('Y position (meters)')
plt.legend([r'$ \hat P_{(x_i,y_i,\theta_i)} $'])

# heading "phi" arrow with colormap
# body frame arrows --> plt.quiver(x_poss, y_poss, Lx, Ly, angles='xy') & plt.quiver(x_poss, y_poss, xv, yv, times, edgecolors='k', units='xy')

# legend compass, indicates heading direction
X_key = -0.125
Y_key = -0.075
Arrow_length = 1.15
#B = plt.quiver(x_poss, y_poss, Ly, Lx, angles='xy')
plt.quiverkey(B, X_key, Y_key, Arrow_length, r'$\theta= \pi/2$', angle=90, labelpos='N') #,coordinates='figure')
plt.quiverkey(B, X_key+.0675, Y_key-0.025, Arrow_length, r'$\theta=0$', angle=0,labelpos='E') #,coordinates='figure')

plt.tight_layout()
#plt.savefig(plots_dir + 'PolicyRolloutPlot' + '.png')
plt.close()

