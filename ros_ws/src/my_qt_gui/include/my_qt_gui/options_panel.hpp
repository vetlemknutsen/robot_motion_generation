#pragma once
#include <QWidget>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include <QLabel>
#include <QFileDialog>
#include <rclcpp/rclcpp.hpp>
#include <motion_pipeline_msgs/srv/generate_request.hpp>
#include <motion_pipeline_msgs/srv/switch_robot.hpp>

class OptionsPanel : public QWidget
{
    Q_OBJECT

public:
    OptionsPanel(std::shared_ptr<rclcpp::Node> node, QLineEdit* pathEdit, QComboBox* adapterBox, QComboBox* robotBox, QPushButton* generateButton, QPushButton* browseButton, QWidget* parent = nullptr);

    QString getCurrentRobot() const {
        return currentRobot_; 
    }

signals:
    void generateStarted(const QString& metadataText);
    void rmlGenerated(const QString& rml);
    void generateFailed(const QString& error);
    void logMessage(const QString& text);

private slots:
    void onGenerateClicked();
    void onBrowseClicked();
    void onRobotChanged(const QString& robot);

private:
    void setLoadingState(bool loading);

    std::shared_ptr<rclcpp::Node> node_;
    rclcpp::Client<motion_pipeline_msgs::srv::GenerateRequest>::SharedPtr generate_client_;
    rclcpp::Client<motion_pipeline_msgs::srv::SwitchRobot>::SharedPtr switch_robot_client_;

    QLineEdit* pathEdit_;
    QComboBox* adapterBox_;
    QComboBox* robotBox_;
    QPushButton* generateButton_;

    QString currentRobot_ = "tiago";
    bool robotLoading_ = false;
};
