import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, TransformStamped
from std_msgs.msg import String
import tf2_ros

class Nav(Node):
    def __init__(self):
        super().__init__('navigation')

        self.goal_sub = self.create_subscription(String, 'nav_goal', self.set_goal, 10)

        self.pos_pub = self.create_publisher(Point, 'robot_position', 10)

        self.status_pub = self.create_publisher(String, 'nav_status', 10)

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

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
        for i in range(2):
            if self.is_moving:
                diff = self.target_pos[i] - self.current_pos[i]
                if abs(diff) > 0.05:
                    self.current_pos[i] += 0.1 if diff > 0 else -0.1

        p = Point()
        p.x, p.y, p.z = self.current_pos[0], self.current_pos[1], 0.0
        self.pos_pub.publish(p)

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'map'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = self.current_pos[0]
        t.transform.translation.y = self.current_pos[1]
        t.transform.translation.z = 0.0

        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)

        if self.is_moving:
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