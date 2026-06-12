import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import String

class Nav(Node):
    def __init__(self):
        super().__init__('navigation')

        self.goal_sub = self.create_subscription(String, 'nav_goal', self.set_goal, 10)

        self.pos_pub = self.create_publisher(Point, 'robot_position', 10)

        self.status_pub = self.create_publisher(String, 'nav_status', 10)

        self.current_pos = [0.0, 0.0]
        self.target_pos = [0.0, 0.0]
        self.is_moving = False

        self.timer = self.create_timer(0.1, self.move_bot)

        self.locations = {
            "Apple": [2.0, 3.0],
            "Banana": [-1.0, 4.0],
            "Bottle": [1.0, 2.0],
            "Cake": [3.0, 4.0],
            "Counter": [0.0, 0.0]
        }

        self.get_logger().info(f"Navigate node active and idle...")

    def set_goal(self, msg):
        item = msg.data
        if item in self.locations:
            self.target_pos = self.locations[item]
            self.is_moving = True
            self.get_logger().info(f"Navigating to {item} at {self.target_pos}...")
        else:
            self.get_logger().warn(f"Location coordinates unknown for item: {item}")

    def move_bot(self):
        if not self.is_moving:
            return
        
        for i in range(2):
            diff = self.target_pos[i] - self.current_pos[i]
            if abs(diff) > 0.05:
                self.current_pos[i] += 0.1 if diff > 0 else -0.1

        p = Point()
        p.x, p.y, p.z = self.current_pos[0], self.current_pos[1], 0.0
        self.pos_pub.publish(p)

        dist = abs(self.current_pos[0] - self.target_pos[0]) + abs(self.current_pos[1] - self.target_pos[1])
        if dist < 0.15:
            self.is_moving = False
            self.get_logger().info("Arrived at destination!")

            status_msg = String()
            status_msg.data = "ARRIVED"
            self.status_pub.publish(status_msg)

def main():
    rclpy.init()
    node = Nav()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()