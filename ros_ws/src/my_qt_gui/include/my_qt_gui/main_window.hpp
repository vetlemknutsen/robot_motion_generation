#pragma once

#include <QMainWindow>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <QFileDialog>
#include <QMovie>


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

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr send_pub_;

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr switch_robot_pub_; 
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr robot_ready_sub_; 
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr log_sub_; 

    QString current_robot_; 
    bool robot_loading_ = false; 

    void onBrowseClicked();
    void onGenerateClicked();
    void onSendClicked();
    void onRmlReceived(const std_msgs::msg::String::SharedPtr msg);

    void onRobotDropdownChanged(const QString& robot);
    void onRobotReady(const std_msgs::msg::String::SharedPtr msg);
    void setLoadingState(bool loading);

    void onLogReceived(const std_msgs::msg::String::SharedPtr msg);
};
