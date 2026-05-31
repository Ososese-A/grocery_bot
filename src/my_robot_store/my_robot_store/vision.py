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

        self.model = YOLO('yolov8n.pt')
        self.yolo_names = self.model.names

        self.package_share = get_package_share_directory('my_robot_store')
        self.image_path = os.path.join(self.package_share, 'images', 'shelf.jpeg')
        self.output_path = os.path.join(self.package_share, 'images', 'output.jpeg')

        self.get_logger().info(f"YOLO Vision Node is online and idling...")

    def scan_callback (self, msg):
        target_item = msg.data.lower().strip()
        self.get_logger().info(f"Scanning shelf for: '{target_item}")

        frame = cv2.imread(self.image_path)
        if frame is None:
            self.get_logger().error(f"Could not load image at {self.image_path}")
            return
        
        results = self.model(frame, verbose=False)
        found_target = False

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                detected_name = self.yolo_names[class_id]

                if detected_name == target_item:
                    found_target = True
                    break

        result_msg = Bool()
        result_msg.data = found_target
        self.result_pub.publish(result_msg)

        if found_target:
            self.get_logger().info(f"Target '{target_item}' LOCKED and verified")
        else:
            self.get_logger().warn(f"Target '{target_item}' not found on the shelf")
        
        annotated_frame = results[0].plot()
        cv2.imwrite(self.output_path, annotated_frame)
        self.get_logger().info(f"Results saved visually to: {self.output_path}")
        

def main():
    rclpy.init()
    node = Vision()
    rclpy.spin(node)
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
