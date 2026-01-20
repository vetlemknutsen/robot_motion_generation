#include <QApplication>
#include <rclcpp/rclcpp.hpp>
#include <thread>
#include <memory>

#include "my_qt_gui/main_window.hpp"


int main(int argc, char *argv[]){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("ros_node_gui");

    std::thread ros_spin([node]() {rclcpp::spin(node); });

    QApplication app(argc, argv);

    MainWindow window(node);
    window.show();

    int result = app.exec();

    rclcpp::shutdown();
    ros_spin.join();
    return result;
}