import quaternion
import numpy as np

def gyro_to_delta_rot(newGyro, dt):
    """
    Convert gyroscope data to delta step rotation.
    """
    xGyro, yGyro, zGyro = newGyro

    # Apply step, convert mDeg to Deg and Deg to Rad
    delta_x = (xGyro/1000 * dt * np.pi / 180) 
    delta_y = (yGyro/1000 * dt * np.pi / 180)
    delta_z = (zGyro/1000 * dt * np.pi / 180)
    return [delta_x, delta_y, delta_z]

def acc_mag_to_euler(accel, mag):
    """
    Convert accelerometer and magnetometer data to rotation.
    - Accelerometer data is used to calculate roll and pitch
    - Magnetometer data is used to calculate yaw.
    """
    xAcc, yAcc, zAcc = accel
    xMag, yMag, zMag = mag

    roll = np.atan2(yAcc, zAcc)
    pitch = np.atan2(-xAcc, np.sqrt(yAcc**2 + zAcc**2))
    Hx = xMag*np.cos(pitch) + zMag*np.sin(pitch)
    Hy = xMag*np.sin(roll)*np.sin(pitch) + yMag*np.cos(roll) - zMag*np.sin(roll)*np.cos(pitch)
    yaw = np.atan2(-Hy, Hx)
    return [roll, pitch, yaw]

class Extended_Kalman_Filter:
    def __init__(self, q):
        
        self.q = q # Quaternion representing the state

        self.P = np.eye(4) * 0.1                # State Covariance Matrix
        self.Q = np.eye(4) * 0.01               # Process Noise Covariance Matrix
        self.R = np.eye(4) * 0.1                # Measurement Noise Covariance Matrix

    def predict(self, delta_gyro):
        # Convert delta gyro to quaternion
        delta_gyro = quaternion.from_float_array(np.concatenate([[0],np.array(delta_gyro)]))
        delta_q = 0.5 * (self.q * delta_gyro) 

        # Update the quaternion with the delta quaternion and renormalize
        self.q = self.q + delta_q
        self.q = self.q.normalized()

        # Compute the Jacobian of the state transition function
        F = 0.5 * np.array([delta_gyro.w, -delta_gyro.x, -delta_gyro.y, -delta_gyro.z,
                            delta_gyro.x, delta_gyro.w, delta_gyro.z, -delta_gyro.y,
                            delta_gyro.y, -delta_gyro.z, delta_gyro.w, delta_gyro.x,
                            delta_gyro.z, delta_gyro.y, -delta_gyro.x, delta_gyro.w]).reshape(4, 4)

        # Update the state covariance matrix
        self.P = (F @ self.P @ F.T) + self.Q

    def update(self, accel_mag_fusion):
        # Here , we assume the measuement Jacobian is identity, so it isn't included in the computation.

        # Convert the accelerometer and magnetometer data to a quaternion                                 
        q_meas = quaternion.from_euler_angles(accel_mag_fusion)
        q_meas = q_meas.normalized()

        # Compute the Kalman Gain
        K = self.P @ np.linalg.inv(self.P + self.R)

        # Update the state with the measurement and normalize
        # convert to normal array for computation, then convert back to quaternion
        q_meas = quaternion.as_float_array(q_meas)
        q = quaternion.as_float_array(self.q)
        self.q = quaternion.from_float_array(q + K @ (q_meas - q))
        self.q = self.q.normalized()

        # Update the state covariance matrix
        self.P = (np.eye(4) - K) @ self.P
