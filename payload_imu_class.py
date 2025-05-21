import struct
from dataclasses import dataclass

STRUCT_FORMAT = "<fffQiiiQfffQ"
STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)

# Define the IMU class
@dataclass
class Payload_IMU:
    """
    A class to represent an Inertial Measurement Unit (IMU) data packet.
    """

    xAcc: float         # Acceleration in X direction [mg, g=9.81]
    yAcc: float         # Acceleration in Y direction [mg, g=9.81]
    zAcc: float         # Acceleration in Z direction [mg, g=9.81]
    timestampAcc: int   # Timestamp of the accelerometer measurement

    xGyro: int        # Gyroscope measurement in X direction [mDeg/s]
    yGyro: int        # Gyroscope measurement in Y direction [mDeg/s]
    zGyro: int        # Gyroscope measurement in Z direction [mDeg/s]
    timestampGyro: int  # Timestamp of the gyroscope measurement

    xMag: float         # Magnetometer measurement in X direction [mGauss]
    yMag: float         # Magnetometer measurement in Y direction [mGauss]
    zMag: float         # Magnetometer measurement in Z direction [mGauss]
    timestampMag: int   # Timestamp of the magnetometer measurement

    @classmethod
    def unpack(cls, data: bytes):
        """
        Create an IMU object from a byte array.

        Args:
            data (bytes): The byte array containing IMU data.

        Returns:
            IMU: An instance of the IMU class with populated attributes.
        """
        if len(data) != STRUCT_SIZE:
            raise ValueError(f"Data size mismatch: expected {STRUCT_SIZE}, got {len(data)}")
        unpacked_data = struct.unpack(STRUCT_FORMAT, data)
        return cls(*unpacked_data)
    
    def pack(self) -> bytes:
        """
        Convert the IMU object to a byte array.

        Returns:
            bytes: The byte array representation of the IMU data.
        """
        try:
            packed_data = struct.pack(STRUCT_FORMAT, *self.__dict__.values())
        except struct.error as e:
            raise ValueError(f"Packing error: {e}")
        return packed_data