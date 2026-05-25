#include <QApplication>
#include <rclcpp/rclcpp.hpp>
#include <thread>
#include <memory>

#include "generation_gui/main_window.hpp"

/// Entry point. Spin a ROS node on a background thread while Qt
/// owns the main thread for the event loop. ROS shuts down only
/// after the Qt window closes. 
int main(int argc, char *argv[]){
    rclcpp::init(argc, argv);
    // one shared node, every panel reuses it for its clients/subs/pubs
    auto node = std::make_shared<rclcpp::Node>("ros_node_gui");

    // ROs must spin somewhere, spins on worker
    std::thread ros_spin([node]() {rclcpp::spin(node); });

    QApplication app(argc, argv);

    MainWindow window(node);
    window.show();

    int result = app.exec(); // blocks until the window closes

    rclcpp::shutdown(); // stop spinning so the worker thread exits
    ros_spin.join();
    return result;
}