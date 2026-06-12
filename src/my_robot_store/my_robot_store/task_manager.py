import rclpy 
import os
from pathlib import Path
from dotenv import load_dotenv
from rclpy.node import Node
from std_msgs.msg import String, Bool
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

        self.order_sub = self.create_subscription(String, 'customer_order', self.order_callback, 10)
        self.nav_status_sub = self.create_subscription(String, 'nav_status', self.nav_status_callback, 10)
        self.basket_sub = self.create_subscription(String, 'basket_status', self.basket_callback, 10)

        self.nav_goal_pub = self.create_publisher(String, 'nav_goal', 10)
        self.scan_trigger_pub = self.create_publisher(String, 'scan_trigger', 10)

        self.current_order_items = []
        self.active_item = None

        self.get_logger().info(f'Task Manager is online and waiting for orders...')

    def order_callback(self, msg):
        order_data = msg.data
        self.get_logger().info(f'Received Order: {order_data}')

        self.current_order_items = [item.strip() for item in order_data.split(',')]

        order_document = {
            # "items": [item.strip() for item in order_data.split(',')],
            "items": self.current_order_items,
            "status": "PENDING",
            "timestamp": self.get_clock().now().to_msg().sec
        }

        result = self.orders_collection.insert_one(order_document)
        self.get_logger().info(f'Order saved to DB with ID: {result.inserted_id}')

        # self.process_order(order_document['items'])
        self.process_next_item()

    # def process_order(self, items):
    #     for item in items:
    #         self.get_logger().info(f"Navigating to {item}")
    def process_next_item(self):
        if self.current_order_items:
            self.active_item = self.current_order_items.pop(0)
            self.get_logger().info(f"Targeting next item: {self.active_item}")

            nav_msg = String()
            nav_msg.data = self.active_item
            self.nav_goal_pub.publish(nav_msg)
        else:
            self.get_logger().info("All items collected! Routing back to Counter")

            self.active_item = None

            nav_msg = String()
            nav_msg.data = "Counter"
            self.nav_goal_pub.publish(nav_msg)

    def nav_status_callback(self, msg):
        if msg.data == "ARRIVED" and self.active_item:
            self.get_logger().info(f"Nev confirmed arrival. Triggering YOLO scan for: {self.active_item}")
            scan_msg = String()
            scan_msg.data = self.active_item
            self.scan_trigger_pub.publish(scan_msg)

    def basket_callback(self, msg):
        if msg.data == "ITEM_SECURED":
            self.get_logger().info(f"Successfully tracked and added {self.active_item} to basket")
            self.process_next_item()


def main():
    rclpy.init()
    node = TaskManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()