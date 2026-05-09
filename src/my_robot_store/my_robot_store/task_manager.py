import rclpy 
from rclpy.node import Node
from std_msgs.msg import String

class TaskManager(Node):
    def __init__(self):
        super().__init__('task_manager_node')

        self.subscription = self.create_subscription(
            String,
            'customer_order',
            self.order_callback,
            10
        )

        self.get_logger().info(f'Task Manager is online and waiting for orders...')

    def order_callback(self, msg):
        order_items = msg.data.split(',')
        self.get_logger().info(f'Received Order: {order_items}')

        for item in order_items:
            self.get_logger().info(f'Processing: {item}...')
            self.get_logger().info(f'Robot is now moving to the location for {item}')

def main():
    rclpy.init()
    node = TaskManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()