#pragma once

#include <QMainWindow>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <QFileDialog>
#include <QMovie>
#include <motion_pipeline_msgs/srv/generate_request.hpp>
#include <motion_pipeline_msgs/srv/switch_robot.hpp>
#include <motion_pipeline_msgs/msg/pipeline_log.hpp>


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

    rclcpp::Client<motion_pipeline_msgs::srv::GenerateRequest>::SharedPtr generate_client_;
    rclcpp::Client<motion_pipeline_msgs::srv::SwitchRobot>::SharedPtr switch_robot_client_;

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr send_pub_;
    rclcpp::Subscription<motion_pipeline_msgs::msg::PipelineLog>::SharedPtr log_sub_; 

    QString current_robot_; 
    bool robot_loading_ = false; 

    void onBrowseClicked();
    void onGenerateClicked();
    void onSendClicked();

    void onRobotDropdownChanged(const QString& robot);
    void setLoadingState(bool loading);

    void onLogReceived(const motion_pipeline_msgs::msg::PipelineLog::SharedPtr msg);
};
