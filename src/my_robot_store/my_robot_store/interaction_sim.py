import rclpy 
from rclpy.node import Node
from std_msgs.msg import Bool, String

class InteractioSim (Node):
    def __init__(self):
        super().__init__('interaction_sim')

        self.found_sub = self.create_subscription(Bool, 'item_found', self.start_pickup, 10)
        self.update_pub = self.create_publisher(String, 'basket_status', 10)
        self.get_logger().info("Interaction (Arm Sim) is ready")

    def start_pickup(self, msg):
        if msg.data == True:
            self.get_logger().info("Vision confirmed item. Starting mechanical arm sequence...")
            self.get_logger().info("Status: Extending Arm...")
            self.get_logger().info("Status: Closing Gripper...")
            self.get_logger().info("Status: Placing in Basket")

            confirmation = String()
            confirmation.data = "ITEM_SECURED"
            self.update_pub.publish(confirmation)
            self.get_logger().info("Pick-and-place complete. Updating list...")


def main():
    rclpy.init()
    node = InteractioSim()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()