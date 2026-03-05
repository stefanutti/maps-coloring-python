import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt1
import matplotlib.animation as animation
import time
#import tmp102

# Create figure for plotting
fig = plt.figure()
fig1 = plt1.figure()
ax = fig.add_subplot(1, 1, 1)
ax1 = fig1.add_subplot(1, 1, 1)
xs = []
ys = []
xs1 = []
ys1 = []

tmp102 = []
hum = []
# Initialize communication with TMP102
tmp102.append(np.random.randint(50))

# This function is called periodically from FuncAnimation
def animate(i, xs, ys, xs1, ys1):

    # Read temperature (Celsius) from TMP102
    tmp102.append(np.random.randint(50))
    hum.append(np.random.randint(50))
    temp_c = tmp102[i]
    hum1 = hum[i] 
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(temp_c)
    
    xs1.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys1.append(hum1)
    time.sleep(0.001)
    print(temp_c," ", hum1)
	# FILE HANDLING
    if(temp_c >= 40):
        with open('sensordata.txt','a+') as f:
            f.write(str(temp_c))
            f.write('\n')
            
    if(hum1 >= 40):
        with open('sensordata12.txt','a+') as f:
            f.write(str(hum1))
            f.write('\n')
	#FILE HANDLING
    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]

    xs1 = xs1[-20:]
    ys1 = ys1[-20:]

    # Draw x and y lists
    ax.clear()
    ax1.clear()
    ax.plot(xs, ys)
    ax1.plot(xs1, ys1)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('TMP102 Temperature over Time')
    plt.ylabel('Temperature (deg C)')
    
    plt1.xticks(rotation=45, ha='right')
    plt1.subplots_adjust(bottom=0.30)
    plt1.title('TMP102 Temperature over Time')
    plt1.ylabel('Temperature (deg C)')

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, xs1, ys1), interval=0.0001)
ani1 = animation.FuncAnimation(fig1, animate, fargs=(xs, ys, xs1, ys1), interval=0.0001)

plt.show()
plt1.show()
