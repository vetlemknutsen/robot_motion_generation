#pragma once

#include <QMainWindow>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <QFileDialog>


namespace rclcpp {
    class Node;
}

namespace Ui {
    class MainWindow;
}

class MainWindow : public QMainWindow
{

public:
    MainWindow(std::shared_ptr<rclcpp::Node> node, QWidget *parent=nullptr);
    ~MainWindow();
private:
    std::shared_ptr<rclcpp::Node> node_;
    Ui::MainWindow *ui;

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr generate_pub_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr rml_sub_;

    void onBrowseClicked();
    void onGenerateClicked();
    void onRmlReceived(const std_msgs::msg::String::SharedPtr msg);
};
