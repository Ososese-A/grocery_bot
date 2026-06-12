import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from flask import Flask, render_template_string
import threading

class WebBridge (Node):
    def __init__(self):
        super().__init__('web_bridge_node')
        self.publisher_ = self.create_publisher(String, 'customer_order', 10)
    
    def send_order(self, items):
        msg = String()
        msg.data = items
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published Order to ROS2: {items}')


app = Flask(__name__)
ros_node = None

HTML_PAGE = """
<html>
    <body>
        <h1></h1>
        <form action="/order" method="post">
            <button name="items" value="Apple, Banana, Bottle, Cake" type="submit" style="padding:20px; font-size:20px">
                Order: Apple, Banana, Bottle, Cake
            </button>
        </form>
    </body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/order", methods=['POST'])
def order():
    ros_node.send_order("Apple, Banana, Bottle, Cake")
    return "<h1> Order Sent to Robot!<h1><a href='/'>Go Back</a>"

def main():
    global ros_node
    rclpy.init()
    ros_node = WebBridge()

    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)).start()

    rclpy.spin(ros_node)
    ros_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()