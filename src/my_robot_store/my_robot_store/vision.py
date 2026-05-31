import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import cv2
import os
from ultralytics import YOLO
from ament_index_python.packages import get_package_share_directory

class Vision(Node):
    def __init__(self):
        super().__init__('vision_node')

        self.trigger_sub = self.create_subscription(String, 'scan_trigger', self.scan_callback, 10)
        self.result_pub = self.create_publisher(Bool, 'item_found', 10)

        self.is_scanning = False
        self.target_item = ""

        self.model = YOLO('yolov8n.pt')
        self.yolo_names = self.model.names

        self.image_path = os.path.join(
            get_package_share_directory('my_robot_store'),
            'images',
            'shelf.jpeg'
        )

        self.timer = self.create_timer(0.1, self.vision_loop)
        self.get_logger().info(f"YOLO Simulation Node ready. Target image path: {self.image_path}")

    def scan_callback (self, msg):
        self.target_item = msg.data.lower().strip()
        self.is_scanning = True
        self.get_logger().info(f"Searching for target object: '{self.target_item}'")

    def vision_loop(self):
        if not self.is_scanning:
            return
        
        frame = cv2.imread(self.image_path)
        if frame is None:
            self.get_logger().error(f"CRITICAL: Could not find or load image at {self.image_path}")
            self.is_scanning = False

        results = self.model(frame, verbose=False)

        found_target = False

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                detected_name = self.yolo_names[class_id]

                if detected_name == self.target_item:
                    found_target = True
                    break

        if found_target:
            self.get_logger().info(f"Target '{self.target_item}' LOCKED via AI image detection!")

            msg = Bool()
            msg.data = True
            self.result_pub.publish(msg)

            self.is_scanning = False

        annotated_frame = results[0].plot()
        cv2.imshow("Robot Eyes (YOLO Simulation)", annotated_frame)
        cv2.waitKey(1)
        

def main():
    rclpy.init()
    node = Vision()
    rclpy.spin(node)
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
