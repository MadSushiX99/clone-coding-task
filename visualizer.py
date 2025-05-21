from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import quaternion

class Visualizer:
    def __init__(self):
        # Set up figure and 3D axis
        self.fig = plt.figure()
        self.fig.legend("Gyro, Accel/Mag, Fused Result", loc="upper right")
        self.ax = self.fig.add_subplot(111, projection='3d')

    def update_plot(self, raw_gyro, raw_accel_mag, fused_result):
        """Update the plot with new data."""
        vec = np.array([1, 0, 0])
        raw_gyro = quaternion.rotate_vectors(quaternion.from_euler_angles(raw_gyro).normalized(), vec)
        raw_accel_mag = quaternion.rotate_vectors(quaternion.from_euler_angles(raw_accel_mag).normalized(), vec)
        fused_result = quaternion.rotate_vectors(fused_result.normalized(), vec)

        u_gyro, v_gyro, w_gyro = raw_gyro
        u_am, v_am, w_am = raw_accel_mag
        u_fused, v_fused, w_fused = fused_result
        
        # Clear the axes and re-draw the quivers with new data
        self.ax.cla()  # Clear the axes to remove the old quivers
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)
        
        # Create new quivers with updated data
        self.ax.quiver(0, 0, 0, u_gyro, v_gyro, w_gyro, color='r', label='Gyro')
        self.ax.quiver(0, 0, 0, u_am, v_am, w_am, color='g', label='Accel/Mag')
        self.ax.quiver(0, 0, 0, u_fused, v_fused, w_fused, color='b', label='Fused Result')
        
        plt.draw()  # Redraw the updated plot
        plt.pause(0.01)
