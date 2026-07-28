#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

class ScanFrameCorrector : public rclcpp::Node
{
public:
    ScanFrameCorrector()
    : Node("scan_frame_corrector")
    {
        sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/scan",
            rclcpp::SensorDataQoS(),
            std::bind(&ScanFrameCorrector::scanCallback, this, std::placeholders::_1));

        pub_ = this->create_publisher<sensor_msgs::msg::LaserScan>(
            "/scan_fixed",
            rclcpp::SensorDataQoS());

        RCLCPP_INFO(this->get_logger(), "Scan Frame Corrector Started");
    }

private:
    void scanCallback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
    {
        auto out = *msg;

        // Change only the frame
        out.header.frame_id = "lidar_link";

        pub_->publish(out);
    }

    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr sub_;
    rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr pub_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ScanFrameCorrector>());
    rclcpp::shutdown();
    return 0;
}