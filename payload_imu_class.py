import struct
from dataclasses import dataclass

STRUCT_FORMAT = "<fffIfffIfffI"
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

    xGyro: float        # Gyroscope measurement in X direction [mDeg/s]
    yGyro: float        # Gyroscope measurement in Y direction [mDeg/s]
    zGyro: float        # Gyroscope measurement in Z direction [mDeg/s]
    timestampGyro: int  # Timestamp of the gyroscope measurement

    xMag: float         # Magnetometer measurement in X direction [uT]
    yMag: float         # Magnetometer measurement in Y direction [uT]
    zMag: float         # Magnetometer measurement in Z direction [uT]
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
        unpacked_data = struct.unpack(STRUCT_FORMAT, data)
        return cls(*unpacked_data)
    
    def pack(self) -> bytes:
        """
        Convert the IMU object to a byte array.

        Returns:
            bytes: The byte array representation of the IMU data.
        """
        packed_data = struct.pack(STRUCT_FORMAT, *self.__dict__.values())
        return packed_data