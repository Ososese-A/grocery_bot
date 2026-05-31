import rclpy 
import os
from pathlib import Path
from dotenv import load_dotenv
from rclpy.node import Node
from std_msgs.msg import String
from pymongo import MongoClient

home_dir = Path.home()
env_path = home_dir / 'bot_ws' / '.env'
load_dotenv(dotenv_path=env_path)

class TaskManager(Node):
    def __init__(self):
        super().__init__('task_manager_node')

        self.uri = os.getenv("MONGO_URI")
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
        self.db = self.client['robot_store_db']
        self.orders_collection = self.db["orders"]

        self.subscription = self.create_subscription(
            String,
            'customer_order',
            self.order_callback,
            10
        )

        self.get_logger().info(f'Task Manager is online and waiting for orders...')

    def order_callback(self, msg):
        order_data = msg.data
        self.get_logger().info(f'Received Order: {order_data}')

        order_document = {
            "items": [item.strip() for item in order_data.split(',')],
            "status": "PENDING",
            "timestamp": self.get_clock().now().to_msg().sec
        }

        result = self.orders_collection.insert_one(order_document)
        self.get_logger().info(f'Order saved to DB with ID: {result.inserted_id}')

        self.process_order(order_document['items'])

    def process_order(self, items):
        for item in items:
            self.get_logger().info(f"Navigating to {item}")

def main():
    rclpy.init()
    node = TaskManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()