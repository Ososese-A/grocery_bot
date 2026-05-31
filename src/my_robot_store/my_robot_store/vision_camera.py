import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import cv2
import numpy as np

class VisionCamera(Node):
    def __init__(self):
        super().__init__('vision_node')

        self.trigger_sub = self.create_subscription(String, 'scan_trigger', self.scan_callback, 10)
        self.result_pub = self.create_publisher(Bool, 'item_found', 10)

        self.is_scanning = False
        self.target_item = ""

        self.cap = cv2.VideoCapture(0)

        self.timer = self.create_timer(0.1, self.vision_loop)

    def scan_callback (self, msg):
        self.target_item = msg.data
        self.is_scanning = True
        self.get_logger().info(f"Searching for {self.target_item}")

    def vision_loop(self):
        if not self.is_scanning:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        low_red = np.array([0, 120, 70])
        high_red = np.array([10, 255, 255])

        mask = cv2.inRange(hsv_frame, low_red, high_red)

        red_pixels = cv2.countNonZero(mask)

        if red_pixels > 5000:
            self.get_logger().info(f"Target {self.target_item} LOCKED")

            msg = Bool()
            msg.data = True
            self.result_pub.publish(msg)

            self.is_scanning = False

        cv2.imshow("Robot Eyes", mask)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = VisionCamera()
    rclpy.spin(node)
    node.cap.release()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == "__main__":
    main()